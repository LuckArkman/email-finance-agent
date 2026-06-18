const {
  default: makeWASocket,
  useMultiFileAuthState,
  DisconnectReason,
  fetchLatestBaileysVersion,
  downloadMediaMessage,
} = require('@whiskeysockets/baileys');
const express = require('express');
const pino = require('pino');
const QRCode = require('qrcode');
const axios = require('axios');
const fs = require('fs');
const path = require('path');
const { EventEmitter } = require('events');
const FormData = require('form-data');

// ─────────────────────────────────────────────
// Config
// ─────────────────────────────────────────────
const PORT = process.env.PORT || 3001;
const BACKEND_URL = process.env.BACKEND_URL || 'http://backend:8000';
const AUTH_DIR = process.env.AUTH_DIR || './auth_sessions';
const UPLOAD_DIR = process.env.UPLOAD_DIR || '/tmp/uploads';

[AUTH_DIR, UPLOAD_DIR].forEach((d) => fs.mkdirSync(d, { recursive: true }));

// ─────────────────────────────────────────────
// State
// ─────────────────────────────────────────────
const state = {
  /** Current QR code as data-URI (base64 PNG) */
  qrDataUrl: null,
  /** 'connecting' | 'qr' | 'connected' | 'disconnected' */
  status: 'disconnected',
  /** Baileys socket instance */
  sock: null,
};

const emitter = new EventEmitter();

// ─────────────────────────────────────────────
// Baileys connection
// ─────────────────────────────────────────────
async function startWhatsApp() {
  const logger = pino({ level: 'silent' });
  const { state: authState, saveCreds } = await useMultiFileAuthState(AUTH_DIR);
  const { version } = await fetchLatestBaileysVersion();

  const sock = makeWASocket({
    version,
    logger,
    auth: authState,
    printQRInTerminal: false,
    browser: ['Finance Agent', 'Chrome', '120.0'],
  });

  state.sock = sock;
  state.status = 'connecting';

  // ── QR code ──
  sock.ev.on('connection.update', async (update) => {
    const { connection, lastDisconnect, qr } = update;

    if (qr) {
      state.qrDataUrl = await QRCode.toDataURL(qr);
      state.status = 'qr';
      emitter.emit('qr', state.qrDataUrl);
      console.log('[baileys] QR code generated — waiting for scan.');
    }

    if (connection === 'open') {
      state.status = 'connected';
      state.qrDataUrl = null;
      emitter.emit('connected');
      console.log('[baileys] WhatsApp connected ✓');
    }

    if (connection === 'close') {
      const code = lastDisconnect?.error?.output?.statusCode;
      const isLoggedOut = code === DisconnectReason.loggedOut;
      state.status = 'disconnected';
      console.log(`[baileys] Connection closed (code=${code}). isLoggedOut=${isLoggedOut}`);
      
      if (isLoggedOut) {
        console.log('[baileys] Logged out from WhatsApp. Clearing session and restarting...');
        try {
          fs.rmSync(AUTH_DIR, { recursive: true, force: true });
          fs.mkdirSync(AUTH_DIR, { recursive: true });
        } catch (err) {}
        setTimeout(startWhatsApp, 2000);
      } else {
        setTimeout(startWhatsApp, 3000);
      }
    }
  });

  sock.ev.on('creds.update', saveCreds);

  // ── Incoming messages ──
  sock.ev.on('messages.upsert', async ({ messages, type }) => {
    if (type !== 'notify') return;

    for (const msg of messages) {
      if (msg.key.fromMe) continue;

      const msgType = Object.keys(msg.message || {})[0];
      const isMedia = ['imageMessage', 'documentMessage', 'documentWithCaptionMessage'].includes(msgType);
      const isText = ['conversation', 'extendedTextMessage'].includes(msgType);
      const isAudio = msgType === 'audioMessage';

      if (!isMedia && !isText && !isAudio) continue;

      const sender = msg.key.remoteJid?.split('@')[0] ?? 'unknown';

      if (isText) {
        const text = msg.message.conversation || msg.message.extendedTextMessage?.text || '';
        console.log(`[baileys] Text message received from ${sender}: ${text}`);
        try {
          await axios.post(`${BACKEND_URL}/api/hermes/whatsapp/message`, {
            sender_phone: sender,
            text: text
          });
        } catch (err) {
          console.error('[baileys] Error forwarding text message:', err.message);
        }
        continue;
      }

      if (isAudio) {
        console.log(`[baileys] Audio message received from ${sender}`);
        try {
          const buffer = await downloadMediaMessage(msg, 'buffer', {}, { logger });
          const filename = `wa_${Date.now()}_${sender}.ogg`;
          const filePath = path.join(UPLOAD_DIR, filename);
          fs.writeFileSync(filePath, buffer);

          const form = new FormData();
          form.append('file', fs.createReadStream(filePath), filename);
          form.append('sender_phone', sender);

          await axios.post(`${BACKEND_URL}/api/hermes/whatsapp/audio`, form, {
            headers: form.getHeaders(),
            maxBodyLength: Infinity,
            maxContentLength: Infinity
          });
          console.log(`[baileys] Forwarded audio to Gateway for STT`);
        } catch (err) {
          console.error('[baileys] Error processing incoming audio:', err.message);
        }
        continue;
      }

      console.log(`[baileys] Media message received from ${sender} — type: ${msgType}`);

      try {
        // Download media from WhatsApp servers
        const buffer = await downloadMediaMessage(msg, 'buffer', {}, { logger });

        const ext = msgType === 'imageMessage' ? 'jpg' : 'pdf';
        const filename = `wa_${Date.now()}_${sender}.${ext}`;
        const filePath = path.join(UPLOAD_DIR, filename);

        fs.writeFileSync(filePath, buffer);
        console.log(`[baileys] Saved media to ${filePath}`);

        // Send to Gateway using form-data
        const form = new FormData();
        form.append('file', fs.createReadStream(filePath), filename);
        form.append('source', 'whatsapp');
        form.append('sender', sender);

        await axios.post(`${BACKEND_URL}/api/hermes/documents/upload`, form, {
          headers: form.getHeaders(),
          maxBodyLength: Infinity,
          maxContentLength: Infinity
        });

        console.log(`[baileys] Uploaded ${filename} to Gateway`);
      } catch (err) {
        console.error('[baileys] Error processing media:', err.message);
      }
    }
  });
}

// ─────────────────────────────────────────────
// Express REST API (consumed by Python backend)
// ─────────────────────────────────────────────
const cors = require('cors');
const app = express();
app.use(cors());
app.use(express.json());

/** GET /status — returns current connection state */
app.get('/status', (_req, res) => {
  res.json({ status: state.status });
});

/** GET /qr — returns QR code as base64 data-URI */
app.get('/qr', (_req, res) => {
  if (!state.qrDataUrl) {
    return res.status(404).json({ error: 'No QR code available', status: state.status });
  }
  res.json({ qr: state.qrDataUrl, status: state.status });
});

/** POST /disconnect — logs out and deletes auth files */
app.post('/disconnect', async (_req, res) => {
  try {
    if (state.sock) {
      await state.sock.logout();
    }
    // Remove persisted session so next start shows QR again
    fs.rmSync(AUTH_DIR, { recursive: true, force: true });
    fs.mkdirSync(AUTH_DIR, { recursive: true });
    state.status = 'disconnected';
    state.qrDataUrl = null;
    res.json({ status: 'disconnected' });
    // Restart to pick up fresh auth
    setTimeout(startWhatsApp, 1500);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

/** POST /send — sends a text or audio message to a WhatsApp user */
app.post('/send', async (req, res) => {
  try {
    const { to, text, audioBase64, isPTT } = req.body;
    if (!state.sock || state.status !== 'connected') {
      return res.status(503).json({ error: 'WhatsApp not connected' });
    }
    const jid = `${to}@s.whatsapp.net`;
    
    if (audioBase64) {
      const buffer = Buffer.from(audioBase64, 'base64');
      await state.sock.sendMessage(jid, { audio: buffer, ptt: !!isPTT });
      console.log(`[baileys] Audio message (PTT) sent to ${to}`);
    } else {
      await state.sock.sendMessage(jid, { text });
      console.log(`[baileys] Text message sent to ${to}`);
    }
    
    res.json({ success: true });
  } catch (err) {
    console.error('[baileys] Error sending message:', err.message);
    res.status(500).json({ error: err.message });
  }
});

/** Health check */
app.get('/health', (_req, res) => res.json({ ok: true }));

app.listen(PORT, () => {
  console.log(`[baileys-bridge] HTTP API listening on :${PORT}`);
  startWhatsApp();
});

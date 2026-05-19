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
      const shouldReconnect = code !== DisconnectReason.loggedOut;
      state.status = 'disconnected';
      console.log(`[baileys] Connection closed (code=${code}). Reconnect=${shouldReconnect}`);
      if (shouldReconnect) {
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

      if (!isMedia) continue;

      const sender = msg.key.remoteJid?.split('@')[0] ?? 'unknown';
      console.log(`[baileys] Media message received from ${sender} — type: ${msgType}`);

      try {
        // Download media from WhatsApp servers
        const buffer = await downloadMediaMessage(msg, 'buffer', {}, { logger });

        const ext = msgType === 'imageMessage' ? 'jpg' : 'pdf';
        const filename = `wa_${Date.now()}_${sender}.${ext}`;
        const filePath = path.join(UPLOAD_DIR, filename);

        fs.writeFileSync(filePath, buffer);
        console.log(`[baileys] Saved media to ${filePath}`);

        // Notify Python backend
        await axios.post(`${BACKEND_URL}/api/v1/whatsapp/baileys/media`, {
          file_path: filePath,
          sender_phone: sender,
          message_id: msg.key.id,
          media_type: msgType === 'imageMessage' ? 'image' : 'document',
        });

        console.log(`[baileys] Notified backend for ${filename}`);
      } catch (err) {
        console.error('[baileys] Error processing media:', err.message);
      }
    }
  });
}

// ─────────────────────────────────────────────
// Express REST API (consumed by Python backend)
// ─────────────────────────────────────────────
const app = express();
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

/** Health check */
app.get('/health', (_req, res) => res.json({ ok: true }));

app.listen(PORT, () => {
  console.log(`[baileys-bridge] HTTP API listening on :${PORT}`);
  startWhatsApp();
});

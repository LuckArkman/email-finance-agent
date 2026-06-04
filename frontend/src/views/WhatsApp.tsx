import React, { useState, useEffect, useRef } from 'react';
import {
  MessageCircle,
  Smartphone,
  QrCode,
  CheckCircle2,
  RefreshCw,
  Lock,
  Terminal,
  Image,
  Zap,
  Info,
} from 'lucide-react';
import LayoutBase from '../components/LayoutBase';
import api from '../services/api';

import QRCode from 'react-qr-code';

type WaStatus = 'disconnected' | 'connecting' | 'qr' | 'connected';

const WhatsAppView: React.FC = () => {
  const [status, setStatus] = useState<WaStatus>('disconnected');
  const [qrCode, setQrCode] = useState<string | null>(null);
  const [polling, setPolling] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Check status on mount
  useEffect(() => {
    checkStatus();
    return () => { if (intervalRef.current) clearInterval(intervalRef.current); };
  }, []);

  const checkStatus = async () => {
    try {
      const res = await api.get('/whatsapp/status');
      setStatus(res.data.status ?? 'disconnected');
    } catch {
      setStatus('disconnected');
    }
  };

  const startQrPolling = async () => {
    setPolling(true);
    setStatus('connecting');
    setQrCode(null);

    if (intervalRef.current) clearInterval(intervalRef.current);

    const iv = setInterval(async () => {
      try {
        const res = await api.get('/whatsapp/qr');
        if (res.data.qr) setQrCode(res.data.qr);
        if (res.data.status) setStatus(res.data.status);
        if (res.data.status === 'connected') {
          clearInterval(iv);
          setPolling(false);
          setQrCode(null);
        }
      } catch { /* keep polling */ }
    }, 2000);

    intervalRef.current = iv;
  };

  const stopPolling = () => {
    if (intervalRef.current) clearInterval(intervalRef.current);
    setPolling(false);
    setStatus('disconnected');
    setQrCode(null);
  };

  const handleDisconnect = async () => {
    try { await api.post('/whatsapp/disconnect'); } catch { /* ignore */ }
    stopPolling();
  };

  const statusColors: Record<string, string> = {
    connected:    'text-green-400  bg-green-500/10  border-green-500/20',
    qr:           'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
    connecting:   'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
    waiting:      'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
    disconnected: 'text-red-400    bg-red-500/10    border-red-500/20',
  };

  const statusLabel: Record<string, string> = {
    connected:    '● Conectado',
    qr:           '⟳ A aguardar scan...',
    connecting:   '⟳ A ligar...',
    waiting:      '⟳ A aguardar QR Code...',
    disconnected: '✕ Desconectado',
  };

  return (
    <LayoutBase>
      <div className="space-y-8 animate-fade-in max-w-3xl mx-auto">

        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold tracking-tight text-white flex items-center gap-3">
              <MessageCircle className="text-green-500" />
              WhatsApp
            </h2>
            <p className="text-gray-400 mt-1">Envie fotos de faturas diretamente pelo WhatsApp.</p>
          </div>
          <div className={`flex items-center gap-2 text-xs font-bold px-4 py-2 rounded-full border ${statusColors[status]}`}>
            {(status === 'connecting' || status === 'qr') && (
              <RefreshCw size={12} className="animate-spin" />
            )}
            {statusLabel[status]}
          </div>
        </div>

        {/* How it works */}
        <div className="glass p-6 rounded-[28px] border border-white/5 space-y-4">
          <h3 className="text-sm font-bold text-gray-300 uppercase tracking-widest flex items-center gap-2">
            <Info size={14} className="text-blue-400" /> Como funciona
          </h3>
          <div className="grid grid-cols-3 gap-4">
            {[
              { icon: <Image size={20} className="text-green-500" />, title: 'Enviar foto', desc: 'Fotografe a fatura e envie para o número WhatsApp do agente' },
              { icon: <Zap size={20} className="text-yellow-500" />,  title: 'Extração IA', desc: 'O Hermes Agent analisa com OCR + visão artificial em segundos' },
              { icon: <CheckCircle2 size={20} className="text-blue-500" />, title: 'Dashboard', desc: 'A fatura aparece automaticamente no dashboard com todos os dados' },
            ].map((step) => (
              <div key={step.title} className="p-4 rounded-2xl bg-white/3 border border-white/5 space-y-3">
                <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center">
                  {step.icon}
                </div>
                <p className="font-bold text-white text-sm">{step.title}</p>
                <p className="text-xs text-gray-500 leading-relaxed">{step.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Connection Card */}
        <div className="glass p-8 rounded-[32px] border border-white/5 shadow-2xl space-y-6">
          <div className="flex items-center gap-4">
            <div className={`p-4 rounded-full ${status === 'connected' ? 'bg-green-500/10 text-green-500' : 'bg-gray-800 text-gray-500'}`}>
              <Smartphone size={28} />
            </div>
            <div>
              <h3 className="text-xl font-bold text-white">
                {status === 'connected' ? 'Bridge Activa' : 'Bridge Desconectada'}
              </h3>
              <p className="text-sm text-gray-500 mt-0.5">
                {status === 'connected'
                  ? 'O Hermes Agent está a monitorizar o WhatsApp. Envie uma foto de fatura para testar.'
                  : 'Faça o pairing para activar a bridge Baileys.'}
              </p>
            </div>
          </div>

          {/* Terminal instructions */}
          <div className="flex items-start gap-3 p-4 bg-amber-500/5 border border-amber-500/20 rounded-2xl">
            <Terminal size={16} className="text-amber-400 mt-0.5 flex-shrink-0" />
            <div className="space-y-2 w-full">
              <p className="text-xs font-bold text-amber-300">Pairing via terminal (necessário apenas uma vez)</p>
              <div className="bg-black/40 rounded-xl px-4 py-3 font-mono text-xs text-green-400 border border-white/5">
                docker exec -it hermes_agent hermes whatsapp
              </div>
              <p className="text-xs text-gray-500">
                Após correr este comando, o QR Code aparece no terminal. Depois clique em <strong className="text-amber-300">Ver QR Ao Vivo</strong> para verificar se o agent já expõe o QR na API.
              </p>
            </div>
          </div>

          {/* QR Code display (Moved to Modal) */}

          {/* Action buttons */}
          <div className="flex gap-3 pt-2">
            {status === 'connected' ? (
              <button
                onClick={handleDisconnect}
                className="px-6 py-3 bg-red-500/10 text-red-400 hover:bg-red-500/20 font-bold rounded-2xl transition-all text-sm border border-red-500/20"
              >
                Desconectar
              </button>
            ) : (
              <>
                <button
                  onClick={checkStatus}
                  className="px-5 py-3 bg-white/5 text-gray-400 hover:bg-white/10 font-bold rounded-2xl transition-all flex items-center gap-2 text-sm border border-white/5"
                >
                  <RefreshCw size={16} /> Verificar Estado
                </button>
                {!polling ? (
                  <button
                    onClick={startQrPolling}
                    className="flex-1 py-3 bg-green-500 text-black hover:bg-green-400 font-bold rounded-2xl transition-all flex items-center justify-center gap-2 text-sm shadow-xl shadow-green-500/20"
                  >
                    <QrCode size={18} /> Ver QR Ao Vivo
                  </button>
                ) : (
                  <button
                    onClick={stopPolling}
                    className="flex-1 py-3 bg-white/5 text-gray-400 hover:bg-white/10 font-bold rounded-2xl transition-all flex items-center justify-center gap-2 text-sm border border-white/5"
                  >
                    <RefreshCw size={16} className="animate-spin" /> A verificar... (Cancelar)
                  </button>
                )}
              </>
            )}
          </div>
        </div>

        {/* Security note */}
        <div className="flex items-start gap-3 p-4 bg-white/3 border border-white/5 rounded-2xl">
          <Lock size={14} className="text-gray-500 mt-0.5 flex-shrink-0" />
          <p className="text-xs text-gray-500 leading-relaxed">
            A bridge usa <strong className="text-gray-300">Baileys</strong> — não requer WhatsApp Business API nem conta Meta.
            A sessão é guardada em <code className="text-blue-400 text-[10px] bg-blue-500/10 px-1.5 py-0.5 rounded">~/.hermes/platforms/whatsapp/session</code> no volume persistente Docker.
            Use um número dedicado para o bot.
          </p>
        </div>

      </div>

      {/* Modal View QR Code */}
      {polling && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-md z-50 flex items-center justify-center p-4">
           <div className="bg-[#121212] w-full max-w-md rounded-[32px] overflow-hidden shadow-2xl border border-white/10 flex flex-col p-8 items-center text-center space-y-6">
              <div className="w-16 h-16 rounded-full bg-green-500/10 text-green-500 flex items-center justify-center mb-2">
                 <QrCode size={32} />
              </div>
              
              <h3 className="text-2xl font-bold text-white">
                {qrCode ? 'Escanear QR Code' : 'A gerar QR Code...'}
              </h3>
              
              {qrCode ? (
                <div className="bg-white p-4 rounded-2xl">
                  {qrCode.startsWith('http') || qrCode.startsWith('data:image') ? (
                    <img src={qrCode} alt="WhatsApp QR Code" className="w-64 h-64 object-contain" />
                  ) : (
                    <QRCode value={qrCode} size={256} className="w-64 h-64" />
                  )}
                </div>
              ) : (
                <div className="w-64 h-64 flex flex-col items-center justify-center bg-white/5 rounded-2xl border border-white/10">
                  <RefreshCw size={32} className="animate-spin text-green-500 mb-4" />
                  <p className="text-sm text-gray-400">Aguardando Hermes Agent...</p>
                </div>
              )}

              <p className="text-xs text-gray-500 font-medium max-w-[250px]">
                Abra o WhatsApp → Definições → Dispositivos Associados → Associar Dispositivo
              </p>

              <button 
                onClick={stopPolling}
                className="w-full px-6 py-4 bg-white/5 text-gray-300 hover:bg-white/10 hover:text-white font-bold rounded-2xl transition-all border border-white/10 mt-4"
              >
                Cancelar
              </button>
           </div>
        </div>
      )}
    </LayoutBase>
  );
};

export default WhatsAppView;

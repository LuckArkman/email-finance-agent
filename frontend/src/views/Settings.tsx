import React, { useState, useEffect } from 'react';
import { 
  Settings as SettingsIcon, 
  Webhook, 
  ShieldCheck, 
  Save, 
  ExternalLink,
  CheckCircle2,
  Lock,
  Zap,
  RefreshCw,
  MessageCircle,
  QrCode,
  X,
  Smartphone,
  Percent,
  Building2,
  Globe,
  Euro
} from 'lucide-react';
import api from '../services/api';
import LayoutBase from '../components/LayoutBase';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

const SettingsView: React.FC = () => {
  const [webhookUrl, setWebhookUrl] = useState('');
  const [secretKey, setSecretKey] = useState('');
  const [isActive, setIsActive] = useState(true);
  const [loading, setLoading] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  // Fiscal Settings
  const [ivaRate, setIvaRate] = useState(0.23);
  const [currency, setCurrency] = useState('EUR');
  const [fiscalName, setFiscalName] = useState('');
  const [fiscalCountry, setFiscalCountry] = useState('PT');
  const [fiscalLoading, setFiscalLoading] = useState(false);

  // WhatsApp States
  const [waStatus, setWaStatus] = useState<'disconnected' | 'connecting' | 'qr' | 'connected'>('disconnected');
  const [qrCodeData, setQrCodeData] = useState<string | null>(null);
  const [showQrModal, setShowQrModal] = useState(false);
  const [pollingInterval, setPollingInterval] = useState<any>(null);

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        const [webhookRes, fiscalRes] = await Promise.all([
          api.get('/settings/webhooks'),
          api.get('/settings/fiscal'),
        ]);
        if (webhookRes.data) {
          setWebhookUrl(webhookRes.data.target_url || '');
          setSecretKey(webhookRes.data.secret_key || '');
          setIsActive(webhookRes.data.is_active ?? true);
        }
        if (fiscalRes.data) {
          setIvaRate(fiscalRes.data.iva_rate ?? 0.23);
          setCurrency(fiscalRes.data.currency ?? 'EUR');
          setFiscalName(fiscalRes.data.fiscal_name ?? '');
          setFiscalCountry(fiscalRes.data.fiscal_country ?? 'PT');
        }
      } catch (err) {
        console.error('Failed to load settings', err);
      }
    };
    fetchSettings();
    checkWhatsAppStatus();
  }, []);

  const checkWhatsAppStatus = async () => {
    try {
      // Baileys bridge is running on port 3001, but in production it should be proxied
      // For local dev, we hit localhost:3001
      const res = await axios.get('http://localhost:3001/status');
      setWaStatus(res.data.status);
    } catch (err) {
      console.log('Baileys bridge not reachable', err);
      setWaStatus('disconnected');
    }
  };

  const handleConnectWhatsApp = () => {
    setShowQrModal(true);
    pollForQr();
  };

  const handleDisconnectWhatsApp = async () => {
    try {
      await axios.post('http://localhost:3001/disconnect');
      setWaStatus('disconnected');
      setQrCodeData(null);
    } catch (err) {
      console.error('Failed to disconnect', err);
    }
  };

  const pollForQr = () => {
    if (pollingInterval) clearInterval(pollingInterval);
    
    const interval = setInterval(async () => {
      try {
        const res = await axios.get('http://localhost:3001/qr');
        setWaStatus(res.data.status);
        if (res.data.qr) {
          setQrCodeData(res.data.qr);
        }
        if (res.data.status === 'connected') {
          clearInterval(interval);
          setShowQrModal(false);
          setShowSuccess(true);
          setTimeout(() => setShowSuccess(false), 3000);
        }
      } catch (err) {
        // Wait or handle error silently while polling
      }
    }, 2000);
    setPollingInterval(interval);
  };

  useEffect(() => {
    return () => {
      if (pollingInterval) clearInterval(pollingInterval);
    };
  }, [pollingInterval]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post('/settings/webhooks', {
        target_url: webhookUrl,
        secret_key: secretKey,
        is_active: isActive
      });
      setShowSuccess(true);
      setTimeout(() => setShowSuccess(false), 3000);
    } catch (err) {
      console.error('Save failed', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveFiscal = async (e: React.FormEvent) => {
    e.preventDefault();
    setFiscalLoading(true);
    try {
      await api.post('/settings/fiscal', {
        iva_rate: ivaRate,
        currency,
        fiscal_name: fiscalName || null,
        fiscal_country: fiscalCountry,
      });
      setShowSuccess(true);
      setTimeout(() => setShowSuccess(false), 3000);
    } catch (err) {
      console.error('Fiscal save failed', err);
    } finally {
      setFiscalLoading(false);
    }
  };

  return (
    <LayoutBase>
      <div className="space-y-8 animate-fade-in max-w-4xl mx-auto">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-white flex items-center gap-3">
            <SettingsIcon className="text-blue-500" />
            System Settings
          </h2>
          <p className="text-gray-400 mt-1">Configure integrations and security preferences.</p>
        </div>

        <div className="grid grid-cols-1 gap-8">
          {/* Fiscal / IVA Settings Section */}
          <div className="glass p-8 rounded-[32px] border border-white/5 shadow-2xl space-y-8">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-blue-600/10 flex items-center justify-center text-blue-400">
                  <Euro size={20} />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">Configurações Fiscais</h3>
                  <p className="text-sm text-gray-500">Defina a taxa de IVA e moeda aplicados nas faturas processadas.</p>
                </div>
              </div>
              <div className="flex items-center gap-2 text-xs font-bold text-gray-500 bg-white/5 px-4 py-2 rounded-full border border-white/5">
                <Percent size={14} className="text-blue-400" />
                FISCALIDADE PT
              </div>
            </div>

            <form onSubmit={handleSaveFiscal} className="space-y-6">
              {/* IVA Rate */}
              <div className="space-y-3">
                <label className="text-xs font-bold text-gray-400 uppercase tracking-widest ml-1">Taxa de IVA</label>
                {/* Quick select buttons */}
                <div className="flex gap-3">
                  {[{label: '6%', value: 0.06}, {label: '13%', value: 0.13}, {label: '23%', value: 0.23}].map(opt => (
                    <button
                      key={opt.label}
                      type="button"
                      onClick={() => setIvaRate(opt.value)}
                      className={`px-5 py-3 rounded-2xl text-sm font-bold border transition-all ${
                        Math.abs(ivaRate - opt.value) < 0.001
                          ? 'bg-blue-600 text-white border-blue-500 shadow-lg shadow-blue-500/20'
                          : 'bg-white/5 text-gray-400 border-white/10 hover:border-blue-500/30 hover:text-white'
                      }`}
                    >
                      {opt.label}
                    </button>
                  ))}
                  <div className="flex-1 relative">
                    <Percent className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" size={14} />
                    <input
                      type="number"
                      min={0}
                      max={100}
                      step={0.1}
                      value={(ivaRate * 100).toFixed(1)}
                      onChange={e => setIvaRate(parseFloat(e.target.value) / 100)}
                      className="w-full pl-9 pr-4 py-3 bg-[#0d1117] border border-white/10 rounded-2xl text-sm text-white outline-none focus:border-blue-500/50 transition-all"
                      placeholder="23.0"
                    />
                  </div>
                </div>
                <p className="text-[10px] text-gray-500 ml-1">
                  Taxa actualmente configurada: <span className="text-blue-400 font-bold">{(ivaRate * 100).toFixed(1)}%</span>
                  {' '}— Esta taxa será usada pelo modelo Llama como fallback quando o IVA não estiver explícito no documento.
                </p>
              </div>

              {/* Fiscal Name */}
              <div className="space-y-2">
                <label className="text-xs font-bold text-gray-400 uppercase tracking-widest ml-1">Nome Fiscal / NIF da Empresa</label>
                <div className="relative">
                  <Building2 className="absolute left-5 top-1/2 -translate-y-1/2 text-gray-600" size={16} />
                  <input
                    type="text"
                    placeholder="Ex: Sustentacódigo, Lda. — NIF 123456789"
                    value={fiscalName}
                    onChange={e => setFiscalName(e.target.value)}
                    className="w-full pl-12 pr-5 py-4 bg-[#0d1117] border border-white/10 rounded-2xl text-sm text-white outline-none focus:border-blue-500/50 transition-all"
                  />
                </div>
              </div>

              {/* Currency + Country */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-xs font-bold text-gray-400 uppercase tracking-widest ml-1">Moeda</label>
                  <select
                    value={currency}
                    onChange={e => setCurrency(e.target.value)}
                    className="w-full px-5 py-4 bg-[#0d1117] border border-white/10 rounded-2xl text-sm text-white outline-none focus:border-blue-500/50 transition-all"
                  >
                    <option value="EUR">€ Euro (EUR)</option>
                    <option value="GBP">£ Libra (GBP)</option>
                    <option value="CHF">CHF Franco Suíço</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-xs font-bold text-gray-400 uppercase tracking-widest ml-1">País Fiscal</label>
                  <div className="relative">
                    <Globe className="absolute left-5 top-1/2 -translate-y-1/2 text-gray-600" size={16} />
                    <input
                      type="text"
                      maxLength={2}
                      placeholder="PT"
                      value={fiscalCountry}
                      onChange={e => setFiscalCountry(e.target.value.toUpperCase())}
                      className="w-full pl-12 pr-5 py-4 bg-[#0d1117] border border-white/10 rounded-2xl text-sm text-white outline-none focus:border-blue-500/50 transition-all font-mono uppercase"
                    />
                  </div>
                </div>
              </div>

              <div className="pt-2">
                <button
                  disabled={fiscalLoading}
                  className="w-full py-4 bg-blue-600 text-white font-bold rounded-2xl hover:bg-blue-500 transition-all flex items-center justify-center gap-2 h-14 shadow-lg shadow-blue-500/20"
                >
                  {fiscalLoading ? (
                    <RefreshCw className="animate-spin" size={20} />
                  ) : (
                    <>
                      <Save size={20} />
                      Guardar Configurações Fiscais
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>

          {/* Outbound Webhooks Section */}
          <div className="glass p-8 rounded-[32px] border border-white/5 shadow-2xl space-y-8">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-purple-600/10 flex items-center justify-center text-purple-500">
                  <Webhook size={20} />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">Outbound Webhooks</h3>
                  <p className="text-sm text-gray-500">Connect to Zapier, Make.com or PowerAutomate.</p>
                </div>
              </div>
              <div className="flex items-center gap-2 text-xs font-bold text-gray-500 bg-white/5 px-4 py-2 rounded-full border border-white/5">
                <Zap size={14} className="text-yellow-500" />
                WEBHOOK SDK V1.0
              </div>
            </div>

            <form onSubmit={handleSave} className="space-y-6">
              <div className="space-y-2">
                <div className="flex items-center justify-between ml-1">
                  <label className="text-xs font-bold text-gray-400 uppercase tracking-widest">Payload Target URL</label>
                  <a href="https://zapier.com/apps/webhook/integrations" target="_blank" rel="noopener noreferrer" className="text-[10px] text-blue-500 hover:underline flex items-center gap-1">
                    Docs <ExternalLink size={10} />
                  </a>
                </div>
                <input 
                  type="url" 
                  placeholder="https://hooks.zapier.com/..."
                  value={webhookUrl}
                  onChange={(e) => setWebhookUrl(e.target.value)}
                  className="w-full px-5 py-4 bg-[#0d1117] border border-white/10 rounded-2xl text-sm text-white outline-none focus:border-purple-500/50 transition-all"
                />
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold text-gray-400 uppercase tracking-widest ml-1">Signing Secret (HMAC)</label>
                <div className="relative">
                  <Lock className="absolute left-5 top-1/2 -translate-y-1/2 text-gray-600" size={16} />
                  <input 
                    type="password" 
                    placeholder="Enter secret for signature validation"
                    value={secretKey}
                    onChange={(e) => setSecretKey(e.target.value)}
                    className="w-full pl-12 pr-5 py-4 bg-[#0d1117] border border-white/10 rounded-2xl text-sm text-white outline-none focus:border-purple-500/50 transition-all font-mono"
                  />
                </div>
                <p className="text-[10px] text-gray-500 ml-1">All payloads will be signed with this key in the <code className="text-purple-400">X-LuckArkman-Signature</code> header.</p>
              </div>

              <div className="flex items-center justify-between p-4 rounded-2xl bg-white/5 border border-white/5">
                <div className="flex items-center gap-3">
                  <ShieldCheck className="text-green-500" size={20} />
                  <div>
                    <p className="text-sm font-bold text-white">Enable Automated Triggers</p>
                    <p className="text-xs text-gray-500">Fire webhook on successful invoice processing.</p>
                  </div>
                </div>
                <button 
                  type="button"
                  onClick={() => setIsActive(!isActive)}
                  className={`w-12 h-6 rounded-full transition-colors relative ${isActive ? 'bg-purple-600' : 'bg-gray-700'}`}
                >
                  <div className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-all ${isActive ? 'right-1' : 'left-1'}`} />
                </button>
              </div>

              <div className="pt-4">
                <button 
                  disabled={loading}
                  className="w-full py-4 bg-white text-black font-bold rounded-2xl hover:bg-gray-200 transition-all flex items-center justify-center gap-2 h-14"
                >
                  {loading ? (
                    <RefreshCw className="animate-spin" size={20} />
                  ) : (
                    <>
                      <Save size={20} />
                      Save Integration Settings
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>

          {/* WhatsApp Baileys Integration Section */}
          <div className="glass p-8 rounded-[32px] border border-white/5 shadow-2xl space-y-8">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-green-600/10 flex items-center justify-center text-green-500">
                  <MessageCircle size={20} />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">Integração WhatsApp</h3>
                  <p className="text-sm text-gray-500">Conecte sua conta via QR Code (Baileys) para receber faturas.</p>
                </div>
              </div>
              <div className="flex items-center gap-2 text-xs font-bold px-4 py-2 rounded-full border border-white/5 bg-white/5">
                {waStatus === 'connected' ? (
                  <span className="text-green-500 flex items-center gap-2"><CheckCircle2 size={14} /> Conectado</span>
                ) : waStatus === 'connecting' || waStatus === 'qr' ? (
                  <span className="text-yellow-500 flex items-center gap-2"><RefreshCw size={14} className="animate-spin" /> Conectando...</span>
                ) : (
                  <span className="text-red-500 flex items-center gap-2"><Lock size={14} /> Desconectado</span>
                )}
              </div>
            </div>

            <div className="p-6 rounded-2xl bg-[#0d1117] border border-white/5 flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className={`p-4 rounded-full ${waStatus === 'connected' ? 'bg-green-500/10 text-green-500' : 'bg-gray-800 text-gray-500'}`}>
                  <Smartphone size={24} />
                </div>
                <div>
                  <h4 className="text-white font-bold">{waStatus === 'connected' ? 'WhatsApp Ativo' : 'WhatsApp Desconectado'}</h4>
                  <p className="text-xs text-gray-500 mt-1">
                    {waStatus === 'connected' 
                      ? 'O agente está a escutar imagens de faturas.' 
                      : 'Ligue o telemóvel para ativar a extração OCR via WhatsApp.'}
                  </p>
                </div>
              </div>

              {waStatus === 'connected' ? (
                <button 
                  onClick={handleDisconnectWhatsApp}
                  className="px-6 py-3 bg-red-500/10 text-red-500 hover:bg-red-500/20 font-bold rounded-xl transition-all text-sm"
                >
                  Desconectar
                </button>
              ) : (
                <button 
                  onClick={handleConnectWhatsApp}
                  className="px-6 py-3 bg-green-500 text-black hover:bg-green-400 font-bold rounded-xl transition-all flex items-center gap-2 text-sm"
                >
                  <QrCode size={18} />
                  Conectar Aparelho
                </button>
              )}
            </div>
          </div>
        </div>

        {/* QR Code Modal Overlay */}
        <AnimatePresence>
          {showQrModal && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4"
            >
              <motion.div 
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                className="bg-[#1a1f2e] p-8 rounded-[40px] border border-white/10 max-w-sm w-full relative flex flex-col items-center shadow-2xl"
              >
                <button 
                  onClick={() => {
                    setShowQrModal(false);
                    if (pollingInterval) clearInterval(pollingInterval);
                  }}
                  className="absolute top-6 right-6 text-gray-400 hover:text-white transition-colors"
                >
                  <X size={24} />
                </button>

                <div className="w-16 h-16 bg-green-500/10 text-green-500 rounded-full flex items-center justify-center mb-6">
                  <MessageCircle size={32} />
                </div>

                <h3 className="text-2xl font-black text-white text-center mb-2">Conectar WhatsApp</h3>
                <p className="text-sm text-gray-400 text-center mb-8">
                  Abra o WhatsApp no telemóvel &gt; Dispositivos Associados &gt; Associar Dispositivo e escaneie o código abaixo.
                </p>

                <div className="bg-white p-4 rounded-3xl w-64 h-64 flex items-center justify-center relative overflow-hidden">
                  {qrCodeData ? (
                    <img src={qrCodeData} alt="WhatsApp QR Code" className="w-full h-full object-contain" />
                  ) : (
                    <div className="flex flex-col items-center justify-center space-y-4 text-gray-400">
                      <RefreshCw className="animate-spin" size={32} />
                      <span className="text-xs font-bold uppercase tracking-widest">A gerar código...</span>
                    </div>
                  )}
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {showSuccess && (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              className="fixed bottom-12 right-12 bg-green-600 text-white px-8 py-4 rounded-3xl shadow-2xl flex items-center gap-3 font-bold z-50 border border-green-400/20"
            >
               <CheckCircle2 size={24} />
               <span>Settings Updated Successfully!</span>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </LayoutBase>
  );
};

export default SettingsView;

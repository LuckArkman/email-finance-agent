import React, { useState } from 'react';
import {
  Mail,
  ShieldCheck,
  Lock,
  MessageSquare,
  CheckCircle2,
  Loader2,
  Server,
  KeyRound,
  Globe,
  Eye,
  EyeOff,
  RefreshCw,
  Info,
} from 'lucide-react';
import LayoutBase from '../components/LayoutBase';
import api from '../services/api';

// IMAP/SMTP defaults per provider
const PROVIDER_DEFAULTS: Record<string, { imapHost: string; smtpHost: string }> = {
  gmail:    { imapHost: 'imap.gmail.com',             smtpHost: 'smtp.gmail.com' },
  outlook:  { imapHost: 'outlook.office365.com',      smtpHost: 'smtp.office365.com' },
  yahoo:    { imapHost: 'imap.mail.yahoo.com',         smtpHost: 'smtp.mail.yahoo.com' },
  fastmail: { imapHost: 'imap.fastmail.com',           smtpHost: 'smtp.fastmail.com' },
  other:    { imapHost: '',                            smtpHost: '' },
};

const providers = [
  { id: 'gmail',    name: 'Gmail / Google Workspace', icon: 'https://cdn-icons-png.flaticon.com/512/2991/2991148.png' },
  { id: 'outlook',  name: 'Outlook / Microsoft 365',  icon: 'https://cdn-icons-png.flaticon.com/512/732/732223.png' },
  { id: 'yahoo',    name: 'Yahoo Mail',               icon: 'https://cdn-icons-png.flaticon.com/512/217/217853.png' },
  { id: 'fastmail', name: 'Fastmail',                 icon: 'https://cdn-icons-png.flaticon.com/512/5968/5968534.png' },
  { id: 'other',    name: 'Outro Provider (IMAP)',     icon: '' },
];

const EmailLinking: React.FC = () => {
  const [selectedProvider, setSelectedProvider] = useState('');
  const [email, setEmail]                       = useState('');
  const [appPassword, setAppPassword]           = useState('');
  const [imapHost, setImapHost]                 = useState('');
  const [smtpHost, setSmtpHost]                 = useState('');
  const [showPassword, setShowPassword]         = useState(false);
  const [loading, setLoading]                   = useState(false);
  const [success, setSuccess]                   = useState(false);
  const [error, setError]                       = useState('');
  const [step, setStep]                         = useState<1 | 2>(1);

  const handleProviderSelect = (id: string) => {
    setSelectedProvider(id);
    const defaults = PROVIDER_DEFAULTS[id] ?? PROVIDER_DEFAULTS.other;
    setImapHost(defaults.imapHost);
    setSmtpHost(defaults.smtpHost);
    setError('');
    setStep(2);
  };

  const handleConfigure = async () => {
    if (!email || !appPassword || !imapHost || !smtpHost) {
      setError('Preencha todos os campos obrigatórios.');
      return;
    }
    setLoading(true);
    setError('');
    try {
      // Send credentials to Gateway → Gateway updates Hermes Agent env config
      await api.post('/emails/configure', {
        provider:     selectedProvider,
        emailAddress: email,
        appPassword:  appPassword,
        imapHost:     imapHost,
        smtpHost:     smtpHost,
        imapPort:     993,
        smtpPort:     587,
      });
      setSuccess(true);
    } catch (err: any) {
      const detail = err?.response?.data?.detail || err?.response?.data?.message || 'Erro ao configurar o email. Verifique as credenciais.';
      setError(detail);
    } finally {
      setLoading(false);
    }
  };

  const appPasswordGuide: Record<string, string> = {
    gmail:    'https://myaccount.google.com/apppasswords',
    outlook:  'https://account.microsoft.com/security',
    yahoo:    'https://login.yahoo.com/account/security',
    fastmail: 'https://app.fastmail.com/settings/security',
  };

  return (
    <LayoutBase>
      <div className="h-full flex flex-col items-center justify-center p-8 bg-[#f3f4f6] overflow-y-auto">
        <div className="max-w-xl w-full space-y-8 animate-fade-in py-8">

          {/* Header */}
          <div className="text-center space-y-4">
            <div className="w-20 h-20 bg-blue-600 rounded-[28px] flex items-center justify-center mx-auto shadow-xl shadow-blue-500/30 text-white">
              {success ? <CheckCircle2 size={40} className="animate-bounce" /> : <Mail size={40} />}
            </div>
            <h2 className="text-3xl font-black text-gray-900 tracking-tight">
              {success ? 'Email de Faturas Configurado!' : 'Configurar Caixa de Faturas'}
            </h2>
            <p className="text-gray-500 font-medium leading-relaxed">
              {success
                ? 'O Hermes Agent começará a monitorizar a caixa de entrada e a extrair faturas automaticamente.'
                : 'Configure o email dedicado de faturas da empresa. O Hermes Agent irá monitorizar esta caixa via IMAP e processar automaticamente todas as faturas recebidas.'}
            </p>
          </div>

          {success ? (
            /* Success State */
            <div className="bg-white p-10 rounded-[48px] shadow-2xl shadow-gray-200/50 border border-gray-100 space-y-6 text-center">
              <CheckCircle2 className="mx-auto text-green-500" size={64} />
              <div>
                <p className="font-black text-xl text-gray-900">{email}</p>
                <p className="text-gray-500 text-sm mt-1">Monitorização activa · a cada 30 segundos</p>
              </div>
              <div className="bg-green-50 border border-green-100 rounded-2xl p-4 text-left space-y-2">
                <p className="text-xs font-bold text-green-800 uppercase tracking-wider">O que acontece agora</p>
                <ul className="text-sm text-green-700 space-y-1">
                  <li>✓ Hermes Agent conectou-se via IMAP SSL (porta 993)</li>
                  <li>✓ Emails com faturas serão detectados automaticamente</li>
                  <li>✓ PDFs e imagens de faturas são extraídos com IA</li>
                  <li>✓ Dados são enviados para o dashboard em tempo real</li>
                </ul>
              </div>
              <button
                onClick={() => { setSuccess(false); setStep(1); setEmail(''); setAppPassword(''); }}
                className="flex items-center gap-2 mx-auto text-sm text-blue-600 hover:text-blue-700 font-semibold"
              >
                <RefreshCw size={14} /> Alterar configuração
              </button>
            </div>
          ) : step === 1 ? (
            /* Step 1: Provider Selection */
            <div className="bg-white p-10 rounded-[48px] shadow-2xl shadow-gray-200/50 border border-gray-100 space-y-6">
              <p className="text-[11px] font-extrabold text-gray-400 uppercase tracking-widest text-center">
                Escolha o provedor de email de faturas
              </p>

              {/* How it works info */}
              <div className="flex items-start gap-3 p-4 bg-blue-50 border border-blue-100 rounded-2xl">
                <Info size={16} className="text-blue-600 mt-0.5 flex-shrink-0" />
                <p className="text-xs text-blue-700 font-medium leading-relaxed">
                  O Hermes Agent monitorizará esta caixa via <strong>IMAP/SMTP</strong> — sem OAuth2,
                  sem tokens externos. Usa uma <strong>App Password</strong> do seu provedor de email.
                </p>
              </div>

              <div className="grid grid-cols-1 gap-3">
                {providers.map((p) => (
                  <button
                    key={p.id}
                    onClick={() => handleProviderSelect(p.id)}
                    className="flex items-center justify-between p-5 rounded-3xl border border-gray-100 bg-gray-50/50 hover:bg-white hover:border-blue-400/30 hover:shadow-lg hover:shadow-blue-500/5 transition-all group"
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-2xl bg-white border border-gray-100 flex items-center justify-center shadow-sm">
                        {p.icon ? (
                          <img src={p.icon} alt={p.name} className="w-7 h-7 object-contain" />
                        ) : (
                          <Globe size={20} className="text-gray-400" />
                        )}
                      </div>
                      <span className="font-bold text-gray-800 group-hover:text-blue-600 transition-colors text-sm">
                        {p.name}
                      </span>
                    </div>
                    <div className="w-6 h-6 rounded-full border-2 border-gray-200 group-hover:border-blue-500 group-hover:bg-blue-500 transition-all flex items-center justify-center">
                      <div className="w-2 h-2 rounded-full bg-transparent group-hover:bg-white transition-all" />
                    </div>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            /* Step 2: Credentials Form */
            <div className="bg-white p-10 rounded-[48px] shadow-2xl shadow-gray-200/50 border border-gray-100 space-y-6 animate-fade-in">
              <div className="flex items-center gap-3">
                <button onClick={() => setStep(1)} className="text-sm text-gray-400 hover:text-gray-600 font-semibold transition-colors">
                  ← Voltar
                </button>
                <span className="text-sm font-black text-gray-900">
                  {providers.find(p => p.id === selectedProvider)?.name}
                </span>
              </div>

              {/* App Password Guide */}
              {appPasswordGuide[selectedProvider] && (
                <div className="flex items-start gap-3 p-4 bg-amber-50 border border-amber-100 rounded-2xl">
                  <KeyRound size={16} className="text-amber-600 mt-0.5 flex-shrink-0" />
                  <div className="space-y-1">
                    <p className="text-xs font-bold text-amber-800">Precisa de uma App Password</p>
                    <p className="text-xs text-amber-700 leading-relaxed">
                      Não use a sua senha normal.{' '}
                      <a
                        href={appPasswordGuide[selectedProvider]}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="underline font-semibold hover:text-amber-900"
                      >
                        Criar App Password →
                      </a>
                    </p>
                  </div>
                </div>
              )}

              {/* Email field */}
              <div className="space-y-2">
                <label className="text-[11px] font-bold text-gray-400 uppercase tracking-widest pl-1">
                  Email de Faturas *
                </label>
                <div className="relative">
                  <Mail className="absolute left-5 top-1/2 -translate-y-1/2 text-gray-300" size={18} />
                  <input
                    type="email"
                    placeholder="faturas@empresa.com"
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                    className="w-full h-14 bg-gray-50 border border-gray-100 rounded-2xl pl-12 pr-4 font-semibold text-gray-900 focus:bg-white focus:ring-4 focus:ring-blue-500/10 focus:border-blue-400/30 outline-none transition-all placeholder:text-gray-300"
                  />
                </div>
              </div>

              {/* App Password field */}
              <div className="space-y-2">
                <label className="text-[11px] font-bold text-gray-400 uppercase tracking-widest pl-1">
                  App Password *
                </label>
                <div className="relative">
                  <Lock className="absolute left-5 top-1/2 -translate-y-1/2 text-gray-300" size={18} />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    placeholder="xxxx xxxx xxxx xxxx"
                    value={appPassword}
                    onChange={e => setAppPassword(e.target.value)}
                    className="w-full h-14 bg-gray-50 border border-gray-100 rounded-2xl pl-12 pr-12 font-mono font-semibold text-gray-900 focus:bg-white focus:ring-4 focus:ring-blue-500/10 focus:border-blue-400/30 outline-none transition-all placeholder:text-gray-300 placeholder:font-sans"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(v => !v)}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-300 hover:text-gray-500 transition-colors"
                  >
                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
              </div>

              {/* IMAP/SMTP hosts */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-[11px] font-bold text-gray-400 uppercase tracking-widest pl-1">
                    IMAP Host *
                  </label>
                  <div className="relative">
                    <Server className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-300" size={16} />
                    <input
                      type="text"
                      placeholder="imap.gmail.com"
                      value={imapHost}
                      onChange={e => setImapHost(e.target.value)}
                      className="w-full h-12 bg-gray-50 border border-gray-100 rounded-xl pl-10 pr-3 text-sm font-semibold text-gray-900 focus:bg-white focus:ring-4 focus:ring-blue-500/10 focus:border-blue-400/30 outline-none transition-all placeholder:text-gray-300"
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <label className="text-[11px] font-bold text-gray-400 uppercase tracking-widest pl-1">
                    SMTP Host *
                  </label>
                  <div className="relative">
                    <Server className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-300" size={16} />
                    <input
                      type="text"
                      placeholder="smtp.gmail.com"
                      value={smtpHost}
                      onChange={e => setSmtpHost(e.target.value)}
                      className="w-full h-12 bg-gray-50 border border-gray-100 rounded-xl pl-10 pr-3 text-sm font-semibold text-gray-900 focus:bg-white focus:ring-4 focus:ring-blue-500/10 focus:border-blue-400/30 outline-none transition-all placeholder:text-gray-300"
                    />
                  </div>
                </div>
              </div>

              {/* Ports info */}
              <p className="text-xs text-gray-400 text-center">
                Portas padrão: IMAP SSL 993 · SMTP STARTTLS 587
              </p>

              {/* Error */}
              {error && (
                <div className="p-4 bg-red-50 border border-red-100 rounded-2xl text-sm text-red-600 font-semibold">
                  {error}
                </div>
              )}

              {/* Submit */}
              <button
                onClick={handleConfigure}
                disabled={loading || !email || !appPassword || !imapHost || !smtpHost}
                className="w-full h-14 bg-blue-600 text-white rounded-2xl font-bold text-sm shadow-xl shadow-blue-500/20 flex items-center justify-center gap-3 hover:bg-blue-700 active:scale-95 transition-all disabled:opacity-50 disabled:active:scale-100"
              >
                {loading ? (
                  <><Loader2 className="animate-spin" size={18} /> A testar ligação IMAP...</>
                ) : (
                  <><Mail size={18} /> Activar Monitorização de Email</>
                )}
              </button>
            </div>
          )}

          {/* Trust indicators */}
          <div className="flex items-center justify-center gap-8 text-[11px] font-bold text-gray-400 uppercase tracking-widest opacity-60">
            <div className="flex items-center gap-2"><Lock size={12} /> <span>IMAP SSL</span></div>
            <div className="flex items-center gap-2"><ShieldCheck size={12} /> <span>App Password</span></div>
            <div className="flex items-center gap-2"><MessageSquare size={12} /> <span>Sem OAuth</span></div>
          </div>

        </div>
      </div>
    </LayoutBase>
  );
};

export default EmailLinking;

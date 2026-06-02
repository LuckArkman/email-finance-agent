import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Send, Bot, User, Sparkles, Settings, History,
  Info, ChevronRight, ShieldCheck, CreditCard,
  FileText, Wifi, WifiOff, Loader2, AlertCircle,
  RefreshCw, Clock, Hash
} from 'lucide-react';
import LayoutBase from '../components/LayoutBase';
import { agentApi, type ChatMessage, type AgentStatus, type AgentSession } from '../services/api';

// ─────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────
interface UIMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  error?: boolean;
}

// ─────────────────────────────────────────────────────────────
// Component: AgentChat
// ─────────────────────────────────────────────────────────────
const AgentChat: React.FC = () => {
  const [messages, setMessages] = useState<UIMessage[]>([
    {
      role: 'assistant',
      content: 'Olá! Sou o **Hermes Agent** — processamento financeiro autónomo por IA. Posso extrair faturas, verificar reconciliações, e responder a questões sobre as tuas finanças. Como posso ajudar?',
      timestamp: new Date(),
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [agentStatus, setAgentStatus] = useState<AgentStatus | null>(null);
  const [sessions, setSessions] = useState<AgentSession[]>([]);
  const [statusLoading, setStatusLoading] = useState(true);
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // ── Scroll to bottom whenever messages change ──
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  // ── Fetch agent status on mount ──
  const fetchStatus = useCallback(async () => {
    setStatusLoading(true);
    try {
      const status = await agentApi.getStatus();
      setAgentStatus(status);
    } catch {
      setAgentStatus({ online: false, version: 'N/A', model: 'N/A', provider: 'N/A', activeSessions: 0, message: 'Gateway inacessível' });
    } finally {
      setStatusLoading(false);
    }
  }, []);

  const fetchSessions = useCallback(async () => {
    try {
      const s = await agentApi.getSessions();
      setSessions(s.slice(0, 5)); // mostrar as 5 mais recentes
    } catch {
      // silencioso
    }
  }, []);

  useEffect(() => {
    fetchStatus();
    fetchSessions();
    // Atualizar estado a cada 30s
    const interval = setInterval(fetchStatus, 30_000);
    return () => clearInterval(interval);
  }, [fetchStatus, fetchSessions]);

  // ── Send message ──
  const handleSendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMsg: UIMessage = { role: 'user', content: input, timestamp: new Date() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    // Placeholder assistente
    const placeholder: UIMessage = { role: 'assistant', content: '', timestamp: new Date() };
    setMessages(prev => [...prev, placeholder]);

    try {
      // Construir histórico para o backend
      const history: ChatMessage[] = messages
        .concat(userMsg)
        .map(m => ({ role: m.role, content: m.content }));

      // Chamar o Hermes.Gateway → Hermes Agent
      const reply = await agentApi.chat(history);

      setMessages(prev => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          role: 'assistant',
          content: reply || 'Sem resposta do agente.',
          timestamp: new Date(),
        };
        return updated;
      });
    } catch (err: any) {
      const errorMsg = err?.response?.data?.error || 'Erro ao conectar ao Hermes Agent. Verifique se o backend está a correr.';
      setMessages(prev => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          role: 'assistant',
          content: errorMsg,
          timestamp: new Date(),
          error: true,
        };
        return updated;
      });
    } finally {
      setLoading(false);
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  };

  // ── Quick actions ──
  const sendQuickMessage = (text: string) => {
    setInput(text);
    setTimeout(() => inputRef.current?.focus(), 50);
  };

  const quickActions = [
    { label: 'Faturas Pendentes', icon: FileText, msg: 'Quais são as faturas pendentes de reconciliação?' },
    { label: 'Estado do Agente', icon: Sparkles, msg: 'Qual é o estado atual do Hermes Agent?' },
    { label: 'Último Processamento', icon: Clock, msg: 'Qual foi a última fatura processada?' },
    { label: 'Verificar Saldo', icon: CreditCard, msg: 'Mostra-me o resumo financeiro do mês.' },
  ];

  return (
    <LayoutBase>
      <div className="flex h-full bg-[#f8fafc] overflow-hidden">

        {/* ── Sidebar ── */}
        <div className="w-80 border-r border-gray-200 bg-white flex flex-col p-6 space-y-6 overflow-y-auto">

          {/* Header */}
          <div className="flex items-center space-x-3 text-blue-600">
            <div className="w-10 h-10 bg-blue-50 rounded-xl flex items-center justify-center">
              <Bot size={20} />
            </div>
            <span className="font-black uppercase tracking-widest text-xs">Agent Workspace</span>
          </div>

          {/* Status do Agente */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <p className="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em]">Hermes Agent</p>
              <button onClick={fetchStatus} className="text-gray-400 hover:text-blue-500 transition-colors">
                <RefreshCw size={12} className={statusLoading ? 'animate-spin' : ''} />
              </button>
            </div>

            <div className={`p-4 rounded-2xl border flex items-center space-x-3 ${agentStatus?.online
              ? 'bg-green-50/50 border-green-100'
              : 'bg-red-50/50 border-red-100'}`}>
              {agentStatus?.online
                ? <Wifi size={14} className="text-green-600 flex-shrink-0" />
                : <WifiOff size={14} className="text-red-500 flex-shrink-0" />}
              <div className="min-w-0">
                <span className={`text-[11px] font-black uppercase tracking-wider block ${agentStatus?.online ? 'text-green-600' : 'text-red-500'}`}>
                  {agentStatus?.online ? 'Online' : 'Offline'}
                </span>
                {agentStatus?.online && (
                  <span className="text-[10px] text-gray-500 truncate block">
                    {agentStatus.model} · {agentStatus.provider}
                  </span>
                )}
                {!agentStatus?.online && agentStatus?.message && (
                  <span className="text-[10px] text-red-400 truncate block">{agentStatus.message}</span>
                )}
              </div>
            </div>

            {agentStatus?.online && (
              <div className="grid grid-cols-2 gap-2">
                <div className="p-3 rounded-xl bg-blue-50/50 border border-blue-100 text-center">
                  <p className="text-[18px] font-black text-blue-600">{agentStatus.activeSessions}</p>
                  <p className="text-[9px] text-blue-500 font-bold uppercase tracking-wider">Sessões</p>
                </div>
                <div className="p-3 rounded-xl bg-purple-50/50 border border-purple-100 text-center">
                  <p className="text-[11px] font-black text-purple-600 truncate">{agentStatus.version || '—'}</p>
                  <p className="text-[9px] text-purple-500 font-bold uppercase tracking-wider">Versão</p>
                </div>
              </div>
            )}
          </div>

          {/* Quick Actions */}
          <div className="space-y-3">
            <p className="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em]">Ações Rápidas</p>
            <div className="space-y-2">
              {quickActions.map((action) => (
                <button
                  key={action.label}
                  onClick={() => sendQuickMessage(action.msg)}
                  className="w-full flex items-center justify-between p-3 rounded-2xl bg-gray-50 hover:bg-white border border-transparent hover:border-gray-100 transition-all text-left group"
                >
                  <div className="flex items-center space-x-3">
                    <action.icon size={16} className="text-gray-400 group-hover:text-blue-500 transition-colors flex-shrink-0" />
                    <span className="text-xs font-bold text-gray-700 group-hover:text-gray-900">{action.label}</span>
                  </div>
                  <ChevronRight size={12} className="text-gray-300 flex-shrink-0" />
                </button>
              ))}
            </div>
          </div>

          {/* Sessões Recentes */}
          {sessions.length > 0 && (
            <div className="space-y-3">
              <p className="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em]">Sessões Recentes</p>
              <div className="space-y-2">
                {sessions.map((s) => (
                  <div key={s.sessionId} className="p-3 rounded-xl bg-gray-50 border border-gray-100">
                    <div className="flex items-center space-x-2">
                      <Hash size={10} className="text-gray-400" />
                      <span className="text-[10px] font-mono text-gray-500 truncate">{s.sessionId.slice(0, 12)}…</span>
                    </div>
                    <div className="mt-1 flex items-center justify-between">
                      <span className="text-[10px] text-gray-400">{s.platform}</span>
                      <span className="text-[10px] text-gray-400">{s.messageCount} msgs</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Promo block */}
          <div className="mt-auto p-5 rounded-3xl bg-blue-600 text-white relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:scale-110 transition-transform">
              <Sparkles size={40} />
            </div>
            <h4 className="font-black text-sm mb-1">Modo Autónomo</h4>
            <p className="text-[11px] opacity-80 font-medium">O Hermes Agent monitoriza o email e processa faturas automaticamente.</p>
          </div>
        </div>

        {/* ── Chat Area ── */}
        <div className="flex-1 flex flex-col h-full bg-white">

          {/* Header */}
          <header className="h-20 bg-white border-b border-gray-100 flex items-center justify-between px-10">
            <div className="flex items-center space-x-4">
              <div className="relative">
                <div className="w-12 h-12 bg-blue-600 rounded-[18px] flex items-center justify-center text-white shadow-lg shadow-blue-500/20">
                  <Bot size={24} />
                </div>
                <div className={`absolute -bottom-1 -right-1 w-4 h-4 border-2 border-white rounded-full ${agentStatus?.online ? 'bg-green-500' : 'bg-gray-300'}`} />
              </div>
              <div>
                <h2 className="font-black text-gray-900 tracking-tight">Hermes Agent</h2>
                <p className={`text-[10px] font-bold uppercase tracking-widest ${agentStatus?.online ? 'text-green-500' : 'text-gray-400'}`}>
                  {statusLoading ? 'A verificar…' : agentStatus?.online ? `${agentStatus.model} · ${agentStatus.provider}` : 'Agente Offline'}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <button onClick={fetchSessions} className="p-3 text-gray-400 hover:text-blue-600 transition-colors" title="Histórico de Sessões">
                <History size={20} />
              </button>
              <button className="p-3 text-gray-400 hover:text-blue-600 transition-colors" title="Configurações">
                <Settings size={20} />
              </button>
            </div>
          </header>

          {/* Offline banner */}
          {!statusLoading && !agentStatus?.online && (
            <div className="mx-6 mt-4 p-4 bg-amber-50 border border-amber-200 rounded-2xl flex items-start space-x-3">
              <AlertCircle size={18} className="text-amber-500 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-bold text-amber-800">Hermes Agent offline</p>
                <p className="text-xs text-amber-600 mt-1">
                  O backend .NET está acessível, mas o Hermes Agent (porta 8642) não responde.
                  Inicia o agente com <code className="bg-amber-100 px-1 rounded">hermes gateway</code> e recarrega.
                </p>
              </div>
            </div>
          )}

          {/* Messages */}
          <div
            className="flex-1 overflow-y-auto p-10 space-y-6 scroll-smooth no-scrollbar bg-slate-50/30"
            ref={scrollRef}
          >
            {messages.map((m, idx) => (
              <div key={idx} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'} animate-in slide-in-from-bottom-2`}>
                <div className={`flex max-w-[80%] ${m.role === 'user' ? 'flex-row-reverse space-x-reverse' : 'flex-row'} items-start space-x-4`}>
                  <div className={`w-10 h-10 rounded-2xl flex items-center justify-center flex-shrink-0 shadow-sm ${m.role === 'user' ? 'bg-white border border-gray-200 text-gray-900' : m.error ? 'bg-red-500 text-white' : 'bg-blue-600 text-white shadow-md'}`}>
                    {m.role === 'user' ? <User size={18} /> : m.error ? <AlertCircle size={18} /> : <Sparkles size={18} />}
                  </div>
                  <div className="space-y-1">
                    <div className={`p-5 rounded-[24px] text-[14px] leading-relaxed font-medium ${m.role === 'user'
                      ? 'bg-white border border-gray-200 text-gray-800 rounded-tr-none'
                      : m.error
                        ? 'bg-red-50 border border-red-100 text-red-700 rounded-tl-none'
                        : 'bg-white border border-blue-100 text-gray-900 rounded-tl-none shadow-sm shadow-blue-500/5'}`}>
                      {m.content || (loading && idx === messages.length - 1 ? (
                        <div className="flex items-center space-x-1">
                          <div className="w-1.5 h-1.5 bg-blue-300 rounded-full animate-bounce" />
                          <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce delay-75" />
                          <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce delay-150" />
                        </div>
                      ) : '')}
                    </div>
                    <p className={`text-[10px] text-gray-400 ${m.role === 'user' ? 'text-right' : 'text-left'} px-2`}>
                      {m.timestamp.toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Input Area */}
          <div className="p-8 bg-white border-t border-gray-100">
            <div className="max-w-4xl mx-auto relative group">
              <input
                ref={inputRef}
                type="text"
                placeholder={agentStatus?.online ? 'Pergunta sobre faturas, orçamentos ou contas…' : 'Hermes Agent offline — inicia o agente primeiro'}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSendMessage()}
                disabled={loading}
                autoFocus
                className="w-full h-16 bg-gray-50 border border-gray-100 rounded-[28px] pl-8 pr-20 font-bold text-base text-gray-900 focus:bg-white focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500/20 outline-none transition-all placeholder:text-gray-300 disabled:opacity-60"
              />
              <button
                onClick={handleSendMessage}
                disabled={!input.trim() || loading}
                className="absolute right-3 top-3 w-10 h-10 bg-blue-600 rounded-2xl flex items-center justify-center text-white shadow-lg shadow-blue-500/20 hover:bg-blue-700 active:scale-95 transition-all disabled:opacity-30"
              >
                {loading ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
              </button>
            </div>
            <div className="flex justify-center mt-4 space-x-6 text-[10px] uppercase font-black tracking-widest text-gray-400">
              <div className="flex items-center space-x-2"><ShieldCheck size={12} /><span>Privacy Secured</span></div>
              <div className="flex items-center space-x-2">
                <Sparkles size={12} />
                <span>{agentStatus?.model || 'Hermes Agent'}</span>
              </div>
              <div className="flex items-center space-x-2"><Info size={12} /><span>via Hermes Gateway</span></div>
            </div>
          </div>
        </div>
      </div>
    </LayoutBase>
  );
};

export default AgentChat;

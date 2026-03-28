import React, { useState, useEffect, useRef } from 'react';
import { 
  Send, 
  Bot, 
  User, 
  Sparkles, 
  Settings, 
  History,
  Info,
  ChevronRight,
  ShieldCheck,
  CreditCard,
  FileText
} from 'lucide-react';
import LayoutBase from '../components/LayoutBase';
import api from '../services/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

const AgentChat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: 'Olá! Eu sou o Sustentacódigo Agent Brain. Estou aqui para ajudar-te com as tuas finanças, faturas e orçamentos. Como posso ajudar hoje?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMsg: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const resp = await api.post('/chat/converse', {
        messages: [...messages, userMsg].map(m => ({ role: m.role, content: m.content }))
      });
      
      const assistantMsg: Message = { role: 'assistant', content: resp.data.response };
      setMessages(prev => [...prev, assistantMsg]);
    } catch (err) {
      console.error("Chat error", err);
      setMessages(prev => [...prev, { role: 'assistant', content: 'Lamento, tive um erro ao processar a tua mensagem. Podes tentar novamente?' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <LayoutBase>
      <div className="flex h-full bg-[#f8fafc] overflow-hidden">
         {/* Sidebar with Stats and Quick Actions */}
         <div className="w-80 border-r border-gray-200 bg-white flex flex-col p-6 space-y-8">
            <div className="flex items-center space-x-3 text-blue-600">
               <div className="w-10 h-10 bg-blue-50 rounded-xl flex items-center justify-center">
                  <Bot size={20} />
               </div>
               <span className="font-black uppercase tracking-widest text-xs">Agent Workspace</span>
            </div>

            <div className="space-y-4">
               <p className="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em]">Quick Insights</p>
               <div className="grid grid-cols-1 gap-2">
                  <div className="p-4 rounded-2xl bg-blue-50/50 border border-blue-100 flex items-center space-x-3">
                     <ShieldCheck size={14} className="text-blue-600" />
                     <span className="text-[11px] font-black text-blue-600 uppercase tracking-wider">MCP Active</span>
                  </div>
                  <div className="p-4 rounded-2xl bg-green-50/50 border border-green-100 flex items-center space-x-3">
                     <Sparkles size={14} className="text-green-600" />
                     <span className="text-[11px] font-black text-green-600 uppercase tracking-wider">Brain: Llama3</span>
                  </div>
               </div>
            </div>

            <div className="space-y-4">
               <p className="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em]">Context Tools</p>
               <div className="space-y-2">
                  <button className="w-full flex items-center justify-between p-4 rounded-2xl bg-gray-50 hover:bg-white border border-transparent hover:border-gray-100 transition-all text-left group">
                     <div className="flex items-center space-x-3">
                        <CreditCard size={18} className="text-gray-400 group-hover:text-blue-500 transition-colors" />
                        <span className="text-sm font-bold text-gray-900">Get Balance</span>
                     </div>
                     <ChevronRight size={14} className="text-gray-300" />
                  </button>
                  <button className="w-full flex items-center justify-between p-4 rounded-2xl bg-gray-50 hover:bg-white border border-transparent hover:border-gray-100 transition-all text-left group">
                     <div className="flex items-center space-x-3">
                        <FileText size={18} className="text-gray-400 group-hover:text-blue-500 transition-colors" />
                        <span className="text-sm font-bold text-gray-900">List Invoices</span>
                     </div>
                     <ChevronRight size={14} className="text-gray-300" />
                  </button>
               </div>
            </div>

            <div className="mt-auto p-6 rounded-3xl bg-blue-600 text-white relative overflow-hidden group">
               <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:scale-110 transition-transform">
                  <Sparkles size={40} />
               </div>
               <h4 className="font-black text-sm mb-2">Modo Orçamento</h4>
               <p className="text-[11px] opacity-80 font-medium">Deixa o Agente otimizar os teus gastos mensais automaticamente.</p>
               <button className="mt-4 px-4 py-2 bg-white/20 rounded-xl text-[10px] font-black uppercase tracking-wider hover:bg-white/30 transition-all">Ativar Agora</button>
            </div>
         </div>

         {/* Chat Area */}
         <div className="flex-1 flex flex-col h-full bg-white">
            {/* Header */}
            <header className="h-20 bg-white border-b border-gray-100 flex items-center justify-between px-10">
               <div className="flex items-center space-x-4">
                  <div className="relative">
                     <div className="w-12 h-12 bg-blue-600 rounded-[18px] flex items-center justify-center text-white shadow-lg shadow-blue-500/20">
                        <Bot size={24} />
                     </div>
                     <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 border-2 border-white rounded-full"></div>
                  </div>
                  <div>
                     <h2 className="font-black text-gray-900 tracking-tight">Agent Brain</h2>
                     <p className="text-[10px] text-green-500 font-bold uppercase tracking-widest">Always Active</p>
                  </div>
               </div>
               <div className="flex items-center space-x-2">
                  <button className="p-3 text-gray-400 hover:text-blue-600 transition-colors"><History size={20}/></button>
                  <button className="p-3 text-gray-400 hover:text-blue-600 transition-colors"><Settings size={20}/></button>
               </div>
            </header>

            {/* Messages */}
            <div 
              className="flex-1 overflow-y-auto p-10 space-y-8 scroll-smooth no-scrollbar bg-slate-50/30"
              ref={scrollRef}
            >
               {messages.map((m, idx) => (
                 <div key={idx} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'} animate-in slide-in-from-bottom-2`}>
                    <div className={`flex max-w-[80%] ${m.role === 'user' ? 'flex-row-reverse space-x-reverse' : 'flex-row'} items-start space-x-4`}>
                       <div className={`w-10 h-10 rounded-2xl flex items-center justify-center flex-shrink-0 ${m.role === 'user' ? 'bg-white border border-gray-200 text-gray-900 shadow-sm' : 'bg-blue-600 text-white shadow-md'}`}>
                          {m.role === 'user' ? <User size={18}/> : <Sparkles size={18}/>}
                       </div>
                       <div className={`p-6 rounded-[28px] text-[15px] leading-relaxed font-medium ${m.role === 'user' ? 'bg-white border border-gray-200 text-gray-800 rounded-tr-none' : 'bg-white border border-blue-100 text-gray-900 rounded-tl-none shadow-sm shadow-blue-500/5'}`}>
                          {m.content}
                       </div>
                    </div>
                 </div>
               ))}
               {loading && (
                 <div className="flex justify-start">
                    <div className="flex items-start space-x-4">
                       <div className="w-10 h-10 rounded-2xl bg-blue-600 text-white flex items-center justify-center shadow-md animate-pulse">
                          <Bot size={18} />
                       </div>
                       <div className="h-14 w-24 bg-white border border-gray-100 rounded-[28px] rounded-tl-none flex items-center justify-center space-x-1 shadow-sm">
                          <div className="w-1.5 h-1.5 bg-blue-300 rounded-full animate-bounce"></div>
                          <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce delay-75"></div>
                          <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce delay-150"></div>
                       </div>
                    </div>
                 </div>
               )}
            </div>

            {/* InputArea */}
            <div className="p-8 bg-white border-t border-gray-100">
               <div className="max-w-4xl mx-auto relative group">
                  <input 
                    type="text" 
                    placeholder="Pergunta sobre faturas, orçamentos ou contas..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    autoFocus
                    className="w-full h-16 bg-gray-50 border border-gray-100 rounded-[28px] pl-8 pr-20 font-bold text-lg text-gray-900 focus:bg-white focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500/20 outline-none transition-all placeholder:text-gray-300"
                  />
                  <button 
                    onClick={handleSendMessage}
                    disabled={!input.trim() || loading}
                    className="absolute right-3 top-3 w-10 h-10 bg-blue-600 rounded-2xl flex items-center justify-center text-white shadow-lg shadow-blue-500/20 hover:bg-blue-700 active:scale-95 transition-all disabled:opacity-30"
                  >
                     <Send size={18} />
                  </button>
               </div>
               <div className="flex justify-center mt-4 space-x-6 text-[10px] uppercase font-black tracking-widest text-gray-400">
                  <div className="flex items-center space-x-2"><ShieldCheck size={12}/> <span>Privacy Secured</span></div>
                  <div className="flex items-center space-x-2"><Sparkles size={12}/> <span>Brain: Llama 3 (Ollama)</span></div>
                  <div className="flex items-center space-x-2"><Info size={12}/> <span>AI-Powered Reasoning</span></div>
               </div>
            </div>
         </div>
      </div>
    </LayoutBase>
  );
};

export default AgentChat;

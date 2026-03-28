import React, { useState } from 'react';
import { 
  Mail, 
  ArrowRight, 
  ShieldCheck, 
  Globe, 
  Lock,
  MessageSquare,
  CheckCircle2,
  ChevronRight,
  Loader2
} from 'lucide-react';
import LayoutBase from '../components/LayoutBase';
import api from '../services/api';

const EmailLinking: React.FC = () => {
  const [step, setStep] = useState(1);
  const [email, setEmail] = useState('');
  const [selectedProvider, setSelectedProvider] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const providers = [
    { id: 'google', name: 'Google Workspace / Gmail', icon: 'https://cdn-icons-png.flaticon.com/512/2991/2991148.png', color: 'bg-red-50' },
    { id: 'outlook', name: 'Microsoft Outlook / 365', icon: 'https://cdn-icons-png.flaticon.com/512/732/732223.png', color: 'bg-blue-50' },
    { id: 'imap', name: 'Outro (IMAP/SMTP)', icon: '', color: 'bg-gray-50' }
  ];

  const handleProviderSelect = (p: any) => {
    setSelectedProvider(p.id);
    setStep(2);
  };

  const handleSyncClick = async () => {
    if (!email) return;
    setLoading(true);
    try {
      await api.post('/emails/accounts', {
        provider: selectedProvider,
        email_address: email,
        access_token: "MOCKED_TOKEN", // This would be provided by OAuth
        refresh_token: "MOCKED_REFRESH"
      });
      setSuccess(true);
      setTimeout(() => {
        setStep(1);
        setSuccess(false);
        setEmail('');
      }, 2000);
    } catch (err) {
      console.error("Failed to link email", err);
      alert("Erro ao vincular conta de email.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <LayoutBase>
      <div className="h-full flex flex-col items-center justify-center p-8 bg-[#f3f4f6]">
         <div className="max-w-xl w-full space-y-12 animate-fade-in">
            <div className="text-center space-y-4">
               <div className="w-20 h-20 bg-blue-600 rounded-[28px] flex items-center justify-center mx-auto shadow-xl shadow-blue-500/30 text-white">
                  {success ? <CheckCircle2 size={40} className="animate-bounce" /> : <Mail size={40} />}
               </div>
               <h2 className="text-3xl font-black text-gray-900 tracking-tight">
                 {success ? "Conta Vinculada!" : "Vincular Conta de Email"}
               </h2>
               <p className="text-gray-500 font-medium">
                 {success ? "O Agente começará a analisar a sua inbox agora." : "Ligue o seu email para que o Agente IA possa recolher faturas automaticamente."}
               </p>
            </div>

            <div className="bg-white p-10 rounded-[48px] shadow-sm border border-gray-100 space-y-8 shadow-2xl shadow-gray-200/50">
               {step === 1 ? (
                 <div className="space-y-6">
                    <p className="text-[11px] font-extrabold text-gray-400 uppercase tracking-widest text-center">Escolha o seu provedor</p>
                    <div className="grid grid-cols-1 gap-4">
                       {providers.map((p) => (
                         <button 
                           key={p.name}
                           onClick={() => handleProviderSelect(p)}
                           className="flex items-center justify-between p-6 rounded-3xl border border-gray-50 bg-gray-50/30 hover:bg-white hover:border-blue-500/20 hover:shadow-xl hover:shadow-blue-500/5 transition-all group"
                         >
                            <div className="flex items-center space-x-6">
                               <div className={`w-14 h-14 rounded-2xl ${p.color} flex items-center justify-center border border-inherit`}>
                                  {p.icon ? (
                                    <img src={p.icon} alt={p.name} className="w-7 h-7" />
                                  ) : (
                                    <Globe size={24} className="text-gray-400" />
                                  )}
                               </div>
                               <span className="font-black text-gray-900 group-hover:text-blue-600 transition-colors uppercase text-xs tracking-wider">{p.name}</span>
                            </div>
                            <ChevronRight size={20} className="text-gray-300 group-hover:text-blue-500 transition-colors" />
                         </button>
                       ))}
                    </div>
                 </div>
               ) : (
                 <div className="space-y-8 animate-fade-in">
                    <div className="space-y-4">
                       <label className="text-[11px] font-bold text-gray-400 uppercase tracking-widest pl-2">Endereço de Email</label>
                       <div className="relative group">
                          <Mail className="absolute left-6 top-1/2 -translate-y-1/2 text-gray-300 group-focus-within:text-blue-500 transition-colors" size={24} />
                          <input 
                            type="email" 
                            placeholder="exemplo@empresa.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            disabled={loading || success}
                            className="w-full h-16 bg-gray-50 border border-gray-100 rounded-[28px] pl-16 pr-6 font-bold text-lg text-gray-900 focus:bg-white focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500/20 outline-none transition-all placeholder:text-gray-300 shadow-inner disabled:opacity-50"
                          />
                       </div>
                    </div>

                    <div className="space-y-4 pt-4 border-t border-gray-50">
                       <div className="flex items-start space-x-4 p-4 rounded-2xl bg-blue-50/50 border border-blue-100">
                          <ShieldCheck size={20} className="text-blue-600 mt-1" />
                          <div className="space-y-1">
                             <p className="text-[13px] font-black text-gray-900">Segurança Total</p>
                             <p className="text-[11px] text-gray-500 font-medium leading-relaxed">Não armazenamos a sua password. A ligação é feita via OAuth2 ou Chave de Aplicação (App Password) encriptada.</p>
                          </div>
                       </div>
                    </div>

                    <div className="flex space-x-4">
                       <button 
                         disabled={loading || success} 
                         onClick={() => setStep(1)} 
                         className="px-8 h-16 bg-gray-50 text-gray-400 rounded-[28px] font-bold text-sm hover:bg-gray-100 transition-all active:scale-95 disabled:pointer-events-none"
                       >
                         Voltar
                       </button>
                       <button 
                         onClick={handleSyncClick}
                         disabled={loading || success || !email}
                         className="flex-1 h-16 bg-blue-600 text-white rounded-[28px] font-bold text-sm shadow-xl shadow-blue-500/20 flex items-center justify-center space-x-3 hover:bg-blue-700 active:scale-95 transition-all disabled:opacity-50 disabled:active:scale-100"
                       >
                          {loading ? <Loader2 className="animate-spin" size={20} /> : (
                            <>
                              <span>Sincronizar Agora</span>
                              <ArrowRight size={20} />
                            </>
                          )}
                       </button>
                    </div>
                 </div>
               )}
            </div>

            <div className="flex items-center justify-center space-x-10 text-[11px] font-extrabold text-gray-400 uppercase tracking-widest opacity-60">
               <div className="flex items-center space-x-2"><Lock size={14} /> <span>Encriptação SSL</span></div>
               <div className="flex items-center space-x-2"><CheckCircle2 size={14} /> <span>GDPR Compliant</span></div>
               <div className="flex items-center space-x-2"><MessageSquare size={14} /> <span>Suporte 24/7</span></div>
            </div>
         </div>
      </div>
    </LayoutBase>
  );
};

export default EmailLinking;

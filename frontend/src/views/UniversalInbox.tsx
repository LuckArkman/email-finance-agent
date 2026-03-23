import React, { useState, useEffect } from 'react';
import { 
  Mail, 
  Search, 
  RefreshCw, 
  Calendar, 
  FileText, 
  ShoppingBag, 
  Eye, 
  Filter,
  ArrowUpDown,
  Clock,
  Loader2
} from 'lucide-react';
import LayoutBase from '../components/LayoutBase';
import api from '../services/api';

interface SimpleEmail {
  id: string;
  subject: string;
  sender: string;
  date: string;
  category: string;
  snippet: string;
}

const UniversalInbox: React.FC = () => {
  const [emails, setEmails] = useState<SimpleEmail[]>([]);
  const [filterDays, setFilterDays] = useState(30);
  const [loading, setLoading] = useState(true);
  
  const fetchEmails = async () => {
    setLoading(true);
    try {
      const res = await api.get('/emails/inbox');
      setEmails(res.data || []);
    } catch (err) {
      console.error("Failed to fetch emails", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEmails();
  }, []);

  return (
    <LayoutBase>
      <div className="p-8 space-y-10 animate-fade-in bg-[#f3f4f6] h-full overflow-y-auto no-scrollbar">
         <div className="flex items-center justify-between">
            <div className="space-y-1">
               <h2 className="text-2xl font-black text-gray-900 tracking-tight">Entrada Financeira</h2>
               <p className="text-gray-400 text-[11px] font-extrabold uppercase tracking-widest">Documentos Capturados via Email</p>
            </div>
            <div className="flex items-center space-x-3">
               <div className="flex items-center bg-white border border-gray-100 rounded-xl px-4 py-2 text-[13px] font-bold shadow-sm">
                  <Clock size={16} className="text-blue-500 mr-2" />
                  <span className="text-gray-400 mr-2 uppercase text-[10px] tracking-widest">Período:</span>
                  <select 
                    value={filterDays}
                    onChange={(e) => setFilterDays(Number(e.target.value))}
                    className="bg-transparent outline-none text-gray-900 border-none p-0 cursor-pointer font-black"
                  >
                     <option value={3}>3 dias</option>
                     <option value={7}>7 dias</option>
                     <option value={10}>10 dias</option>
                     <option value={15}>15 dias</option>
                     <option value={30}>30 dias</option>
                  </select>
               </div>
               <button 
                onClick={fetchEmails}
                className="flex items-center space-x-2 px-5 py-3 bg-white border border-gray-200 rounded-xl text-[13px] font-black shadow-sm hover:bg-gray-50 active:scale-95 transition-all"
               >
                 <RefreshCw size={16} className={loading ? 'animate-spin text-blue-500' : 'text-gray-400'} /> 
                 <span>Sincronizar</span>
               </button>
            </div>
         </div>

         <div className="flex items-center space-x-4">
            <div className="relative flex-1 group">
               <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-300 group-focus-within:text-blue-500 transition-colors" size={20} />
               <input 
                 type="text" 
                 placeholder="Pesquisar em e-mails capturados..." 
                 className="w-full bg-white border border-gray-100 rounded-2xl py-4 pl-12 pr-6 text-sm font-medium focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500/20 shadow-sm outline-none transition-all placeholder:text-gray-300"
               />
            </div>
            <button className="flex items-center space-x-2 px-8 py-4 bg-white border border-gray-100 rounded-2xl text-[13px] font-black shadow-sm hover:border-blue-500/20 transition-all text-gray-500">
               <Filter size={18} /> 
               <span>Filtros Avançados</span>
            </button>
         </div>

         <div className="bg-white rounded-[40px] shadow-sm border border-gray-100 overflow-hidden shadow-2xl shadow-gray-200/50 flex flex-col flex-1">
            {loading && emails.length === 0 ? (
               <div className="flex-1 flex flex-col items-center justify-center py-32 space-y-6">
                  <div className="relative">
                    <Loader2 size={48} className="animate-spin text-blue-500" />
                    <Mail size={16} className="absolute top-1/2 left-1/2 -translate-y-1/2 -translate-x-1/2 text-blue-600" />
                  </div>
                  <p className="text-gray-400 font-black uppercase tracking-widest text-[11px]">Procurando correspondência financeira...</p>
               </div>
            ) : emails.length === 0 ? (
               <div className="flex-1 flex flex-col items-center justify-center py-32 space-y-4">
                  <div className="w-20 h-20 bg-gray-50 rounded-[28px] flex items-center justify-center text-gray-200">
                     <Mail size={40} />
                  </div>
                  <div className="text-center">
                    <p className="text-gray-900 font-black text-sm uppercase tracking-tight">Nenhuma correspondência encontrada</p>
                    <p className="text-gray-400 text-[11px] font-bold uppercase tracking-widest mt-1">Ligue a sua conta de email para começar</p>
                  </div>
               </div>
            ) : (
               <div className="overflow-auto no-scrollbar">
                  <table className="w-full text-left border-collapse">
                     <thead>
                        <tr className="border-b border-gray-50 bg-gray-50/30 font-black text-gray-400 uppercase tracking-widest text-[10px]">
                           <th className="p-6 pl-10 border-r border-gray-50/50">Status IA</th>
                           <th className="p-6 border-r border-gray-50/50">
                              <div className="flex items-center justify-between">
                                 <span>Remetente</span>
                                 <ArrowUpDown size={12} className="text-gray-300" />
                              </div>
                           </th>
                           <th className="p-6 border-r border-gray-50/50">Assunto</th>
                           <th className="p-6 border-r border-gray-50/50">Categoria</th>
                           <th className="p-6 text-right pr-10">Opções</th>
                        </tr>
                     </thead>
                     <tbody className="divide-y divide-gray-50">
                        {emails.map((email) => (
                          <tr key={email.id} className="group hover:bg-gray-50/50 transition-all cursor-pointer">
                             <td className="p-6 pl-10 border-r border-gray-50/50">
                                <div className={`w-12 h-12 rounded-2xl flex items-center justify-center transition-all ${
                                  email.category !== 'Non-Financial' ? 'bg-blue-50 text-blue-500 shadow-sm' : 'bg-gray-50 text-gray-300'
                                }`}>
                                   <Calendar size={18} />
                                </div>
                             </td>
                             <td className="p-6 border-r border-gray-50/50 max-w-[200px]">
                                <div className="space-y-1">
                                   <p className="font-black text-gray-900 truncate">{email.sender}</p>
                                   <p className="text-[10px] text-blue-500/60 font-black uppercase tracking-widest">{email.date}</p>
                                </div>
                             </td>
                             <td className="p-6 border-r border-gray-50/50 max-w-sm">
                                <div className="space-y-1">
                                   <h4 className="font-extrabold text-gray-800 line-clamp-1 text-sm">{email.subject}</h4>
                                   <p className="text-[12px] text-gray-400 line-clamp-1 italic font-medium leading-relaxed">"{email.snippet}"</p>
                                </div>
                             </td>
                             <td className="p-6 border-r border-gray-50/50">
                                <span className={`inline-flex items-center space-x-2 px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest shadow-sm border ${
                                  email.category === 'Fatura' || email.category === 'Accounts Payable' ? 'bg-blue-50 text-blue-600 border-blue-100' : 
                                  email.category === 'Receipt' ? 'bg-purple-50 text-purple-600 border-purple-100' : 'bg-gray-50 text-gray-400 border-gray-100'
                                }`}>
                                   {email.category === 'Receipt' ? <ShoppingBag size={12} /> : <FileText size={12} />}
                                   <span>{email.category}</span>
                                </span>
                             </td>
                             <td className="p-6 text-right pr-10">
                                <button className="p-3.5 bg-white border border-gray-100 hover:bg-blue-600 hover:text-white rounded-2xl text-gray-400 shadow-sm transition-all transform active:scale-95 group-hover:shadow-lg group-hover:shadow-blue-500/10">
                                   <Eye size={18} />
                                </button>
                             </td>
                          </tr>
                        ))}
                     </tbody>
                  </table>
                  
                  <div className="p-8 bg-gray-50/30 flex justify-between items-center px-10 border-t border-gray-50">
                     <span className="text-[10px] font-extrabold text-gray-400 uppercase tracking-widest">Total: {emails.length} capturas automáticas</span>
                     <div className="flex space-x-3">
                        <button className="px-6 py-2.5 bg-white border border-gray-200 rounded-2xl text-[12px] font-black text-gray-300 opacity-50 cursor-not-allowed">Anterior</button>
                        <button className="px-6 py-2.5 bg-white border border-gray-200 rounded-2xl text-[12px] font-black text-gray-300 opacity-50 cursor-not-allowed">Próximo</button>
                     </div>
                  </div>
               </div>
            )}
         </div>
      </div>
    </LayoutBase>
  );
};

export default UniversalInbox;

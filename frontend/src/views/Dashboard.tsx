import React, { useEffect, useState } from 'react';
import { 
  Search, 
  Grid, 
  List, 
  Share2,
  FileText,
  MessageCircle,
  Mail,
  Upload,
  Zap,
  CheckCircle2,
  Plus,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import api from '../services/api';
import LayoutBase from '../components/LayoutBase';

const Dashboard: React.FC = () => {
  const [pendingDocs, setPendingDocs] = useState<any[]>([]);
  const [recentDocs, setRecentDocs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const queueRes = await api.get('/documents/queue');
      // Backend returns a list of documents in 'pending' status
      setPendingDocs(queueRes.data || []);
      
      // For now, recent docs might still be mocked or I can fetch approved invoices
      const invoicesRes = await api.get('/invoices?limit=4&status_filter=paid');
      setRecentDocs(invoicesRes.data.data || []);
    } catch (err) {
      console.error("Failed to fetch dashboard data", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  return (
    <LayoutBase>
      <div className="space-y-10 animate-fade-in p-8 h-full overflow-y-auto no-scrollbar bg-[#f3f4f6]">
        {/* Top Header with Search and Actions */}
        <div className="flex items-center justify-between">
           <div className="flex items-center space-x-6">
              <div className="flex space-x-2">
                 <button className="p-3 bg-white text-gray-400 hover:text-gray-900 border border-gray-100 rounded-xl transition-all shadow-sm">
                    <ChevronLeft size={20} />
                 </button>
                 <button className="p-3 bg-white text-gray-400 hover:text-gray-900 border border-gray-100 rounded-xl transition-all shadow-sm">
                    <ChevronRight size={20} />
                 </button>
              </div>
              <div className="space-y-0.5">
                 <h1 className="text-2xl font-black text-gray-900 tracking-tight">Recolha de Informação</h1>
                 <p className="text-gray-400 text-[11px] font-extrabold uppercase tracking-widest">Controlo de Fluxos de Entrada</p>
              </div>
           </div>

           <div className="flex items-center space-x-4 flex-1 max-w-2xl px-8">
              <div className="relative w-full group">
                 <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-300 group-focus-within:text-blue-500 transition-colors" size={20} />
                 <input 
                   type="text" 
                   placeholder="Pesquisar documentos, datas ou valores..." 
                   className="w-full bg-white border border-gray-100 rounded-2xl py-3.5 pl-12 pr-6 text-sm font-medium focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500/20 shadow-sm outline-none transition-all placeholder:text-gray-300"
                 />
              </div>
           </div>

           <div className="flex items-center space-x-2">
              <button className="p-3 text-gray-400 bg-white hover:bg-gray-50 border border-gray-100 rounded-xl transition-all shadow-sm"><Grid size={20} /></button>
              <button className="p-3 text-gray-400 bg-white hover:bg-gray-50 border border-gray-100 rounded-xl transition-all shadow-sm"><List size={20} /></button>
              <div className="w-px h-8 bg-gray-200 mx-3" />
              <button className="p-3 text-gray-400 bg-white hover:bg-gray-50 border border-gray-100 rounded-xl transition-all shadow-sm"><Share2 size={20} /></button>
           </div>
        </div>

        {/* Processamento Pendente Section */}
        <section className="space-y-8">
           <div className="flex items-center space-x-4">
              <h2 className="text-[11px] font-black text-gray-400 uppercase tracking-widest">Processamento Pendente</h2>
              <span className="bg-blue-600 text-white text-[10px] font-black px-3 py-1 rounded-full shadow-lg shadow-blue-500/20">{pendingDocs.length}</span>
           </div>

           <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
              {loading && pendingDocs.length === 0 ? (
                <>
                  <SkeletonCard />
                  <SkeletonCard />
                  <SkeletonCard />
                </>
              ) : (
                pendingDocs.map((doc) => (
                  <div key={doc.id} className="bg-white p-6 rounded-[40px] shadow-sm border border-gray-100 hover:shadow-2xl hover:shadow-gray-200/50 transition-all group relative overflow-hidden flex flex-col items-center">
                     <div className="absolute top-6 right-6 z-10">
                        <span className={`text-[9px] font-black px-2.5 py-1 rounded-lg tracking-wider border shadow-sm ${
                          doc.status === 'pending' ? 'bg-orange-50 text-orange-600 border-orange-100' : 'bg-blue-50 text-blue-600 border-blue-100'
                        }`}>
                          {doc.status === 'pending' ? 'OCR PENDENTE' : 'A ANALISAR'}
                        </span>
                     </div>
                     
                     <div className="w-full aspect-[3/4] bg-gray-50/50 rounded-[32px] mb-6 flex items-center justify-center border border-gray-100 group-hover:bg-blue-50 group-hover:border-blue-200 transition-all duration-500 overflow-hidden relative shadow-inner">
                        <div className="bg-white p-6 shadow-2xl border border-gray-50 rounded-2xl transform transition-transform group-hover:scale-110 duration-700">
                           <FileText className="text-gray-100" size={64} />
                        </div>
                        <div className="absolute inset-0 bg-blue-600/0 group-hover:bg-blue-600/5 transition-colors" />
                     </div>

                     <div className="text-center space-y-2 w-full">
                        <h4 className="font-extrabold text-gray-900 text-sm truncate px-4">{doc.filename || doc.vendor_name || 'Documento_IA.pdf'}</h4>
                        <div className="flex items-center justify-center space-x-3 text-[10px] font-black tracking-widest text-gray-400 uppercase">
                           {doc.source === 'whatsapp' ? <MessageCircle size={14} className="text-green-500" /> : doc.source === 'email' ? <Mail size={14} className="text-blue-500" /> : <Upload size={14} className="text-gray-400" />}
                           <span className="capitalize">{doc.source || 'Manual'}</span>
                           <span className="text-gray-200">•</span>
                           <span>{doc.created_at ? new Date(doc.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '---'}</span>
                        </div>
                     </div>
                  </div>
                ))
              )}
              
              <button className="bg-white rounded-[40px] border-2 border-dashed border-gray-100 flex flex-col items-center justify-center p-8 text-gray-300 hover:bg-white hover:border-blue-500/20 hover:shadow-xl hover:shadow-blue-500/5 transition-all duration-500 space-y-4 group">
                 <div className="w-16 h-16 rounded-[24px] bg-gray-50 flex items-center justify-center shadow-inner group-hover:bg-blue-50 transition-colors">
                    <Plus size={32} className="text-gray-200 group-hover:text-blue-500 transition-colors" />
                 </div>
                 <div className="text-center">
                    <span className="text-[13px] font-black text-gray-900 block">Importar Ficheiro</span>
                    <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mt-1">Manual / Fotos</span>
                 </div>
              </button>
           </div>
        </section>

        {/* Recently Scanned Section */}
        <section className="space-y-8">
           <h2 className="text-[11px] font-black text-gray-400 uppercase tracking-widest">Recentemente Digitalizados</h2>
           <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
              {recentDocs.length === 0 && !loading && (
                 <div className="col-span-full py-20 text-center opacity-30 italic text-gray-400">Nenhum documento processado recentemente.</div>
              )}
              {recentDocs.map((doc) => (
                <div key={doc.id} className="bg-white p-6 rounded-[40px] shadow-sm border border-gray-100 hover:shadow-2xl hover:shadow-gray-200/50 transition-all group cursor-pointer flex flex-col">
                   <div className="w-full aspect-[3/4] bg-gray-50/50 rounded-[32px] mb-6 flex items-center justify-center relative border border-gray-50 shadow-inner group-hover:bg-white transition-colors">
                      <FileText className="text-gray-100" size={80} />
                      <div className="absolute bottom-6 left-6">
                         <div className="flex items-center space-x-2 bg-white text-green-500 text-[10px] font-black px-3 py-1.5 rounded-full uppercase tracking-widest shadow-xl border border-green-50 shadow-green-500/10">
                            <CheckCircle2 size={12} strokeWidth={3} />
                            <span>APROVADO</span>
                         </div>
                      </div>
                   </div>
                   <div className="flex justify-between items-start px-2">
                      <div className="space-y-1">
                         <h4 className="font-extrabold text-gray-900 text-sm truncate w-32">{doc.filename || doc.vendor_name || 'Fatura_IA.pdf'}</h4>
                         <p className="text-[10px] text-gray-400 font-black tracking-widest uppercase">{doc.category || 'Não Classificado'}</p>
                      </div>
                      <span className="font-black text-gray-900 text-[16px] tracking-tight">€{doc.total_amount?.toLocaleString('pt-PT', { minimumFractionDigits: 2 })}</span>
                   </div>
                </div>
              ))}
           </div>
        </section>

        {/* Bottom Cards: Summary and AI Status */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 pt-4">
           <div className="bg-white p-10 rounded-[48px] shadow-sm border border-gray-100 space-y-8 shadow-2xl shadow-gray-200/50 relative overflow-hidden">
              <div className="flex flex-col space-y-1">
                 <h3 className="text-lg font-black text-gray-900">Sumário Semanal</h3>
                 <p className="text-[11px] text-gray-400 font-extrabold uppercase tracking-widest">Análise de Fluxo de Caixa</p>
              </div>
              <div className="space-y-8">
                 <div className="space-y-3">
                    <div className="flex justify-between items-center text-[12px] font-black text-gray-900 uppercase tracking-widest">
                       <div className="flex items-center space-x-3">
                          <div className="p-2.5 bg-green-50 text-green-600 rounded-xl border border-green-100"><MessageCircle size={18} /></div>
                          <span>WhatsApp</span>
                       </div>
                       <span className="text-gray-400 font-black">75%</span>
                    </div>
                    <div className="w-full h-2 bg-gray-50 rounded-full border border-gray-100 overflow-hidden p-0.5 shadow-inner">
                       <div className="h-full bg-green-500 rounded-full shadow-sm" style={{ width: '75%' }} />
                    </div>
                 </div>
                 <div className="space-y-3">
                    <div className="flex justify-between items-center text-[12px] font-black text-gray-900 uppercase tracking-widest">
                       <div className="flex items-center space-x-3">
                          <div className="p-2.5 bg-blue-50 text-blue-600 rounded-xl border border-blue-100"><Mail size={18} /></div>
                          <span>Email Automático</span>
                       </div>
                       <span className="text-gray-400 font-black">45%</span>
                    </div>
                    <div className="w-full h-2 bg-gray-50 rounded-full border border-gray-100 overflow-hidden p-0.5 shadow-inner">
                       <div className="h-full bg-blue-500 rounded-full shadow-sm" style={{ width: '45%' }} />
                    </div>
                 </div>
              </div>
           </div>

           <div className="bg-blue-600 p-10 rounded-[48px] shadow-xl shadow-blue-500/30 flex flex-col justify-between relative overflow-hidden group">
              <div className="space-y-6 relative z-10">
                 <div className="space-y-2">
                    <h3 className="text-[11px] font-black text-white/50 uppercase tracking-[0.2em]">Sustentacódigo Agente</h3>
                    <h2 className="text-3xl font-black text-white leading-tight">O seu agente IA está pronto para processar.</h2>
                 </div>
                 <div className="flex space-x-3">
                    <div className="flex items-center space-x-2 px-4 py-2 bg-white/10 text-white rounded-full text-[10px] font-black border border-white/10 backdrop-blur-md">
                       <div className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse shadow-lg shadow-green-400/50" />
                       <span className="uppercase tracking-widest">OCR Ativo</span>
                    </div>
                    <div className="flex items-center space-x-2 px-4 py-2 bg-white/10 text-white rounded-full text-[10px] font-black border border-white/10 backdrop-blur-md">
                       <div className="w-1.5 h-1.5 bg-blue-300 rounded-full shadow-lg shadow-blue-300/50" />
                       <span className="uppercase tracking-widest">Sinc. Nuvem</span>
                    </div>
                 </div>
              </div>
              
              <button className="mt-12 bg-white text-blue-600 p-6 py-4 rounded-3xl shadow-2xl flex items-center justify-center space-x-4 font-black uppercase text-xs tracking-[0.1em] transition-all transform active:scale-95 z-10 group-hover:bg-blue-50 duration-300">
                 <Plus size={20} strokeWidth={3} />
                 <span>Nova Recolha Manual</span>
              </button>
              
              <div className="absolute right-[-40px] bottom-[-40px] opacity-10 group-hover:opacity-20 transition-opacity duration-1000 rotate-12">
                 <Zap size={280} color="white" fill="white" />
              </div>
           </div>
        </div>
      </div>
    </LayoutBase>
  );
};

const SkeletonCard = () => (
  <div className="bg-white p-6 rounded-[40px] border border-gray-100 space-y-6 flex flex-col items-center">
    <div className="w-full aspect-[3/4] bg-gray-50 rounded-[32px] animate-pulse" />
    <div className="w-3/4 h-4 bg-gray-50 rounded-full animate-pulse" />
    <div className="w-1/2 h-3 bg-gray-50 rounded-full animate-pulse" />
  </div>
);

export default Dashboard;

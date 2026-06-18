import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { 
  Building, 
  ArrowRight,
  ShieldCheck,
  AlertCircle,
  MinusCircle,
  PlusCircle,
  FileCheck,
  X,
  Loader2
} from 'lucide-react';
import LayoutBase from '../components/LayoutBase';

const ReconciliacaoBancaria: React.FC = () => {
  const [bankTransactions, setBankTransactions] = useState<any[]>([]);
  const [aiSuggestions, setAiSuggestions] = useState<any[]>([]);
  const [overdueInvoices, setOverdueInvoices] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchReconciliationData = async () => {
    try {
      const [txRes, sugRes, overdueRes] = await Promise.all([
        api.get('/reconciliation/transactions'),
        api.get('/reconciliation/suggestions'),
        api.get('/invoices?status=overdue')
      ]);
      
      setBankTransactions(txRes.data);
      setAiSuggestions(sugRes.data);
      setOverdueInvoices(overdueRes.data?.data || []);
    } catch (error) {
      console.error("Erro ao carregar dados de reconciliação:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReconciliationData();
  }, []);

  const handleApproveSuggestion = async (transactionId: string, invoiceId: string) => {
    try {
      await api.post(`/reconciliation/match/${transactionId}/${invoiceId}`, {});
      // Refresh data
      fetchReconciliationData();
    } catch (error) {
      alert("Falha ao aprovar reconciliação.");
    }
  };

  return (
    <LayoutBase>
      <div className="flex h-full bg-[#f3f4f6] text-gray-900">
        {/* Panel Left: Split into two columns: Bank Transactions and Overdue Invoices */}
        <div className="flex-1 grid grid-cols-2 gap-0 border-r border-gray-200">
           
           {/* Extrato Bancário */}
           <div className="p-10 space-y-10 border-r border-gray-100 overflow-y-auto no-scrollbar">
              <div className="flex items-center justify-between">
                 <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 bg-white rounded-2xl flex items-center justify-center p-2 shadow-sm border border-gray-100">
                       <Building size={24} className="text-blue-500" />
                    </div>
                    <div className="space-y-1">
                       <h2 className="text-xl font-black tracking-tight text-gray-900">Extrato Bancário</h2>
                       <p className="text-gray-500 text-[11px] font-medium">BPI Prime Empresa</p>
                    </div>
                 </div>
              </div>

              {loading ? (
                <div className="flex justify-center py-20"><Loader2 className="animate-spin text-blue-500" size={32} /></div>
              ) : (
                <div className="space-y-4">
                   {bankTransactions.map((tx) => (
                     <div key={tx.id} className={`flex items-center p-4 rounded-[24px] border border-gray-100 bg-white hover:bg-gray-50 transition-all group shadow-sm ${tx.isReconciled ? 'opacity-50 grayscale-0' : 'border-blue-500/10'}`}>
                        <div className="w-10 h-10 rounded-[14px] bg-gray-50 flex items-center justify-center text-red-500/70 group-hover:bg-red-500 group-hover:text-white transition-all">
                           <MinusCircle size={20} />
                        </div>
                        <div className="flex-1 ml-4">
                           <h4 className="font-bold text-[13px] text-gray-900">{tx.description || "Transação sem nome"}</h4>
                           <p className="text-[10px] text-gray-500 font-bold uppercase">{new Date(tx.paymentDate).toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' })}</p>
                        </div>
                        <div className="text-right">
                           <p className="font-black text-[14px] text-gray-900">{Number(tx.amount).toLocaleString('pt-BR', { style: 'currency', currency: 'EUR' })}</p>
                           {tx.isReconciled && (
                             <div className="flex items-center justify-end space-x-1 mt-1">
                                <ShieldCheck size={10} className="text-green-500" />
                                <span className="text-[9px] font-extrabold text-green-500 uppercase tracking-widest">Reconciliado</span>
                             </div>
                           )}
                        </div>
                     </div>
                   ))}
                </div>
              )}
           </div>

           {/* Faturas Vencidas */}
           <div className="p-10 space-y-10 overflow-y-auto no-scrollbar bg-[#f8fafc]">
              <div className="flex items-center justify-between">
                 <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 bg-white rounded-2xl flex items-center justify-center p-2 shadow-sm border border-gray-100">
                       <FileCheck size={24} className="text-red-500" />
                    </div>
                    <div className="space-y-1">
                       <h2 className="text-xl font-black tracking-tight text-gray-900">Faturas Pendentes</h2>
                       <p className="text-gray-500 text-[11px] font-medium">Aguardando reconciliação</p>
                    </div>
                 </div>
              </div>

              {loading ? (
                <div className="flex justify-center py-20"><Loader2 className="animate-spin text-red-500" size={32} /></div>
              ) : (
                <div className="space-y-4">
                   {overdueInvoices.map((inv) => (
                     <div key={inv.id} className="flex items-center p-4 rounded-[24px] border border-red-500/10 bg-white hover:bg-red-50/50 transition-all shadow-sm">
                        <div className="w-10 h-10 rounded-[14px] bg-red-50 flex items-center justify-center text-red-500">
                           <AlertCircle size={20} />
                        </div>
                        <div className="flex-1 ml-4">
                           <h4 className="font-bold text-[13px] text-gray-900">{inv.vendor_name}</h4>
                           <p className="text-[10px] text-red-500 font-bold uppercase">Vencida em: {new Date(inv.due_date).toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' })}</p>
                        </div>
                        <div className="text-right">
                           <p className="font-black text-[14px] text-gray-900">{Number(inv.total_amount).toLocaleString('pt-BR', { style: 'currency', currency: 'EUR' })}</p>
                           <p className="text-[10px] text-gray-400 font-bold uppercase">{inv.invoice_number}</p>
                        </div>
                     </div>
                   ))}
                   {overdueInvoices.length === 0 && (
                     <div className="py-20 text-center opacity-30">
                        <p className="font-bold text-gray-400">Nenhuma fatura vencida</p>
                     </div>
                   )}
                </div>
              )}
           </div>

        </div>

        {/* Sugestões IA View */}
        <div className="w-[500px] bg-white p-10 flex flex-col space-y-10 overflow-y-auto no-scrollbar shadow-xl z-10 border-l border-gray-100">
           <div className="space-y-2">
              <h3 className="text-sm font-extrabold text-gray-500 uppercase tracking-widest flex items-center space-x-2">
                 <FileCheck size={16} className="text-blue-500" />
                 <span>Sugestões IA</span>
              </h3>
              <p className="text-xs text-gray-500 leading-relaxed font-medium">O Agente cruzou dados de OCR com o seu extrato.</p>
           </div>

           <div className="space-y-6 flex-1">
              {!loading && aiSuggestions.map((sug) => {
                return (
                  <div key={sug.id} className="relative group">
                     <div className="absolute -left-12 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <ArrowRight size={32} className="text-blue-500" />
                     </div>
                     <div className="p-8 rounded-[40px] bg-gray-50/50 border border-gray-100 hover:border-blue-500/30 transition-all space-y-6">
                        <div className="flex justify-between items-start">
                           <div className="space-y-1">
                              <span className="text-[9px] font-black uppercase tracking-widest px-2 py-0.5 bg-blue-500 text-white rounded-md">Confiança {Math.round(sug.confidence * 100)}%</span>
                              <h4 className="font-black text-lg pt-1 text-gray-900">{sug.vendorName}</h4>
                           </div>
                           <PlusCircle size={24} className="text-blue-500/50" />
                        </div>
                        
                        <div className="bg-white rounded-2xl p-4 flex items-center space-x-3 border border-gray-100 border-dashed">
                           <div className="p-2 bg-blue-500/10 text-blue-500 rounded-lg"><FileCheck size={20} /></div>
                           <div className="flex-1">
                              <p className="text-xs font-bold text-gray-700 truncate">{sug.documentName}</p>
                              <p className="text-[10px] text-gray-400 font-extrabold uppercase">Fatura Associada</p>
                           </div>
                        </div>

                        <div className="flex space-x-3">
                           <button 
                             onClick={() => handleApproveSuggestion(sug.transactionId, sug.invoiceId)}
                             className="flex-1 py-3.5 bg-blue-600 hover:bg-blue-500 text-white rounded-2xl text-[12px] font-black shadow-xl shadow-blue-500/20 active:scale-95 transition-all"
                           >
                             Aprovar Sugestão
                           </button>
                           <button className="w-14 py-3.5 bg-white border border-gray-200 text-gray-400 hover:bg-gray-50 rounded-2xl flex items-center justify-center active:scale-95 transition-all shadow-sm"><X size={20} /></button>
                        </div>
                     </div>
                  </div>
                );
              })}

              {!loading && aiSuggestions.length === 0 && (
                 <div className="py-20 text-center opacity-30">
                    <p className="font-bold text-gray-400">Sem sugestões no momento</p>
                 </div>
              )}

              <div className="p-8 rounded-[40px] border border-dashed border-gray-200 flex flex-col items-center justify-center text-center space-y-4 opacity-50 hover:opacity-100 transition-opacity cursor-pointer bg-white">
                 <div className="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center border border-gray-100"><PlusCircle size={32} className="text-gray-300" /></div>
                 <div className="space-y-1">
                    <p className="font-black text-sm text-gray-900">Adicionar Correspondência</p>
                    <p className="text-[11px] text-gray-400 font-medium">Selecione uma fatura manualmente</p>
                 </div>
              </div>
           </div>
        </div>
      </div>
    </LayoutBase>
  );
};

export default ReconciliacaoBancaria;

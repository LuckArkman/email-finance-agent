import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Building, 
  Search, 
  ArrowRight,
  ShieldCheck,
  MoreVertical,
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
  const [loading, setLoading] = useState(true);

  const fetchReconciliationData = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      
      const [txRes, sugRes] = await Promise.all([
        axios.get('/api/v1/reconciliation/transactions', { headers }),
        axios.get('/api/v1/reconciliation/suggestions', { headers })
      ]);
      
      setBankTransactions(txRes.data);
      setAiSuggestions(sugRes.data);
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
      const token = localStorage.getItem('token');
      await axios.post(`/api/v1/reconciliation/match/${transactionId}/${invoiceId}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      // Refresh data
      fetchReconciliationData();
    } catch (error) {
      alert("Falha ao aprovar reconciliação.");
    }
  };

  return (
    <LayoutBase>
      <div className="flex h-full bg-[#f3f4f6] text-gray-900">
        {/* Extrato Bancário View */}
        <div className="flex-1 p-10 space-y-10 border-r border-gray-200 overflow-y-auto no-scrollbar">
           <div className="flex items-center justify-between">
              <div className="flex items-center space-x-6">
                 <div className="w-14 h-14 bg-white rounded-2xl flex items-center justify-center p-3 shadow-sm border border-gray-100">
                    <Building size={32} className="text-blue-500" />
                 </div>
                 <div className="space-y-1">
                    <h2 className="text-2xl font-black tracking-tight text-gray-900">Extrato Bancário Digital</h2>
                    <p className="text-gray-500 text-[13px] font-medium">BPI Prime Empresa • **** 4920</p>
                 </div>
              </div>
              <div className="flex space-x-2">
                 <button className="p-3 bg-white hover:bg-gray-50 rounded-2xl border border-gray-200 shadow-sm"><Search size={20} className="text-gray-400" /></button>
                 <button className="p-3 bg-white hover:bg-gray-50 rounded-2xl border border-gray-200 shadow-sm"><MoreVertical size={20} className="text-gray-400" /></button>
              </div>
           </div>

           {loading ? (
             <div className="flex justify-center py-20"><Loader2 className="animate-spin text-blue-500" size={48} /></div>
           ) : (
             <div className="space-y-4">
                {bankTransactions.map((tx) => (
                  <div key={tx.id} className={`flex items-center p-6 rounded-[32px] border border-gray-100 bg-white hover:bg-gray-50 transition-all group shadow-sm ${tx.is_reconciled ? 'opacity-50 grayscale-0' : 'border-blue-500/10'}`}>
                     <div className="w-12 h-12 rounded-[18px] bg-gray-50 flex items-center justify-center text-red-500/70 group-hover:bg-red-500 group-hover:text-white transition-all">
                        <MinusCircle size={24} />
                     </div>
                     <div className="flex-1 ml-6">
                        <h4 className="font-bold text-[14px] text-gray-900">{tx.description || "Transação sem nome"}</h4>
                        <p className="text-[11px] text-gray-500 font-bold tracking-widest uppercase">{new Date(tx.payment_date).toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' })}</p>
                     </div>
                     <div className="text-right">
                        <p className="font-black text-[16px] text-gray-900">{Number(tx.amount).toLocaleString('pt-BR', { style: 'currency', currency: 'EUR' })}</p>
                        {tx.is_reconciled && (
                          <div className="flex items-center justify-end space-x-1 mt-1">
                             <ShieldCheck size={12} className="text-green-500" />
                             <span className="text-[10px] font-extrabold text-green-500 uppercase tracking-widest">Reconciliado</span>
                          </div>
                        )}
                     </div>
                  </div>
                ))}
             </div>
           )}
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
                              <h4 className="font-black text-lg pt-1 text-gray-900">{sug.vendor_name}</h4>
                           </div>
                           <PlusCircle size={24} className="text-blue-500/50" />
                        </div>
                        
                        <div className="bg-white rounded-2xl p-4 flex items-center space-x-3 border border-gray-100 border-dashed">
                           <div className="p-2 bg-blue-500/10 text-blue-500 rounded-lg"><FileCheck size={20} /></div>
                           <div className="flex-1">
                              <p className="text-xs font-bold text-gray-700 truncate">{sug.document_name}</p>
                              <p className="text-[10px] text-gray-400 font-extrabold uppercase">Fatura Associada</p>
                           </div>
                        </div>

                        <div className="flex space-x-3">
                           <button 
                             onClick={() => handleApproveSuggestion(sug.transaction_id, sug.invoice_id)}
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

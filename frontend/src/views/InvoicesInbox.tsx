import React, { useEffect, useState } from 'react';
import { 
  useReactTable, 
  getCoreRowModel, 
  flexRender, 
  createColumnHelper,
  getPaginationRowModel
} from '@tanstack/react-table';
import { 
  FileText,
  CheckCircle2, 
  AlertCircle, 
  Filter,
  MoreVertical,
  X,
  Plus,
  Upload,
  Loader2,
  Check
} from 'lucide-react';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import LayoutBase from '../components/LayoutBase';
import api from '../services/api';

interface Invoice {
  id: string;
  vendor_name: string;
  total_amount: number;
  issue_date: string;
  category: string;
  status: 'pending' | 'paid' | 'overdue' | 'review_required';
  confidence_score: number;
  filename: string;
  invoice_number?: string;
  raw_document_url?: string;
}

const columnHelper = createColumnHelper<Invoice>();

const columns = [
  columnHelper.accessor('filename', {
    header: 'Nome',
    cell: info => (
      <div className="flex items-center space-x-3">
         <div className="p-2 bg-red-50 text-red-500 rounded-lg">
            <FileText size={18} />
         </div>
         <span className="font-bold text-gray-900 text-[13px] truncate max-w-[200px]">{info.getValue() || 'Fatura_Digital.pdf'}</span>
      </div>
    ),
  }),
  columnHelper.accessor('issue_date', {
    header: 'Data Emissão',
    cell: info => <span className="text-gray-500 text-[13px]">{info.getValue() ? format(new Date(info.getValue()), 'dd MMM yyyy', { locale: ptBR }) : '---'}</span>,
  }),
  columnHelper.accessor('total_amount', {
    header: 'Valor',
    cell: info => <span className="text-gray-900 font-extrabold text-[13px]">€{info.getValue()?.toLocaleString('pt-PT', { minimumFractionDigits: 2 })}</span>,
  }),
  columnHelper.accessor('category', {
    header: 'Categoria',
    cell: info => <span className="text-gray-500 text-[13px]">{info.getValue() || 'Não Definido'}</span>,
  }),
  columnHelper.accessor('status', {
    header: 'Status AI',
    cell: info => {
      const isOk = (info.row.original.confidence_score || 0) >= 0.8;
      return (
        <div className="flex items-center">
           {isOk ? (
             <div className="w-6 h-6 rounded-full bg-green-100 flex items-center justify-center text-green-600 border border-green-200 shadow-sm">
                <CheckCircle2 size={12} />
             </div>
           ) : (
             <div className="w-6 h-6 rounded-full bg-orange-100 flex items-center justify-center text-orange-600 border border-orange-200 shadow-sm">
                <AlertCircle size={12} />
             </div>
           )}
        </div>
      );
    },
  }),
  columnHelper.display({
    id: 'actions',
    cell: () => <MoreVertical size={16} className="text-gray-300 cursor-pointer" />,
  }),
];

const InvoicesInboxView: React.FC = () => {
  const [data, setData] = useState<Invoice[]>([]);
  const [selectedInvoice, setSelectedInvoice] = useState<Invoice | null>(null);
  const [loading, setLoading] = useState(true);
  
  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const fetchInvoices = async () => {
    setLoading(true);
    try {
      const res = await api.get('/invoices');
      // Backend returns { data: [...], total: ... }
      setData(res.data.data || []);
    } catch (err) {
      console.error('Failed to fetch invoices', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInvoices();
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setUploadProgress(20);
    
    const formData = new FormData();
    formData.append('file', file);

    try {
      setUploadProgress(50);
      await api.post('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setUploadProgress(100);
      setIsModalOpen(false);
      fetchInvoices();
    } catch (err) {
      alert('Erro ao carregar ficheiro');
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
  });

  return (
    <LayoutBase>
      <div className="flex h-full overflow-hidden bg-[#f3f4f6]">
        {/* Main Content List */}
        <div className={`flex-1 transition-all duration-300 p-8 flex flex-col space-y-8 ${selectedInvoice ? 'mr-0' : ''}`}>
           <div className="flex items-center justify-between">
              <div className="space-y-1">
                 <h2 className="text-2xl font-black text-gray-900 tracking-tight">Arquivo Digital</h2>
                 <p className="text-gray-400 text-xs font-bold uppercase tracking-widest">Base de Dados Centralizada</p>
              </div>
              <div className="flex items-center space-x-3">
                 <button className="flex items-center space-x-2 px-5 p-3 bg-white border border-gray-200 rounded-2xl text-[13px] font-black shadow-sm text-gray-500 hover:border-gray-300 transition-all"><Filter size={16} /> <span>Filtros</span></button>
                 <button 
                  onClick={() => setIsModalOpen(true)}
                  className="flex items-center space-x-2 px-5 p-3 bg-blue-600 text-white rounded-2xl text-[13px] font-black shadow-xl shadow-blue-500/20 hover:bg-blue-700 active:scale-95 transition-all"
                 >
                   <Plus size={16} /> <span>Adicionar</span>
                 </button>
              </div>
           </div>

           {/* Table */}
           <div className="bg-white rounded-[40px] shadow-sm border border-gray-100 overflow-hidden flex-1 flex flex-col shadow-2xl shadow-gray-200/50">
              {loading && data.length === 0 ? (
                <div className="flex-1 flex flex-col items-center justify-center space-y-4">
                   <Loader2 size={40} className="animate-spin text-blue-500" />
                   <p className="text-gray-400 font-bold uppercase tracking-widest text-[10px]">A carregar arquivo...</p>
                </div>
              ) : (
                <div className="overflow-auto no-scrollbar">
                  <table className="w-full text-left border-collapse">
                    <thead className="sticky top-0 bg-gray-50/50 z-10 backdrop-blur-md">
                      {table.getHeaderGroups().map(hg => (
                        <tr key={hg.id} className="border-b border-gray-100">
                           {hg.headers.map(header => (
                             <th key={header.id} className="px-6 py-6 text-[10px] font-black text-gray-400 uppercase tracking-widest border-r border-gray-50/50">
                                {flexRender(header.column.columnDef.header, header.getContext())}
                             </th>
                           ))}
                        </tr>
                      ))}
                    </thead>
                    <tbody className="divide-y divide-gray-50">
                      {table.getRowModel().rows.map(row => (
                        <tr 
                          key={row.id} 
                          onClick={() => setSelectedInvoice(row.original)}
                          className={`hover:bg-gray-50/50 transition-all cursor-pointer group ${selectedInvoice?.id === row.original.id ? 'bg-blue-50/30' : ''}`}
                        >
                           {row.getVisibleCells().map(cell => (
                             <td key={cell.id} className="px-6 py-5 border-r border-gray-50/50 group-last:border-r-0">
                                {flexRender(cell.column.columnDef.cell, cell.getContext())}
                             </td>
                           ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
           </div>
        </div>

        {/* AI Extraction Sidebar Preview */}
        {selectedInvoice && (
          <div className="w-[450px] border-l border-gray-100 bg-white h-full animate-slide-in shadow-2xl z-20 overflow-hidden flex flex-col">
             <div className="p-8 h-full flex flex-col space-y-10">
                <div className="flex items-center justify-between">
                   <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center border border-blue-100">
                         <FileText size={20} />
                      </div>
                      <h3 className="font-black text-gray-900 text-lg">Revisão IA</h3>
                   </div>
                   <button onClick={() => setSelectedInvoice(null)} className="p-2.5 hover:bg-gray-50 border border-gray-100 rounded-xl text-gray-400 transition-all"><X size={20} /></button>
                </div>

                <div className="flex-1 overflow-y-auto no-scrollbar space-y-10">
                   <div className="space-y-4">
                      <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest pl-1">Documento Original</p>
                      <div className="w-full aspect-[3/4] bg-gray-50 rounded-[32px] border border-gray-100 flex flex-col items-center justify-center p-10 relative overflow-hidden group shadow-inner">
                         <div className="bg-white p-6 shadow-2xl border border-gray-100 rounded-2xl transform transition-transform group-hover:scale-105 duration-500">
                            <FileText size={80} className="text-gray-100" />
                         </div>
                         <div className="mt-8 text-center space-y-1">
                            <p className="font-black text-gray-900 text-sm">{selectedInvoice.filename || 'Fatura_Digital.pdf'}</p>
                            <button className="text-[10px] text-blue-500 underline font-black uppercase tracking-widest mt-1">Ver PDF Completo</button>
                         </div>
                      </div>
                   </div>

                   <div className="space-y-6">
                      <div className="flex justify-between items-center px-1">
                         <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest">Extração Automática</p>
                         <span className="text-[10px] font-black text-green-500 bg-green-50 px-2 py-0.5 rounded-md border border-green-100">Sincronizado</span>
                      </div>
                      <div className="space-y-6 bg-gray-50/50 p-6 rounded-[32px] border border-gray-100">
                         <DetailField label="Entidade Fornecedora" value={selectedInvoice.vendor_name || '---'} isConfirmed />
                         <DetailField label="Nº Fatura / Referência" value={selectedInvoice.invoice_number || 'EXT-39402-A'} />
                         <DetailField label="Data de Emissão" value={selectedInvoice.issue_date ? format(new Date(selectedInvoice.issue_date), 'dd MMMM yyyy', { locale: ptBR }) : '---'} />
                         <DetailField label="Valor Total (S/ Iva)" value={`€${selectedInvoice.total_amount?.toLocaleString('pt-PT', { minimumFractionDigits: 2 })}`} />
                         
                         <div className="space-y-3 pt-4 border-t border-gray-100">
                            <div className="flex justify-between text-[10px] font-black text-gray-400 uppercase tracking-widest overflow-visible">
                               <span>Confiança no Reconhecimento</span>
                               <span className="text-blue-500">{( (selectedInvoice.confidence_score || 0) * 100).toFixed(0)}%</span>
                            </div>
                            <div className="w-full h-1.5 bg-gray-100 rounded-full overflow-hidden">
                               <div 
                                 className={`h-full transition-all duration-1000 ${selectedInvoice.confidence_score > 0.8 ? 'bg-blue-500' : 'bg-orange-400'}`} 
                                 style={{ width: `${(selectedInvoice.confidence_score || 0) * 100}%` }} 
                               />
                            </div>
                         </div>
                      </div>
                   </div>
                </div>

                <div className="pt-8 border-t border-gray-50 flex flex-col space-y-3 mt-auto">
                   <button className="w-full py-5 bg-blue-600 text-white rounded-[24px] font-black text-xs uppercase tracking-widest shadow-xl shadow-blue-500/20 hover:bg-blue-700 active:scale-95 transition-all flex items-center justify-center space-x-2">
                     <Check size={16} strokeWidth={3} />
                     <span>Confirmar e Validar</span>
                   </button>
                   <button onClick={() => setSelectedInvoice(null)} className="w-full py-5 bg-white text-gray-400 border border-gray-200 rounded-[24px] font-black text-xs uppercase tracking-widest hover:bg-gray-50 active:scale-95 transition-all">Fechar Pré-visualização</button>
                </div>
             </div>
          </div>
        )}
      </div>

      {/* Upload Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-6 bg-gray-900/40 backdrop-blur-sm animate-fade-in">
           <div className="bg-white w-full max-w-md rounded-[48px] p-10 shadow-2xl border border-gray-100 relative space-y-8">
              <button 
                onClick={() => setIsModalOpen(false)}
                className="absolute right-8 top-8 text-gray-300 hover:text-gray-900 transition-colors"
                disabled={isUploading}
              >
                 <X size={24} />
              </button>

              <div className="text-center space-y-2">
                 <div className="w-16 h-16 bg-blue-50 text-blue-600 rounded-[24px] flex items-center justify-center mx-auto mb-4">
                    <Upload size={32} />
                 </div>
                 <h3 className="text-xl font-black text-gray-900">Upload de Faturas</h3>
                 <p className="text-gray-400 text-sm font-medium">Carregue ficheiros PDF, JPG ou PNG para processamento</p>
              </div>

              {isUploading ? (
                <div className="space-y-6 pt-4 animate-fade-in">
                   <div className="flex justify-between text-[11px] font-black text-gray-400 uppercase tracking-widest">
                      <span>A extrair dados...</span>
                      <span>{uploadProgress}%</span>
                   </div>
                   <div className="w-full h-3 bg-gray-50 rounded-full border border-gray-100 overflow-hidden p-0.5">
                      <div className="h-full bg-blue-500 rounded-full transition-all duration-300 shadow-sm" style={{ width: `${uploadProgress}%` }} />
                   </div>
                   <p className="text-center text-[11px] text-gray-400 animate-pulse">Este processo demora alguns segundos dependendo da complexidade.</p>
                </div>
              ) : (
                <label className="flex flex-col items-center justify-center w-full h-48 border-2 border-dashed border-gray-200 rounded-[32px] cursor-pointer hover:bg-blue-50 hover:border-blue-200 transition-all space-y-3 group">
                   <div className="w-12 h-12 bg-white rounded-2xl flex items-center justify-center shadow-sm group-hover:scale-110 transition-transform">
                      <Plus size={24} className="text-gray-300 group-hover:text-blue-500" />
                   </div>
                   <div className="text-center">
                      <p className="text-[13px] font-black text-gray-900">Clique ou arraste o ficheiro</p>
                      <p className="text-[11px] text-gray-400 uppercase tracking-widest font-black mt-1">PDF, PNG, JPG (Máx 10MB)</p>
                   </div>
                   <input type="file" className="hidden" onChange={handleFileUpload} accept=".pdf,.png,.jpg,.jpeg" />
                </label>
              )}
           </div>
        </div>
      )}
    </LayoutBase>
  );
};

const DetailField = ({ label, value, isConfirmed }: { label: string; value: string; isConfirmed?: boolean }) => (
  <div className="flex flex-col space-y-1.5">
     <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest pl-0.5">{label}</span>
     <div className="flex items-center justify-between group bg-white border border-gray-100 p-3.5 rounded-2xl shadow-sm transition-all hover:border-blue-500/20">
        <span className="text-[13px] font-bold text-gray-900">{value}</span>
        {isConfirmed ? (
          <CheckCircle2 size={14} className="text-green-500 shrink-0" />
        ) : (
          <ArrowRight size={14} className="text-gray-200 group-hover:text-blue-400 transition-colors shrink-0" />
        )}
     </div>
  </div>
);

const ArrowRight = ({ size, className }: { size: number; className?: string }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M5 12h14M12 5l7 7-7 7"/>
  </svg>
);

export default InvoicesInboxView;

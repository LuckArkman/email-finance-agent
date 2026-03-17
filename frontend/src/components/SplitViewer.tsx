import React, { useState } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  X, 
  ChevronLeft, 
  ChevronRight, 
  ZoomIn, 
  ZoomOut, 
  Save, 
  CheckCircle2, 
  AlertCircle,
  FileText
} from 'lucide-react';

// Setup PDF worker
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

interface SplitViewerProps {
  isOpen: boolean;
  onClose: () => void;
  invoiceData: any;
  pdfUrl: string;
}

const SplitViewer: React.FC<SplitViewerProps> = ({ isOpen, onClose, invoiceData, pdfUrl }) => {
  const [numPages, setNumPages] = useState<number>(0);
  const [pageNumber, setPageNumber] = useState(1);
  const [scale, setScale] = useState(1.0);
  const [formData] = useState(invoiceData);

  const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages);
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
      >
        <motion.div 
          initial={{ scale: 0.95, y: 20 }}
          animate={{ scale: 1, y: 0 }}
          className="bg-[#0d1117] w-full h-full max-w-[1600px] rounded-[32px] overflow-hidden border border-white/10 flex flex-col shadow-2xl"
        >
          {/* Header */}
          <div className="h-20 px-8 border-b border-white/10 flex items-center justify-between bg-white/[0.02]">
            <div className="flex items-center space-x-4">
              <div className="p-3 rounded-2xl bg-blue-600/10 text-blue-500">
                <FileText size={24} />
              </div>
              <div>
                <h2 className="text-xl font-bold text-white">Document Audit View</h2>
                <p className="text-xs text-gray-500">Invoice ID: {invoiceData?.id || 'PRO-2024-001'}</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <button className="flex items-center space-x-2 px-6 py-2.5 bg-green-600 hover:bg-green-500 text-white rounded-xl font-bold transition-all shadow-lg shadow-green-600/20 active:scale-95">
                <CheckCircle2 size={18} />
                <span>Approve Extraction</span>
              </button>
              <button 
                onClick={onClose}
                className="p-3 rounded-xl bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
              >
                <X size={24} />
              </button>
            </div>
          </div>

          {/* Main Context Split */}
          <div className="flex-1 flex overflow-hidden">
            
            {/* Left Side: PDF Viewer */}
            <div className="flex-1 bg-[#161b22] relative overflow-hidden flex flex-col border-r border-white/10">
              {/* PDF Toolbar */}
              <div className="h-12 px-4 flex items-center justify-between border-b border-white/5 bg-black/20">
                <div className="flex items-center space-x-2 text-xs text-gray-400">
                  <button 
                    disabled={pageNumber <= 1}
                    onClick={() => setPageNumber(prev => prev - 1)}
                    className="p-1 hover:text-white disabled:opacity-30"
                  >
                    <ChevronLeft size={16} />
                  </button>
                  <span>Page {pageNumber} of {numPages || '--'}</span>
                  <button 
                    disabled={pageNumber >= numPages}
                    onClick={() => setPageNumber(prev => prev + 1)}
                    className="p-1 hover:text-white disabled:opacity-30"
                  >
                    <ChevronRight size={16} />
                  </button>
                </div>
                <div className="flex items-center space-x-4">
                  <button onClick={() => setScale(s => s - 0.1)} className="p-1 text-gray-400 hover:text-white"><ZoomOut size={16} /></button>
                  <span className="text-[10px] text-gray-500">{(scale * 100).toFixed(0)}%</span>
                  <button onClick={() => setScale(s => s + 0.1)} className="p-1 text-gray-400 hover:text-white"><ZoomIn size={16} /></button>
                </div>
              </div>

              {/* PDF Canvas Container */}
              <div className="flex-1 overflow-auto p-8 flex justify-center scrollbar-hide">
                <div className="shadow-2xl rounded-lg overflow-hidden bg-white">
                  <Document
                    file={pdfUrl}
                    onLoadSuccess={onDocumentLoadSuccess}
                    loading={
                      <div className="w-[600px] h-[800px] flex items-center justify-center text-gray-500 italic">
                        Initializing PDF Engine...
                      </div>
                    }
                  >
                    <Page 
                      pageNumber={pageNumber} 
                      scale={scale} 
                      renderTextLayer={false}
                      renderAnnotationLayer={false}
                    />
                  </Document>
                </div>
              </div>
            </div>

            {/* Right Side: Extraction Form */}
            <div className="w-[480px] bg-[#0d1117] flex flex-col animate-fade-in overflow-y-auto p-8 space-y-8">
               <div>
                  <h3 className="text-sm font-bold text-gray-500 uppercase tracking-widest mb-6 flex items-center gap-2">
                    <AlertCircle size={14} className="text-blue-500" />
                    AI Intelligence Extraction
                  </h3>
                  
                  <div className="space-y-6">
                    {/* Form Fields */}
                    {[
                      { label: 'Vendor Name', key: 'vendor_name', value: formData.vendor_name },
                      { label: 'Invoice Number', key: 'invoice_number', value: formData.invoice_number || 'INV-9921' },
                      { label: 'Issue Date', key: 'issue_date', value: formData.issue_date },
                      { label: 'Total Amount', key: 'total_amount', value: `$ ${formData.total_amount?.toFixed(2)}` },
                    ].map((field) => (
                      <div key={field.key} className="space-y-2 group">
                        <label className="text-xs font-medium text-gray-400 ml-1">{field.label}</label>
                        <div className="relative">
                          <input 
                            type="text" 
                            defaultValue={field.value}
                            className="w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-4 text-white outline-none focus:border-blue-500/50 focus:ring-4 focus:ring-blue-500/10 transition-all font-medium"
                          />
                          <div className="absolute right-4 top-1/2 -translate-y-1/2 w-2 h-2 rounded-full bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.5)]"></div>
                        </div>
                      </div>
                    ))}
                  </div>
               </div>

               <div className="pt-6 border-t border-white/10">
                  <h3 className="text-sm font-bold text-gray-500 uppercase tracking-widest mb-4">Confidence Audit</h3>
                  <div className="glass p-6 rounded-3xl border-blue-500/10">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs text-gray-400">LLM Prediction Accuracy</span>
                      <span className="text-sm font-bold text-green-500">98.4%</span>
                    </div>
                    <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden">
                      <div className="h-full bg-green-500 shadow-[0_0_15px_rgba(34,197,94,0.3)]" style={{ width: '98%' }} />
                    </div>
                  </div>
               </div>

               <div className="mt-auto pt-6 flex gap-3">
                  <button className="flex-1 py-4 bg-white/5 hover:bg-white/10 text-white font-bold rounded-2xl transition-all border border-white/10 flex items-center justify-center gap-2">
                    <Save size={18} />
                    <span>Save Draft</span>
                  </button>
               </div>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default SplitViewer;

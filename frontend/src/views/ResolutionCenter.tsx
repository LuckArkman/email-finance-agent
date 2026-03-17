import React, { useState } from 'react';
import { 
  CheckCircle2, 
  AlertTriangle, 
  ArrowRight, 
  ArrowLeft,
} from 'lucide-react';
import api from '../services/api';
import SplitViewer from '../components/SplitViewer';
import { motion, AnimatePresence } from 'framer-motion';

interface HitlWorkQueueItem {
  id: string;
  vendor_name: string;
  total_amount: number;
  confidence_score: number;
  issue_date: string;
  pdf_url: string;
  reason: string;
}

const HitlResolutionCenter: React.FC = () => {
  const [queue, setQueue] = useState<HitlWorkQueueItem[]>([
    { 
      id: 'INV-LO-001', 
      vendor_name: 'Unknwn Suply', 
      total_amount: 890.00, 
      confidence_score: 0.65, 
      issue_date: '2026-03-10',
      pdf_url: 'https://raw.githubusercontent.com/mozilla/pdf.js/ba2edeae/web/compressed.tracemonkey-pldi-09.pdf',
      reason: 'Low OCR confidence on vendor name'
    },
    { 
      id: 'INV-LO-002', 
      vendor_name: 'Total Energy', 
      total_amount: 150.00, 
      confidence_score: 0.45, 
      issue_date: '2026-03-12',
      pdf_url: 'https://raw.githubusercontent.com/mozilla/pdf.js/ba2edeae/web/compressed.tracemonkey-pldi-09.pdf',
      reason: 'Mathematical total mismatch (Subtotal + Tax != Total)'
    }
  ]);
  
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isSuccess, setIsSuccess] = useState(false);

  const currentItem = queue[currentIndex];

  const handleManualApprove = async () => {
    try {
      await api.put(`/invoices/${currentItem.id}`, {
        status: 'processed',
        manual_override: true
      });
      
      setIsSuccess(true);
      setTimeout(() => {
        setIsSuccess(false);
        loadNextInQueue();
      }, 1500);
    } catch (err) {
      console.error("Resolution failed", err);
    }
  };

  const loadNextInQueue = () => {
    if (currentIndex < queue.length - 1) {
      setCurrentIndex(prev => prev + 1);
    } else {
      setQueue([]);
    }
  };

  if (queue.length === 0) {
    return (
      <div className="h-[80vh] flex flex-col items-center justify-center text-center space-y-4">
        <div className="w-20 h-20 bg-green-500/10 text-green-500 rounded-full flex items-center justify-center">
          <CheckCircle2 size={40} />
        </div>
        <h2 className="text-2xl font-bold text-white">All caught up!</h2>
        <p className="text-gray-500 max-w-sm">No more invoices require manual review at this time.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in relative h-full">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-white flex items-center gap-3">
            Resolution Center
            <span className="text-sm bg-blue-600/20 text-blue-500 px-3 py-1 rounded-full border border-blue-500/20">
              {queue.length} Pending
            </span>
          </h2>
          <p className="text-gray-400 mt-1">Resolve AI extraction warnings for low-confidence documents.</p>
        </div>

        <div className="flex items-center space-x-2">
           <button 
            disabled={currentIndex === 0}
            onClick={() => setCurrentIndex(c => c - 1)}
            className="p-3 rounded-xl glass border-white/5 disabled:opacity-30 hover:bg-white/10"
           >
              <ArrowLeft size={20} />
           </button>
           <button 
            disabled={currentIndex === queue.length - 1}
            onClick={() => setCurrentIndex(c => c + 1)}
            className="p-3 rounded-xl glass border-white/5 disabled:opacity-30 hover:bg-white/10"
           >
              <ArrowRight size={20} />
           </button>
        </div>
      </div>

      <div className="bg-yellow-500/10 border border-yellow-500/20 p-4 rounded-2xl flex items-center justify-between gap-3 text-yellow-500 shadow-lg shadow-yellow-500/5">
         <div className="flex items-center gap-3">
            <AlertTriangle size={20} />
            <span className="text-sm font-medium">Issue Detected: <span className="text-white">{currentItem.reason}</span></span>
         </div>
         <button 
          onClick={handleManualApprove}
          className="px-4 py-2 bg-green-600 text-white text-xs font-bold rounded-lg hover:bg-green-500 transition-colors"
         >
           Force Approve
         </button>
      </div>

      <div className="bg-[#0d1117] rounded-[32px] overflow-hidden border border-white/10 h-[calc(100vh-280px)] flex flex-col shadow-2xl">
          <SplitViewer 
            isOpen={true} 
            onClose={() => {}} 
            invoiceData={currentItem} 
            pdfUrl={currentItem.pdf_url}
          />
      </div>

      <AnimatePresence>
        {isSuccess && (
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="fixed bottom-12 right-12 bg-green-600 text-white px-8 py-4 rounded-3xl shadow-2xl flex items-center gap-3 font-bold z-50 border border-green-400/20"
          >
             <CheckCircle2 size={24} />
             <span>Invoice Resolved Successfully!</span>
          </motion.div>
        )}
      </AnimatePresence>

    </div>
  );
};

export default HitlResolutionCenter;

import React, { useEffect, useState, useCallback } from 'react';
import { 
  CheckCircle2, 
  AlertTriangle, 
  ArrowRight, 
  ArrowLeft,
  Loader2,
  FileSearch
} from 'lucide-react';
import api from '../services/api';
import SplitViewer from '../components/SplitViewer';
import { motion, AnimatePresence } from 'framer-motion';
import LayoutBase from '../components/LayoutBase';

interface ReviewItem {
  id: string;
  invoice_id: string;
  vendor_name: string;
  total_amount: number;
  confidence_score: number;
  reason: string;
  created_at: string;
}

const HitlResolutionCenter: React.FC = () => {
  const [queue, setQueue] = useState<ReviewItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isSuccess, setIsSuccess] = useState(false);
  const [resolving, setResolving] = useState(false);

  const fetchQueue = useCallback(async () => {
    setLoading(true);
    try {
      const response = await api.get('/review/queue');
      setQueue(response.data);
    } catch (err) {
      console.error('Failed to fetch review queue', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchQueue();
  }, [fetchQueue]);

  const currentItem = queue[currentIndex];

  const handleResolve = async (action: 'approve' | 'reject') => {
    if (!currentItem) return;
    setResolving(true);
    try {
      await api.post(`/review/resolve/${currentItem.id}`, { action });
      
      setIsSuccess(true);
      setTimeout(() => {
        setIsSuccess(false);
        setQueue(prev => prev.filter((_, i) => i !== currentIndex));
        if (currentIndex >= queue.length - 1 && currentIndex > 0) {
          setCurrentIndex(prev => prev - 1);
        }
        setResolving(false);
      }, 1000);
    } catch (err) {
      console.error("Resolution failed", err);
      setResolving(false);
    }
  };

  if (loading) {
    return (
      <LayoutBase>
        <div className="h-[60vh] flex flex-col items-center justify-center gap-4 text-gray-500">
          <Loader2 className="animate-spin text-blue-500" size={40} />
          <p className="font-medium">Loading Human-in-the-loop Queue...</p>
        </div>
      </LayoutBase>
    );
  }

  if (queue.length === 0) {
    return (
      <LayoutBase>
        <div className="h-[70vh] flex flex-col items-center justify-center text-center space-y-6 animate-fade-in">
          <div className="w-24 h-24 bg-green-500/10 text-green-500 rounded-full flex items-center justify-center shadow-xl shadow-green-500/10">
            <CheckCircle2 size={48} />
          </div>
          <div className="space-y-2">
            <h2 className="text-3xl font-bold text-white">Inbox Zero!</h2>
            <p className="text-gray-400 max-w-sm mx-auto">
              Everything is in order. All automatically processed documents met high confidence requirements.
            </p>
          </div>
        </div>
      </LayoutBase>
    );
  }

  return (
    <LayoutBase>
      <div className="space-y-6 animate-fade-in relative h-[calc(100vh-140px)] flex flex-col overflow-hidden">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold tracking-tight text-white flex items-center gap-3">
              <FileSearch className="text-blue-500" />
              Resolution Center
              <span className="text-sm bg-blue-600/20 text-blue-500 px-3 py-1 rounded-full border border-blue-500/20">
                {queue.length} Pending
              </span>
            </h2>
            <p className="text-gray-400 mt-1">Verify and reconcile AI extraction alerts.</p>
          </div>

          <div className="flex items-center space-x-2">
            <button 
              disabled={currentIndex === 0 || resolving}
              onClick={() => setCurrentIndex(c => c - 1)}
              className="p-3 rounded-xl glass border border-white/5 disabled:opacity-30 hover:bg-white/10 transition-colors"
            >
              <ArrowLeft size={20} />
            </button>
            <span className="text-white font-bold text-sm px-4">
              {currentIndex + 1} / {queue.length}
            </span>
            <button 
              disabled={currentIndex === queue.length - 1 || resolving}
              onClick={() => setCurrentIndex(c => c + 1)}
              className="p-3 rounded-xl glass border border-white/5 disabled:opacity-30 hover:bg-white/10 transition-colors"
            >
              <ArrowRight size={20} />
            </button>
          </div>
        </div>

        <div className="bg-yellow-500/10 border border-yellow-500/20 p-5 rounded-3xl flex items-center justify-between gap-3 text-yellow-500 shadow-xl shadow-yellow-500/5 backdrop-blur-md">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 rounded-full bg-yellow-500/20 flex items-center justify-center">
              <AlertTriangle size={20} />
            </div>
            <div>
              <p className="text-xs text-yellow-500/60 font-bold uppercase tracking-widest">Review Reason</p>
              <p className="text-sm font-bold text-white mt-0.5">{currentItem.reason}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button 
              disabled={resolving}
              onClick={() => handleResolve('reject')}
              className="px-6 py-2.5 bg-red-500/10 hover:bg-red-500/20 text-red-500 text-sm font-bold rounded-xl transition-all border border-red-500/10 disabled:opacity-50"
            >
              Reject
            </button>
            <button 
              disabled={resolving}
              onClick={() => handleResolve('approve')}
              className="px-8 py-2.5 bg-green-600 hover:bg-green-500 text-white text-sm font-bold rounded-xl shadow-lg shadow-green-600/20 transition-all disabled:opacity-50 flex items-center gap-2"
            >
              {resolving ? <Loader2 className="animate-spin" size={18} /> : <CheckCircle2 size={18} />}
              Force Approve
            </button>
          </div>
        </div>

        <div className="bg-[#0b0e14] rounded-[40px] overflow-hidden border border-white/10 flex-1 flex flex-col shadow-2xl">
          <SplitViewer 
            isOpen={true} 
            onClose={() => {}} 
            invoiceData={currentItem} 
            pdfUrl={`https://storage.example.com/mock-invoice-${currentItem.invoice_id}.pdf`}
          />
        </div>

        <AnimatePresence>
          {isSuccess && (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              className="fixed bottom-12 right-12 bg-green-600 text-white px-8 py-4 rounded-3xl shadow-2xl flex items-center gap-4 font-bold z-[100] border border-green-400/20 backdrop-blur-xl"
            >
              <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
                <CheckCircle2 size={20} />
              </div>
              <div className="flex flex-col">
                <span className="text-sm">Resolved Successfully</span>
                <span className="text-[10px] opacity-70 font-medium">Moving to next item...</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </LayoutBase>
  );
};

export default HitlResolutionCenter;

import React, { useEffect, useState } from 'react';
import { 
  ClipboardCheck, 
  XCircle, 
  CheckCircle2, 
  AlertCircle,
  FileText,
  Loader2
} from 'lucide-react';
import api from '../services/api';
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

const ReviewQueue: React.FC = () => {
  const [items, setItems] = useState<ReviewItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [processingId, setProcessingId] = useState<string | null>(null);

  const fetchQueue = async () => {
    setLoading(true);
    try {
      const response = await api.get('/review/queue');
      setItems(response.data);
    } catch (err) {
      console.error('Failed to fetch review queue', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQueue();
  }, []);

  const handleResolve = async (id: string, action: 'approve' | 'reject') => {
    setProcessingId(id);
    try {
      await api.post(`/review/resolve/${id}`, { action });
      setItems(items.filter(item => item.id !== id));
    } catch (err) {
      console.error('Failed to resolve review', err);
    } finally {
      setProcessingId(null);
    }
  };

  return (
    <LayoutBase>
      <div className="space-y-8 animate-fade-in">
        <div className="flex flex-col gap-2">
          <h2 className="text-3xl font-bold tracking-tight text-white flex items-center gap-3">
            <ClipboardCheck className="text-yellow-500" />
            Human-in-the-Loop Review
          </h2>
          <p className="text-gray-400">
            Verify documents where AI confidence was below the 90% threshold to ensure 100% financial accuracy.
          </p>
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 gap-4">
            <Loader2 className="animate-spin text-blue-500" size={40} />
            <p className="text-gray-500 font-medium">Scanning pending reviews...</p>
          </div>
        ) : items.length === 0 ? (
          <div className="glass p-12 rounded-[40px] border border-white/5 flex flex-col items-center justify-center gap-6 text-center">
            <div className="w-20 h-20 rounded-full bg-green-500/10 flex items-center justify-center text-green-500">
              <CheckCircle2 size={40} />
            </div>
            <div>
              <h3 className="text-xl font-bold text-white">Queue Clear!</h3>
              <p className="text-gray-400 mt-2 max-w-md">
                Great job! All automatically processed documents met the high confidence standards.
              </p>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {items.map((item) => (
              <div 
                key={item.id}
                className="glass p-6 rounded-3xl border border-white/5 hover:border-white/10 transition-all group flex flex-col md:flex-row items-center justify-between gap-6"
              >
                <div className="flex items-center gap-6 flex-1">
                  <div className="w-14 h-14 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-gray-400 group-hover:text-blue-500 transition-colors">
                    <FileText size={28} />
                  </div>
                  <div className="space-y-1">
                    <div className="flex items-center gap-3">
                      <h4 className="text-lg font-bold text-white">{item.vendor_name || 'Unknown Vendor'}</h4>
                      <span className="px-3 py-1 rounded-full bg-yellow-500/10 text-yellow-500 text-[10px] font-bold uppercase tracking-widest border border-yellow-500/20">
                        Pending Approval
                      </span>
                    </div>
                    <p className="text-sm text-gray-500 flex items-center gap-2">
                      <AlertCircle size={14} className="text-red-500" />
                      {item.reason}
                    </p>
                    <div className="flex items-center gap-4 text-xs font-medium text-gray-400 pt-2">
                      <span className="flex items-center gap-1">
                        Amount: <strong className="text-white">${item.total_amount?.toLocaleString()}</strong>
                      </span>
                      <span className="flex items-center gap-1">
                        Confidence: <strong className={item.confidence_score < 0.8 ? 'text-red-500' : 'text-yellow-500'}>
                          {(item.confidence_score * 100).toFixed(1)}%
                        </strong>
                      </span>
                      <span>Detected {new Date(item.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3 w-full md:w-auto">
                  <button 
                    onClick={() => handleResolve(item.id, 'reject')}
                    disabled={!!processingId}
                    className="flex-1 md:flex-none flex items-center justify-center gap-2 px-6 py-3 rounded-2xl bg-red-500/10 hover:bg-red-500/20 text-red-500 font-bold border border-red-500/10 transition-all disabled:opacity-50"
                  >
                    <XCircle size={18} />
                    Reject
                  </button>
                  <button 
                    onClick={() => handleResolve(item.id, 'approve')}
                    disabled={!!processingId}
                    className="flex-1 md:flex-none flex items-center justify-center gap-2 px-6 py-3 rounded-2xl bg-green-500 hover:bg-green-600 text-white font-bold shadow-lg shadow-green-500/20 transition-all disabled:opacity-50"
                  >
                    {processingId === item.id ? (
                      <Loader2 className="animate-spin" size={18} />
                    ) : (
                      <CheckCircle2 size={18} />
                    )}
                    Approve
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </LayoutBase>
  );
};

export default ReviewQueue;

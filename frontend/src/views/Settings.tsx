import React, { useState, useEffect } from 'react';
import { 
  Settings as SettingsIcon, 
  Webhook, 
  ShieldCheck, 
  Save, 
  ExternalLink,
  CheckCircle2,
  Lock,
  Zap,
  RefreshCw
} from 'lucide-react';
import api from '../services/api';
import LayoutBase from '../components/LayoutBase';
import { motion, AnimatePresence } from 'framer-motion';

const SettingsView: React.FC = () => {
  const [webhookUrl, setWebhookUrl] = useState('');
  const [secretKey, setSecretKey] = useState('');
  const [isActive, setIsActive] = useState(true);
  const [loading, setLoading] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  useEffect(() => {
    // Fetch current settings
    const fetchSettings = async () => {
      try {
        const response = await api.get('/settings/webhooks');
        if (response.data) {
          setWebhookUrl(response.data.target_url || '');
          setSecretKey(response.data.secret_key || '');
          setIsActive(response.data.is_active ?? true);
        }
      } catch (err) {
        console.error("Failed to load settings", err);
      }
    };
    fetchSettings();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post('/settings/webhooks', {
        target_url: webhookUrl,
        secret_key: secretKey,
        is_active: isActive
      });
      setShowSuccess(true);
      setTimeout(() => setShowSuccess(false), 3000);
    } catch (err) {
      console.error("Save failed", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <LayoutBase>
      <div className="space-y-8 animate-fade-in max-w-4xl mx-auto">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-white flex items-center gap-3">
            <SettingsIcon className="text-blue-500" />
            System Settings
          </h2>
          <p className="text-gray-400 mt-1">Configure integrations and security preferences.</p>
        </div>

        <div className="grid grid-cols-1 gap-8">
          {/* Outbound Webhooks Section */}
          <div className="glass p-8 rounded-[32px] border border-white/5 shadow-2xl space-y-8">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-purple-600/10 flex items-center justify-center text-purple-500">
                  <Webhook size={20} />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">Outbound Webhooks</h3>
                  <p className="text-sm text-gray-500">Connect to Zapier, Make.com or PowerAutomate.</p>
                </div>
              </div>
              <div className="flex items-center gap-2 text-xs font-bold text-gray-500 bg-white/5 px-4 py-2 rounded-full border border-white/5">
                <Zap size={14} className="text-yellow-500" />
                WEBHOOK SDK V1.0
              </div>
            </div>

            <form onSubmit={handleSave} className="space-y-6">
              <div className="space-y-2">
                <div className="flex items-center justify-between ml-1">
                  <label className="text-xs font-bold text-gray-400 uppercase tracking-widest">Payload Target URL</label>
                  <a href="https://zapier.com/apps/webhook/integrations" target="_blank" rel="noopener noreferrer" className="text-[10px] text-blue-500 hover:underline flex items-center gap-1">
                    Docs <ExternalLink size={10} />
                  </a>
                </div>
                <input 
                  type="url" 
                  placeholder="https://hooks.zapier.com/..."
                  value={webhookUrl}
                  onChange={(e) => setWebhookUrl(e.target.value)}
                  className="w-full px-5 py-4 bg-[#0d1117] border border-white/10 rounded-2xl text-sm text-white outline-none focus:border-purple-500/50 transition-all"
                />
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold text-gray-400 uppercase tracking-widest ml-1">Signing Secret (HMAC)</label>
                <div className="relative">
                  <Lock className="absolute left-5 top-1/2 -translate-y-1/2 text-gray-600" size={16} />
                  <input 
                    type="password" 
                    placeholder="Enter secret for signature validation"
                    value={secretKey}
                    onChange={(e) => setSecretKey(e.target.value)}
                    className="w-full pl-12 pr-5 py-4 bg-[#0d1117] border border-white/10 rounded-2xl text-sm text-white outline-none focus:border-purple-500/50 transition-all font-mono"
                  />
                </div>
                <p className="text-[10px] text-gray-500 ml-1">All payloads will be signed with this key in the <code className="text-purple-400">X-LuckArkman-Signature</code> header.</p>
              </div>

              <div className="flex items-center justify-between p-4 rounded-2xl bg-white/5 border border-white/5">
                <div className="flex items-center gap-3">
                  <ShieldCheck className="text-green-500" size={20} />
                  <div>
                    <p className="text-sm font-bold text-white">Enable Automated Triggers</p>
                    <p className="text-xs text-gray-500">Fire webhook on successful invoice processing.</p>
                  </div>
                </div>
                <button 
                  type="button"
                  onClick={() => setIsActive(!isActive)}
                  className={`w-12 h-6 rounded-full transition-colors relative ${isActive ? 'bg-purple-600' : 'bg-gray-700'}`}
                >
                  <div className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-all ${isActive ? 'right-1' : 'left-1'}`} />
                </button>
              </div>

              <div className="pt-4">
                <button 
                  disabled={loading}
                  className="w-full py-4 bg-white text-black font-bold rounded-2xl hover:bg-gray-200 transition-all flex items-center justify-center gap-2 h-14"
                >
                  {loading ? (
                    <RefreshCw className="animate-spin" size={20} />
                  ) : (
                    <>
                      <Save size={20} />
                      Save Integration Settings
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>

        <AnimatePresence>
          {showSuccess && (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              className="fixed bottom-12 right-12 bg-green-600 text-white px-8 py-4 rounded-3xl shadow-2xl flex items-center gap-3 font-bold z-50 border border-green-400/20"
            >
               <CheckCircle2 size={24} />
               <span>Settings Updated Successfully!</span>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </LayoutBase>
  );
};

export default SettingsView;

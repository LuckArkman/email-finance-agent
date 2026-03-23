import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Mail, Lock, Loader2, ArrowRight, Building2 } from 'lucide-react';
import api from '../services/api';

const Register: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [tenantName, setTenantName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await api.post('/auth/register', {
        email,
        password,
        tenant_name: tenantName
      });

      setSuccess(true);
      setTimeout(() => navigate('/login'), 2000);
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Unknown network error';
      setError(`Error: ${msg}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0d1117] relative overflow-hidden">
      {/* Abstract Background Shapes */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-600/20 blur-[120px] rounded-full" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-indigo-600/20 blur-[120px] rounded-full" />

      <div className="w-full max-w-md p-8 relative z-10">
        <div className="glass p-10 rounded-[32px] border border-white/10 shadow-2xl backdrop-blur-2xl animate-fade-in">
          <div className="text-center mb-10">
            <h1 className="text-4xl font-bold tracking-tight text-white mb-2">Create Account</h1>
            <p className="text-gray-400">Join LuckArkman and automate your finance agents</p>
          </div>

          {success ? (
            <div className="text-center p-8 space-y-4">
              <div className="w-16 h-16 bg-green-500/20 border border-green-500/40 rounded-full flex items-center justify-center mx-auto">
                <Loader2 className="animate-spin text-green-400" size={32} />
              </div>
              <p className="text-green-400 font-medium">Account created! Redirecting to login...</p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-300 ml-1">Company / Tenant Name</label>
                <div className="relative group">
                  <Building2 className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-blue-500 transition-colors" size={20} />
                  <input 
                    type="text" 
                    value={tenantName}
                    onChange={(e) => setTenantName(e.target.value)}
                    placeholder="Acme Corp"
                    required
                    className="w-full pl-12 pr-4 py-4 bg-white/5 border border-white/10 rounded-2xl outline-none focus:border-blue-500/50 focus:ring-4 focus:ring-blue-500/10 transition-all text-white"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-300 ml-1">Email Address</label>
                <div className="relative group">
                  <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-blue-500 transition-colors" size={20} />
                  <input 
                    type="email" 
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="name@company.com"
                    required
                    className="w-full pl-12 pr-4 py-4 bg-white/5 border border-white/10 rounded-2xl outline-none focus:border-blue-500/50 focus:ring-4 focus:ring-blue-500/10 transition-all text-white"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-300 ml-1">Password</label>
                <div className="relative group">
                  <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-blue-500 transition-colors" size={20} />
                  <input 
                    type="password" 
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    required
                    className="w-full pl-12 pr-4 py-4 bg-white/5 border border-white/10 rounded-2xl outline-none focus:border-blue-500/50 focus:ring-4 focus:ring-blue-500/10 transition-all text-white"
                  />
                </div>
              </div>

              {error && (
                <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm animate-shake">
                  {error}
                </div>
              )}

              <button 
                type="submit" 
                disabled={loading}
                className="w-full py-4 bg-blue-600 hover:bg-blue-500 disabled:bg-blue-800 disabled:cursor-not-allowed text-white font-bold rounded-2xl transition-all shadow-lg shadow-blue-600/20 flex items-center justify-center space-x-2 group active:scale-95"
              >
                {loading ? (
                  <Loader2 className="animate-spin" size={22} />
                ) : (
                  <>
                    <span>Sign Up</span>
                    <ArrowRight className="group-hover:translate-x-1 transition-transform" size={20} />
                  </>
                )}
              </button>

              <div className="text-center text-sm">
                <span className="text-gray-500">Already have an account? </span>
                <Link to="/login" className="text-blue-400 hover:text-blue-300 transition-colors font-medium">Log In</Link>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default Register;

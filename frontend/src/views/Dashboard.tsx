import React, { useEffect, useState, useCallback } from 'react';
import { 
  BarChart,
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';
import { 
  TrendingUp, 
  DollarSign, 
  FileCheck, 
  AlertCircle,
  ArrowUpRight,
  RefreshCw
} from 'lucide-react';
import api from '../services/api';
import LayoutBase from '../components/LayoutBase';
import { useAuthStore } from '../store/authStore';

const Dashboard: React.FC = () => {
  const [cashflowData, setCashflowData] = useState<any[]>([]);
  const [topVendors, setTopVendors] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuthStore();

  const fetchDashboardData = useCallback(async () => {
    setLoading(true);
    try {
      const [cashflowRes, vendorsRes] = await Promise.all([
        api.get('/analytics/cashflow'),
        api.get('/analytics/vendors/top')
      ]);
      
      setCashflowData(cashflowRes.data.cashflow_series);
      setTopVendors(vendorsRes.data.top_vendors);
    } catch (err) {
      console.error('Failed to fetch analytics', err);
      // Fallback mocks for UI preview
      setCashflowData([
        { month: 1, total_spent: 1200 }, { month: 2, total_spent: 2100 },
        { month: 3, total_spent: 800 }, { month: 4, total_spent: 1600 },
        { month: 5, total_spent: 900 }, { month: 6, total_spent: 1700 },
      ]);
      setTopVendors([
        { vendor: 'AWS', total_spent: 5000 },
        { vendor: 'Google Cloud', total_spent: 3200 },
        { vendor: 'Uber', total_spent: 800 },
        { vendor: 'GitHub', total_spent: 450 },
      ]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();

    // WebSocket Mock Integration for Real-time updates
    const ws = new WebSocket(`ws://localhost:8000/api/v1/ws/${user?.tenant_id}`);
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.event === "OCR_PROCESS_FINISHED") {
        console.log("Real-time update triggered via WebSocket");
        fetchDashboardData(); // Refresh metrics
      }
    };
    
    return () => ws.close();
  }, [fetchDashboardData, user?.tenant_id]);

  const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

  return (
    <LayoutBase>
      <div className="space-y-8 animate-fade-in">
        {/* Header Section */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold tracking-tight text-white">Financial Insights</h2>
            <p className="text-gray-400 mt-1">Real-time spending analysis and vendor metrics.</p>
          </div>
          <button 
            onClick={fetchDashboardData}
            className="p-3 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-all text-gray-400 hover:text-white"
          >
            <RefreshCw size={20} className={loading ? 'animate-spin' : ''} />
          </button>
        </div>

        {/* Metric Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <StatCard title="Total Spent (YTD)" value="$42,500.00" trend="+12.5%" icon={<DollarSign size={24} />} color="blue" />
          <StatCard title="Processed Invoices" value="128" trend="+5" icon={<FileCheck size={24} />} color="green" />
          <StatCard title="Pending Review" value="3" trend="-2" icon={<AlertCircle size={24} />} color="yellow" />
          <StatCard title="Avg. Score" value="96.2%" trend="+0.4%" icon={<TrendingUp size={24} />} color="purple" />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Cashflow Chart */}
          <div className="glass p-8 rounded-[32px] border border-white/5 shadow-2xl space-y-6">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <TrendingUp size={20} className="text-blue-500" />
              Annual Cashflow Trends
            </h3>
            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={cashflowData}>
                  <defs>
                    <linearGradient id="colorSpent" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <XAxis 
                    dataKey="month" 
                    tickFormatter={(m) => monthNames[m-1]} 
                    stroke="#4b5563" 
                    fontSize={12} 
                    tickLine={false} 
                    axisLine={false} 
                  />
                  <YAxis stroke="#4b5563" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(v) => `$${v}`} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0d1117', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px' }}
                    itemStyle={{ color: '#fff' }}
                  />
                  <Area type="monotone" dataKey="total_spent" stroke="#3b82f6" fillOpacity={1} fill="url(#colorSpent)" strokeWidth={3} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Top Vendors Bar Chart */}
          <div className="glass p-8 rounded-[32px] border border-white/5 shadow-2xl space-y-6">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <ArrowUpRight size={20} className="text-purple-500" />
              Top Vendors by Volume
            </h3>
            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={topVendors} layout="vertical">
                  <XAxis type="number" hide />
                  <YAxis dataKey="vendor" type="category" stroke="#9ca3af" fontSize={12} width={100} axisLine={false} tickLine={false} />
                  <Tooltip 
                    cursor={{fill: 'rgba(255,255,255,0.05)'}}
                    contentStyle={{ backgroundColor: '#0d1117', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px' }}
                  />
                  <Bar dataKey="total_spent" fill="#3b82f6" radius={[0, 8, 8, 0]} barSize={32} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
    </LayoutBase>
  );
};

const StatCard: React.FC<{ title: string; value: string; trend: string; icon: React.ReactNode; color: string }> = ({ 
  title, value, trend, icon, color 
}) => {
  const colorMap: any = {
    blue: 'bg-blue-600/10 text-blue-500',
    green: 'bg-green-600/10 text-green-500',
    yellow: 'bg-yellow-600/10 text-yellow-500',
    purple: 'bg-purple-600/10 text-purple-500',
  };

  return (
    <div className="glass p-6 rounded-3xl border border-white/5 shadow-lg relative overflow-hidden group">
      <div className={`w-12 h-12 rounded-2xl ${colorMap[color]} flex items-center justify-center mb-4 transition-transform group-hover:scale-110`}>
        {icon}
      </div>
      <div>
        <p className="text-xs font-bold text-gray-500 uppercase tracking-widest">{title}</p>
        <p className="text-2xl font-bold text-white mt-1">{value}</p>
        <div className="mt-3 flex items-center text-xs font-bold text-green-500">
          <span>{trend}</span>
          <span className="text-gray-500 ml-2 font-normal">than last month</span>
        </div>
      </div>
      {/* Decorative Gradient Background */}
      <div className={`absolute -right-4 -bottom-4 w-24 h-24 blur-3xl opacity-10 rounded-full ${colorMap[color].split(' ')[1]}`} />
    </div>
  );
};

export default Dashboard;

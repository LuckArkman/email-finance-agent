import React, { useState, useEffect } from 'react';
import { 
  AreaChart, 
  Area, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer 
} from 'recharts';
import { 
  FileText, 
  AlertCircle, 
  Target, 
  TrendingUp,
  ChevronDown,
  Download,
  Calendar,
  Filter
} from 'lucide-react';
import LayoutBase from '../components/LayoutBase';
import api from '../services/api';

const RelatoriosMetricas: React.FC = () => {
  const [stats, setStats] = useState({
    total_spent: 0,
    processed_count: 0,
    pending_review: 0,
    avg_confidence: 0
  });

  const [cashflow, setCashflow] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, cashRes] = await Promise.all([
          api.get('/analytics/stats'),
          api.get('/analytics/cashflow')
        ]);
        setStats(statsRes.data);
        
        // Map month numbers to Portuguese names for the chart
        const monthNames = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
        const series = cashRes.data.cashflow_series || [];
        const formattedCashflow = series.map((item: any) => ({
          name: monthNames[item.month - 1],
          spent: item.total_spent
        }));
        setCashflow(formattedCashflow);
      } catch (error) {
        console.error("Error fetching analytics:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  // Utility to format as Currency (BRL/EUR)
  const formatCurrency = (val: number) => {
    return new Intl.NumberFormat('pt-PT', { style: 'currency', currency: 'EUR' }).format(val);
  };

  const chartMockData = [
    { value: 4000 }, { value: 3000 }, { value: 5000 }, { value: 2780 }, { value: 1890 }, { value: 2390 }, { value: 3490 },
  ];

  if (loading) {
    return (
      <LayoutBase>
        <div className="flex items-center justify-center h-full">
           <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </LayoutBase>
    );
  }

  return (
    <LayoutBase>
      <div className="space-y-10 p-8 animate-fade-in no-scrollbar overflow-y-auto h-full">
         <div className="flex items-center justify-between">
            <div className="space-y-1">
               <h2 className="text-2xl font-black text-gray-900">Relatórios e Métricas</h2>
               <p className="text-gray-400 text-[13px] font-medium">Controlo analítico do ecossistema financeiro real.</p>
            </div>
            <div className="flex items-center space-x-3">
               <button className="flex items-center space-x-2 px-4 py-2.5 bg-white border border-gray-200 rounded-xl text-[13px] font-bold shadow-sm group hover:border-blue-500/20 transition-all"><Calendar size={16} /> <span>{new Date().getFullYear()}</span> <ChevronDown size={14} className="text-gray-300 group-hover:text-blue-500" /></button>
               <button className="flex items-center space-x-2 px-4 py-2.5 bg-white border border-gray-200 rounded-xl text-[13px] font-bold shadow-sm group hover:border-blue-500/20 transition-all"><Filter size={16} /> <span>Filtros</span></button>
               <button className="flex items-center space-x-2 px-4 py-2.5 bg-blue-600 text-white rounded-xl text-[13px] font-bold shadow-lg shadow-blue-500/30 active:scale-95 transition-all"><Download size={16} /> <span>Exportar</span></button>
            </div>
         </div>

         {/* Metrics Grid */}
         <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <MetricCard 
              title="Total em Faturas" 
              value={formatCurrency(stats.total_spent)} 
              trend="+0%" 
              icon={<TrendingUp size={20} />} 
              data={chartMockData} 
              color="blue" 
            />
            <MetricCard 
              title="Média por Doc." 
              value={formatCurrency(stats.processed_count > 0 ? stats.total_spent / stats.processed_count : 0)} 
              trend="IA" 
              icon={<FileText size={20} />} 
              data={chartMockData} 
              color="purple" 
            />
            <MetricCard 
              title="Aguardando Revisão" 
              value={stats.pending_review.toString()} 
              trend="Ação" 
              icon={<AlertCircle size={20} />} 
              data={chartMockData} 
              color="red" 
            />
            <MetricCard 
              title="Confiança Média" 
              value={`${stats.avg_confidence}%`} 
              trend="Preciso" 
              icon={<Target size={20} />} 
              data={chartMockData} 
              color="green" 
            />
         </div>

         {/* Business Evolution */}
         <section className="bg-white p-10 rounded-[48px] shadow-sm border border-gray-100 space-y-8">
            <div className="flex justify-between items-center">
               <h3 className="text-sm font-black text-gray-400 uppercase tracking-widest">Fluxo de Despesas (Acumulado Mensal)</h3>
               <div className="flex items-center space-x-6">
                  <div className="flex items-center space-x-2">
                     <div className="w-2.5 h-2.5 rounded-full bg-blue-500" />
                     <span className="text-[11px] font-extrabold text-gray-400">Total Gasto</span>
                  </div>
               </div>
            </div>

            <div className="h-[400px] w-full">
               <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={cashflow}>
                     <XAxis dataKey="name" axisLine={false} tickLine={false} fontSize={12} tick={{ fill: '#9ca3af', fontWeight: 'bold' }} dy={10} />
                     <YAxis axisLine={false} tickLine={false} fontSize={12} tick={{ fill: '#9ca3af', fontWeight: 'bold' }} tickFormatter={(v) => `€${v/1000}k`} />
                     <Tooltip 
                       cursor={{ fill: '#f9fafb' }}
                       contentStyle={{ borderRadius: '24px', border: 'none', boxShadow: '0 20px 40px rgba(0,0,0,0.05)', padding: '20px' }}
                       formatter={(value: any) => formatCurrency(value)}
                     />
                     <Bar dataKey="spent" fill="#3b82f6" radius={[6, 6, 0, 0]} barSize={40} />
                  </BarChart>
               </ResponsiveContainer>
            </div>
         </section>
      </div>
    </LayoutBase>
  );
};

const MetricCard = ({ title, value, trend, icon, data, color }: { title: string; value: string; trend: string; icon: any; data: any[]; color: string }) => {
  const colorMap: any = {
    blue: '#3b82f6',
    red: '#ef4444',
    green: '#22c55e',
    purple: '#a855f7',
  };
  return (
    <div className="bg-white p-8 rounded-[40px] shadow-sm border border-gray-100 space-y-4 hover:shadow-xl transition-all group">
       <div className="flex justify-between items-start">
          <div className={`p-3 bg-gray-50 rounded-2xl text-gray-400 group-hover:text-blue-500 transition-colors`}>{icon}</div>
          <span className={`text-xs font-black ${trend.startsWith('+') ? 'text-green-500' : 'text-blue-500'}`}>{trend}</span>
       </div>
       <div className="space-y-1">
          <p className="text-[11px] font-extrabold text-gray-400 uppercase tracking-widest">{title}</p>
          <p className="text-2xl font-black text-gray-900">{value}</p>
       </div>
       <div className="h-16 w-full -mx-4 group-hover:scale-y-110 transition-transform">
          <ResponsiveContainer width="100%" height="100%">
             <AreaChart data={data}>
                <Area type="monotone" dataKey="value" stroke={colorMap[color]} fill={colorMap[color]} fillOpacity={0.05} strokeWidth={2} />
             </AreaChart>
          </ResponsiveContainer>
       </div>
    </div>
  );
};

export default RelatoriosMetricas;

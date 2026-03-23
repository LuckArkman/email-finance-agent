import React from 'react';
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
  TrendingUp, 
  TrendingDown, 
  Users, 
  Zap,
  ChevronDown,
  Download,
  Calendar,
  Filter
} from 'lucide-react';
import LayoutBase from '../components/LayoutBase';

const RelatoriosMetricas: React.FC = () => {
  const data = [
    { name: 'Jan', value: 4000 },
    { name: 'Fev', value: 3000 },
    { name: 'Mar', value: 5000 },
    { name: 'Abr', value: 2780 },
    { name: 'Mai', value: 1890 },
    { name: 'Jun', value: 2390 },
    { name: 'Jul', value: 3490 },
  ];

  const businessEvolution = [
    { name: 'Set', receita: 45000, custo: 32000 },
    { name: 'Out', receita: 52000, custo: 38000 },
    { name: 'Nov', receita: 48000, custo: 35000 },
    { name: 'Dez', receita: 61000, custo: 42000 },
    { name: 'Jan', receita: 55000, custo: 40000 },
    { name: 'Fev', receita: 67000, custo: 45000 },
  ];

  return (
    <LayoutBase>
      <div className="space-y-10 p-8 animate-fade-in no-scrollbar overflow-y-auto h-full">
         <div className="flex items-center justify-between">
            <div className="space-y-1">
               <h2 className="text-2xl font-black text-gray-900">Relatórios e Métricas</h2>
               <p className="text-gray-400 text-[13px] font-medium">Controlo analítico do ecossistema financeiro.</p>
            </div>
            <div className="flex items-center space-x-3">
               <button className="flex items-center space-x-2 px-4 py-2.5 bg-white border border-gray-200 rounded-xl text-[13px] font-bold shadow-sm group hover:border-blue-500/20 transition-all"><Calendar size={16} /> <span>Outubro 2024</span> <ChevronDown size={14} className="text-gray-300 group-hover:text-blue-500" /></button>
               <button className="flex items-center space-x-2 px-4 py-2.5 bg-white border border-gray-200 rounded-xl text-[13px] font-bold shadow-sm group hover:border-blue-500/20 transition-all"><Filter size={16} /> <span>Filtros</span></button>
               <button className="flex items-center space-x-2 px-4 py-2.5 bg-blue-600 text-white rounded-xl text-[13px] font-bold shadow-lg shadow-blue-500/30 active:scale-95 transition-all"><Download size={16} /> <span>Exportar</span></button>
            </div>
         </div>

         {/* Metrics Grid */}
         <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <MetricCard title="Receita Total" value="€67.240,00" trend="+12%" icon={<TrendingUp size={20} />} data={data} color="blue" />
            <MetricCard title="Ticket Médio" value="€2.450" trend="-4%" icon={<TrendingDown size={20} />} data={data} color="red" />
            <MetricCard title="Novos Clientes" value="142" trend="+8%" icon={<Users size={20} />} data={data} color="green" />
            <MetricCard title="Eficiência Energética" value="94.2%" trend="+2%" icon={<Zap size={20} />} data={data} color="purple" />
         </div>

         {/* Business Evolution */}
         <section className="bg-white p-10 rounded-[48px] shadow-sm border border-gray-100 space-y-8">
            <div className="flex justify-between items-center">
               <h3 className="text-sm font-black text-gray-400 uppercase tracking-widest">Evolução mensal do negócio</h3>
               <div className="flex items-center space-x-6">
                  <div className="flex items-center space-x-2">
                     <div className="w-2.5 h-2.5 rounded-full bg-blue-500" />
                     <span className="text-[11px] font-extrabold text-gray-400">Receita</span>
                  </div>
                  <div className="flex items-center space-x-2">
                     <div className="w-2.5 h-2.5 rounded-full bg-blue-200" />
                     <span className="text-[11px] font-extrabold text-gray-400">Custo Operacional</span>
                  </div>
               </div>
            </div>

            <div className="h-[400px] w-full">
               <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={businessEvolution}>
                     <XAxis dataKey="name" axisLine={false} tickLine={false} fontSize={12} tick={{ fill: '#9ca3af', fontWeight: 'bold' }} dy={10} />
                     <YAxis axisLine={false} tickLine={false} fontSize={12} tick={{ fill: '#9ca3af', fontWeight: 'bold' }} tickFormatter={(v) => `€${v/1000}k`} />
                     <Tooltip 
                       cursor={{ fill: '#f9fafb' }}
                       contentStyle={{ borderRadius: '24px', border: 'none', boxShadow: '0 20px 40px rgba(0,0,0,0.05)', padding: '20px' }}
                     />
                     <Bar dataKey="receita" fill="#3b82f6" radius={[6, 6, 0, 0]} barSize={24} />
                     <Bar dataKey="custo" fill="#bfdbfe" radius={[6, 6, 0, 0]} barSize={24} />
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
          <span className={`text-xs font-black ${trend.startsWith('+') ? 'text-green-500' : 'text-red-500'}`}>{trend}</span>
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

import React, { useState } from 'react';
import { 
  ChevronLeft, 
  ChevronRight, 
  Calendar as CalendarIcon,
  DollarSign,
  AlertTriangle,
  TrendingDown,
  LayoutGrid,
  Filter,
  Plus
} from 'lucide-react';
import LayoutBase from '../components/LayoutBase';

const PaymentsAgenda: React.FC = () => {
  const [currentDate, setCurrentDate] = useState(new Date());

  const daysInMonth = (year: number, month: number) => new Date(year, month + 1, 0).getDate();
  const firstDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1).getDay();
  
  const monthName = currentDate.toLocaleString('pt-PT', { month: 'long' });
  const year = currentDate.getFullYear();

  const days = [];
  for (let i = 0; i < firstDayOfMonth; i++) days.push(null);
  for (let i = 1; i <= daysInMonth(year, currentDate.getMonth()); i++) days.push(i);

  // Mock payments
  const payments = [
    { day: 15, vendor: 'EDP', amount: '€145,20', status: 'pending' },
    { day: 22, vendor: 'Aluguer', amount: '€1,200,00', status: 'paid' },
    { day: 28, vendor: 'AWS', amount: '€450,00', status: 'overdue' },
  ];

  return (
    <LayoutBase>
      <div className="flex h-full overflow-hidden">
        {/* Calendar View */}
        <div className="flex-1 p-8 space-y-8 overflow-y-auto no-scrollbar">
           <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                 <h2 className="text-2xl font-black text-gray-900 capitalize">{monthName} {year}</h2>
                 <div className="flex space-x-1">
                    <button onClick={() => setCurrentDate(new Date(year, currentDate.getMonth() - 1))} className="p-2 hover:bg-white rounded-xl border border-gray-200"><ChevronLeft size={16} /></button>
                    <button onClick={() => setCurrentDate(new Date(year, currentDate.getMonth() + 1))} className="p-2 hover:bg-white rounded-xl border border-gray-200"><ChevronRight size={16} /></button>
                 </div>
              </div>
              <div className="flex items-center space-x-3">
                 <button className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-200 rounded-xl text-[13px] font-bold shadow-sm"><Filter size={16} /> <span>Filtros</span></button>
                 <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-xl text-[13px] font-bold shadow-lg shadow-blue-500/30"><Plus size={16} /> <span>Novo Agendamento</span></button>
              </div>
           </div>

           <div className="bg-white rounded-[40px] shadow-sm border border-gray-100 overflow-hidden p-8">
              <div className="grid grid-cols-7 mb-4">
                 {['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'].map(d => (
                   <div key={d} className="text-center text-[10px] font-extrabold text-gray-400 uppercase tracking-widest py-4">{d}</div>
                 ))}
              </div>
              <div className="grid grid-cols-7 gap-4">
                 {days.map((day, idx) => {
                   const payment = payments.find(p => p.day === day);
                   return (
                     <div key={idx} className={`aspect-square rounded-3xl p-4 transition-all border ${day ? 'bg-gray-50/50 border-gray-50' : 'border-transparent'} ${payment ? 'ring-2 ring-blue-500/20 bg-white border-blue-100' : ''}`}>
                        {day && (
                          <div className="flex flex-col h-full">
                             <span className={`text-[14px] font-black ${payment ? 'text-blue-600' : 'text-gray-400'}`}>{day}</span>
                             {payment && (
                               <div className="mt-auto space-y-1">
                                  <p className="text-[10px] font-black text-gray-900 truncate">{payment.vendor}</p>
                                  <p className="text-[10px] text-gray-500 font-bold">{payment.amount}</p>
                               </div>
                             )}
                          </div>
                        )}
                     </div>
                   );
                 })}
              </div>
           </div>
        </div>

        {/* Status Sidebar */}
        <div className="w-[380px] border-l border-gray-200 bg-white h-full p-8 flex flex-col space-y-10 overflow-y-auto no-scrollbar">
           <div className="space-y-6">
              <h3 className="text-sm font-extrabold text-gray-400 uppercase tracking-widest">Neste Mês</h3>
              <div className="space-y-4">
                 <SummaryCard 
                   icon={<DollarSign size={20} />} 
                   label="Total a Pagar" 
                   value="€4.250,00" 
                   color="blue" 
                 />
                 <SummaryCard 
                   icon={<AlertTriangle size={20} />} 
                   label="Em atraso" 
                   value="€145,20" 
                   color="red" 
                 />
                 <SummaryCard 
                   icon={<TrendingDown size={20} />} 
                   label="Previsão Fluxo" 
                   value="-€850,00" 
                   color="orange" 
                 />
              </div>
           </div>

           <div className="space-y-6 flex-1">
              <div className="flex justify-between items-center">
                 <h3 className="text-sm font-extrabold text-gray-400 uppercase tracking-widest">Próximas Contas</h3>
                 <LayoutGrid size={16} className="text-gray-300 pointer-events-none" />
              </div>
              <div className="space-y-4">
                 {payments.map((p, i) => (
                   <div key={i} className="flex items-center space-x-4 group cursor-pointer hover:bg-gray-50 p-2 rounded-2xl transition-all">
                      <div className="w-12 h-12 rounded-2xl bg-gray-100 flex items-center justify-center font-black text-gray-900 shadow-sm border border-gray-200 group-hover:bg-white group-hover:border-blue-100">
                         {p.day}
                      </div>
                      <div className="flex-1">
                         <h4 className="font-bold text-[13px] text-gray-900">{p.vendor}</h4>
                         <p className="text-[11px] text-gray-400">Classificação: Fornecedor</p>
                      </div>
                      <span className="font-black text-gray-900 text-[13px]">{p.amount}</span>
                   </div>
                 ))}
              </div>
           </div>
           
           <button className="bg-gray-900 text-white rounded-2xl p-4 py-3 font-bold text-sm shadow-xl flex items-center justify-center space-x-2 active:scale-95 transition-all">
              <CalendarIcon size={18} />
              <span>Sincronizar com Agenda</span>
           </button>
        </div>
      </div>
    </LayoutBase>
  );
};

const SummaryCard = ({ icon, label, value, color }: { icon: any; label: string; value: string; color: string }) => {
  const styles: any = {
    blue: 'bg-blue-50 text-blue-600 border-blue-100',
    red: 'bg-red-50 text-red-600 border-red-100',
    orange: 'bg-orange-50 text-orange-600 border-orange-100',
  };
  return (
    <div className={`p-5 rounded-[28px] border transition-all hover:scale-[1.02] cursor-default ${styles[color]}`}>
       <div className="flex items-center justify-between mb-3">
          <div className={`w-10 h-10 rounded-xl flex items-center justify-center bg-white shadow-sm border border-inherit`}>
             {icon}
          </div>
          <span className="text-[10px] font-black uppercase tracking-wider opacity-60">Mensal</span>
       </div>
       <p className="text-[11px] font-bold opacity-70 mb-1">{label}</p>
       <p className="text-2xl font-black">{value}</p>
    </div>
  );
};

export default PaymentsAgenda;

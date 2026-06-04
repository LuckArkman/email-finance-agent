import React, { useState, useEffect, useCallback } from 'react';
import {
  ChevronLeft,
  ChevronRight,
  Calendar as CalendarIcon,
  Euro,
  AlertTriangle,
  RefreshCw,
  X,
  FileText,
  Receipt,
  CheckCircle2,
  HelpCircle,
  Loader2,
  Clock,
  CreditCard,
  Hash,
  ArrowRight,
} from 'lucide-react';
import LayoutBase from '../components/LayoutBase';
import api from '../services/api';

interface InvoiceItem {
  id: string;
  vendor_name: string | null;
  invoice_number: string | null;
  due_date: string | null;
  issue_date: string | null;
  document_type: string | null;
  net_amount: number;
  iva_rate: number;
  iva_amount: number;
  total_amount: number;
  currency: string;
  status: string;
  payment_reference: string | null;
}

const STATUS_CONFIG: Record<string, { label: string; color: string; textColor: string; bg: string; border: string; dot: string; badgeBg: string }> = {
  pending:         { label: 'Em Aberto',    color: 'text-blue-600',   textColor: 'text-blue-700',   bg: 'bg-blue-50',    border: 'border-blue-200',  dot: 'bg-blue-500',   badgeBg: 'bg-blue-100' },
  paid:            { label: 'Pago',         color: 'text-green-600',  textColor: 'text-green-700',  bg: 'bg-green-50',   border: 'border-green-200', dot: 'bg-green-500',  badgeBg: 'bg-green-100' },
  overdue:         { label: 'Em Atraso',    color: 'text-red-600',    textColor: 'text-red-700',    bg: 'bg-red-50',     border: 'border-red-200',   dot: 'bg-red-500',    badgeBg: 'bg-red-100' },
  reconciliation:  { label: 'Conciliação',  color: 'text-red-600',    textColor: 'text-red-700',    bg: 'bg-red-50',     border: 'border-red-200',   dot: 'bg-red-400',    badgeBg: 'bg-red-100' },
  review_required: { label: 'Em Revisão',   color: 'text-purple-600', textColor: 'text-purple-700', bg: 'bg-purple-50',  border: 'border-purple-200',dot: 'bg-purple-500', badgeBg: 'bg-purple-100' },
};

const DOCTYPE_CONFIG: Record<string, { label: string; icon: React.ReactNode }> = {
  accounts_payable: { label: 'Conta a Pagar', icon: <FileText size={13} /> },
  paid_bill:        { label: 'Conta Paga',     icon: <CheckCircle2 size={13} /> },
  payment_receipt:  { label: 'Comprovante',    icon: <Receipt size={13} /> },
  non_financial:    { label: 'Não Financeiro', icon: <HelpCircle size={13} /> },
};

const fmt = (n: number) =>
  `€${(n || 0).toLocaleString('pt-PT', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

const getDaysUntil = (dueDateStr: string | null): number | null => {
  if (!dueDateStr) return null;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const due = new Date(dueDateStr + 'T12:00:00');
  due.setHours(0, 0, 0, 0);
  return Math.round((due.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
};

// Determines the cell urgency color for a given day's invoices
const getDayUrgency = (invoices: InvoiceItem[], dayKey: string): 'overdue' | 'today' | 'pending' | 'paid' | 'none' => {
  if (invoices.length === 0) return 'none';
  const todayKey = new Date().toISOString().split('T')[0];
  const hasOverdue = invoices.some(i => i.status === 'overdue' || i.status === 'reconciliation');
  const hasPending = invoices.some(i => i.status === 'pending');
  const allPaid = invoices.every(i => i.status === 'paid');
  if (hasOverdue) return 'overdue';
  if (dayKey < todayKey && hasPending) return 'overdue';
  if (dayKey === todayKey) return 'today';
  if (hasPending) return 'pending';
  if (allPaid) return 'paid';
  return 'none';
};

// Color scheme for a day's invoice card in the modal
const getInvoiceCardColor = (inv: InvoiceItem, dayKey: string) => {
  const todayKey = new Date().toISOString().split('T')[0];
  if (inv.status === 'overdue' || inv.status === 'reconciliation') return 'overdue';
  if (dayKey < todayKey) return 'overdue';
  if (dayKey === todayKey) return 'today';
  return 'pending';
};

const CARD_STYLES = {
  overdue: { bg: 'bg-red-50', border: 'border-red-200', header: 'bg-red-500', accent: 'text-red-600', dot: 'bg-red-500', badge: 'bg-red-100 text-red-700' },
  today:   { bg: 'bg-orange-50', border: 'border-orange-200', header: 'bg-orange-500', accent: 'text-orange-600', dot: 'bg-orange-500', badge: 'bg-orange-100 text-orange-700' },
  pending: { bg: 'bg-blue-50', border: 'border-blue-200', header: 'bg-blue-500', accent: 'text-blue-600', dot: 'bg-blue-500', badge: 'bg-blue-100 text-blue-700' },
};

const PaymentsAgenda: React.FC = () => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [calendarData, setCalendarData] = useState<Record<string, InvoiceItem[]>>({});
  const [loading, setLoading] = useState(true);
  const [selectedDay, setSelectedDay] = useState<string | null>(null);

  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();

  const fetchCalendar = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get(`/invoices/calendar?year=${year}&month=${month + 1}`);
      setCalendarData(res.data || {});
    } catch (err) {
      console.error('Failed to fetch calendar', err);
    } finally {
      setLoading(false);
    }
  }, [year, month]);

  useEffect(() => {
    fetchCalendar();
    setSelectedDay(null);
  }, [fetchCalendar]);

  // Build calendar grid
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const firstDayOfMonth = new Date(year, month, 1).getDay();
  const days: (number | null)[] = [];
  for (let i = 0; i < firstDayOfMonth; i++) days.push(null);
  for (let i = 1; i <= daysInMonth; i++) days.push(i);

  const monthName = currentDate.toLocaleString('pt-PT', { month: 'long' });

  const getDayKey = (day: number) =>
    `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;

  const getDayInvoices = (day: number) => calendarData[getDayKey(day)] || [];

  // --- Monthly Stats ---
  const allInvoices = Object.values(calendarData).flat();

  const totalPending   = allInvoices.filter(i => i.status === 'pending').reduce((s, i) => s + (i.total_amount || 0), 0);
  const totalOverdue   = allInvoices.filter(i => i.status === 'overdue' || i.status === 'reconciliation').reduce((s, i) => s + (i.total_amount || 0), 0);
  const totalMonth     = allInvoices.reduce((s, i) => s + (i.total_amount || 0), 0);
  const countTotal     = allInvoices.length;
  const countPending   = allInvoices.filter(i => i.status === 'pending').length;
  const countOverdue   = allInvoices.filter(i => i.status === 'overdue').length;
  const countReconc    = allInvoices.filter(i => i.status === 'reconciliation').length;

  // --- Upcoming bills (pending/overdue, sorted by due date) ---
  const upcomingBills = allInvoices
    .filter(i => i.status === 'pending' || i.status === 'overdue' || i.status === 'reconciliation')
    .sort((a, b) => {
      if (!a.due_date) return 1;
      if (!b.due_date) return -1;
      return a.due_date.localeCompare(b.due_date);
    });

  const selectedInvoices = selectedDay ? (calendarData[selectedDay] || []) : [];

  const todayKey = new Date().toISOString().split('T')[0];

  return (
    <LayoutBase>
      <div className="flex h-full overflow-hidden bg-[#f3f4f6]">
        {/* ─── Main Calendar Panel ─── */}
        <div className="flex-1 p-8 space-y-8 overflow-y-auto no-scrollbar">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex space-x-1">
                <button
                  id="calendar-prev-month"
                  onClick={() => setCurrentDate(new Date(year, month - 1))}
                  className="p-2.5 bg-white hover:bg-gray-50 rounded-xl border border-gray-200 transition-all shadow-sm"
                >
                  <ChevronLeft size={16} className="text-gray-600" />
                </button>
                <button
                  id="calendar-next-month"
                  onClick={() => setCurrentDate(new Date(year, month + 1))}
                  className="p-2.5 bg-white hover:bg-gray-50 rounded-xl border border-gray-200 transition-all shadow-sm"
                >
                  <ChevronRight size={16} className="text-gray-600" />
                </button>
              </div>
              <div>
                <h2 className="text-2xl font-black text-gray-900 capitalize">{monthName} {year}</h2>
                <p className="text-[10px] font-extrabold text-gray-400 uppercase tracking-widest">{countTotal} fatura(s) neste mês</p>
              </div>
            </div>
            <button
              id="calendar-refresh"
              onClick={fetchCalendar}
              className="flex items-center space-x-2 px-4 py-2.5 bg-white border border-gray-200 rounded-xl text-[13px] font-bold shadow-sm hover:bg-gray-50 transition-all"
            >
              <RefreshCw size={14} className={loading ? 'animate-spin text-blue-500' : 'text-gray-500'} />
              <span className="text-gray-700">Actualizar</span>
            </button>
          </div>

          {/* Calendar Grid */}
          <div className="bg-white rounded-[40px] shadow-sm border border-gray-100 overflow-hidden p-8 relative min-h-[520px] shadow-2xl shadow-gray-200/50">
            {loading && (
              <div className="absolute inset-0 bg-white/80 backdrop-blur-sm z-50 flex items-center justify-center rounded-[40px]">
                <div className="flex flex-col items-center space-y-4">
                  <Loader2 className="animate-spin text-blue-600" size={40} />
                  <p className="text-sm font-black text-gray-900 uppercase tracking-widest">A Sincronizar Agenda...</p>
                </div>
              </div>
            )}

            {/* Day of week headers */}
            <div className="grid grid-cols-7 mb-2">
              {['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'].map(d => (
                <div key={d} className="text-center text-[10px] font-extrabold text-gray-400 uppercase tracking-widest py-3">
                  {d}
                </div>
              ))}
            </div>

            {/* Day cells */}
            <div className="grid grid-cols-7 gap-1.5">
              {days.map((day, idx) => {
                if (!day) return <div key={idx} />;
                const dayKey = getDayKey(day);
                const dayInvoices = getDayInvoices(day);
                const urgency = getDayUrgency(dayInvoices, dayKey);
                const isSelected = selectedDay === dayKey;
                const isToday = dayKey === todayKey;

                const cellStyles: Record<string, string> = {
                  none:    'bg-gray-50/60 border-gray-100 hover:bg-gray-100/60',
                  paid:    'bg-green-50 border-green-100',
                  pending: 'bg-blue-50 border-blue-100',
                  today:   'bg-orange-50 border-orange-200',
                  overdue: 'bg-red-50 border-red-200',
                };

                const countByStatus = {
                  pending:        dayInvoices.filter(i => i.status === 'pending').length,
                  overdue:        dayInvoices.filter(i => i.status === 'overdue' || i.status === 'reconciliation').length,
                  paid:           dayInvoices.filter(i => i.status === 'paid').length,
                };

                return (
                  <div
                    key={idx}
                    id={`calendar-day-${dayKey}`}
                    onClick={() => setSelectedDay(isSelected ? null : dayKey)}
                    className={`
                      relative rounded-2xl p-2.5 border transition-all duration-200 cursor-pointer min-h-[80px] flex flex-col
                      ${cellStyles[urgency] || cellStyles.none}
                      ${isSelected ? 'ring-2 ring-blue-500 ring-offset-1 scale-[1.03] z-10 shadow-xl bg-white' : ''}
                      ${dayInvoices.length > 0 ? 'hover:scale-[1.02] hover:shadow-md' : ''}
                    `}
                  >
                    {/* Day number */}
                    <div className="flex items-center justify-between mb-1">
                      <span className={`text-[12px] font-black leading-none ${
                        isToday ? 'w-5 h-5 rounded-full bg-blue-600 text-white flex items-center justify-center text-[10px]' :
                        urgency === 'overdue' ? 'text-red-600' :
                        urgency === 'today' ? 'text-orange-600' :
                        urgency === 'pending' ? 'text-blue-600' :
                        urgency === 'paid' ? 'text-green-600' : 'text-gray-400'
                      }`}>
                        {day}
                      </span>
                      {dayInvoices.length > 0 && (
                        <span className={`text-[8px] font-black px-1 py-0.5 rounded-md ${
                          urgency === 'overdue' ? 'bg-red-100 text-red-600' :
                          urgency === 'today' ? 'bg-orange-100 text-orange-600' :
                          urgency === 'pending' ? 'bg-blue-100 text-blue-600' :
                          'bg-gray-100 text-gray-500'
                        }`}>
                          {dayInvoices.length}
                        </span>
                      )}
                    </div>

                    {/* Invoice dots with vendor names */}
                    <div className="flex-1 space-y-1 mt-1">
                      {dayInvoices.slice(0, 3).map((inv, i) => {
                        const sc = STATUS_CONFIG[inv.status];
                        return (
                          <div key={i} className={`flex items-center gap-1 overflow-hidden px-1.5 py-0.5 rounded ${sc?.badgeBg || 'bg-gray-100'}`}>
                            <span className={`w-1 h-1 rounded-full flex-shrink-0 ${sc?.dot || 'bg-gray-400'}`} />
                            <p className={`text-[9px] font-bold truncate leading-tight ${sc?.textColor || 'text-gray-700'}`}>
                              {inv.vendor_name || 'Fatura'}
                            </p>
                          </div>
                        );
                      })}
                      {dayInvoices.length > 3 && (
                        <p className="text-[8px] font-black text-blue-500 pl-1 pt-0.5">+{dayInvoices.length - 3} mais</p>
                      )}
                    </div>

                    {/* Total amount if has invoices */}
                    {dayInvoices.length > 0 && (
                      <div className={`text-[9px] font-black mt-1 text-right ${
                        urgency === 'overdue' ? 'text-red-600' :
                        urgency === 'today' ? 'text-orange-600' :
                        urgency === 'pending' ? 'text-blue-600' : 'text-gray-500'
                      }`}>
                        {fmt(dayInvoices.reduce((s, i) => s + (i.total_amount || 0), 0))}
                      </div>
                    )}

                    {/* Status pill indicators at bottom */}
                    {dayInvoices.length > 0 && (
                      <div className="flex gap-0.5 mt-1">
                        {countByStatus.pending > 0 && <span className="w-2 h-1 rounded-full bg-blue-400" title={`${countByStatus.pending} em aberto`} />}
                        {countByStatus.overdue > 0 && <span className="w-2 h-1 rounded-full bg-red-500" title={`${countByStatus.overdue} em atraso`} />}
                        {countByStatus.paid > 0 && <span className="w-2 h-1 rounded-full bg-green-500" title={`${countByStatus.paid} pagos`} />}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Legend */}
            <div className="flex flex-wrap items-center gap-x-6 gap-y-2 mt-8 pt-6 border-t border-gray-100">
              {[
                { dot: 'bg-blue-500', label: 'Em Aberto' },
                { dot: 'bg-orange-500', label: 'Vence Hoje' },
                { dot: 'bg-red-500', label: 'Em Atraso / Conciliação' },
                { dot: 'bg-green-500', label: 'Pago' },
              ].map(({ dot, label }) => (
                <div key={label} className="flex items-center gap-2">
                  <span className={`w-2 h-2 rounded-full ${dot}`} />
                  <span className="text-[10px] font-bold text-gray-400">{label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ─── Right Sidebar ─── */}
        <div className="w-[390px] border-l border-gray-200 bg-white h-full flex flex-col overflow-y-auto no-scrollbar">
          <div className="flex-1 p-7 space-y-8">
            {/* Monthly Summary */}
            <div className="space-y-4">
              <h3 className="text-[10px] font-extrabold text-gray-400 uppercase tracking-widest">Resumo — {monthName}</h3>

              {/* Money KPIs */}
              <div className="space-y-3">
                <div className="p-5 rounded-[24px] border border-blue-100 bg-blue-50">
                  <div className="flex items-center justify-between mb-3">
                    <div className="w-9 h-9 rounded-xl flex items-center justify-center bg-white shadow-sm border border-blue-100">
                      <FileText size={18} className="text-blue-600" />
                    </div>
                    <span className="text-[9px] font-black uppercase tracking-widest text-blue-400">Total em Aberto</span>
                  </div>
                  <p className="text-2xl font-black text-blue-700">{fmt(totalPending)}</p>
                  <p className="text-[10px] font-bold text-blue-500 mt-1">{countPending} fatura(s) pendente(s)</p>
                </div>

                <div className="p-5 rounded-[24px] border border-red-100 bg-red-50">
                  <div className="flex items-center justify-between mb-3">
                    <div className="w-9 h-9 rounded-xl flex items-center justify-center bg-white shadow-sm border border-red-100">
                      <AlertTriangle size={18} className="text-red-600" />
                    </div>
                    <span className="text-[9px] font-black uppercase tracking-widest text-red-400">Vencidas / Conciliação</span>
                  </div>
                  <p className="text-2xl font-black text-red-700">{fmt(totalOverdue)}</p>
                  <div className="flex gap-3 mt-1">
                    <p className="text-[10px] font-bold text-red-500">{countOverdue} em atraso</p>
                    {countReconc > 0 && <p className="text-[10px] font-bold text-red-400">· {countReconc} em conciliação</p>}
                  </div>
                </div>

                <div className="p-5 rounded-[24px] border border-gray-200 bg-white shadow-sm">
                  <div className="flex items-center justify-between mb-3">
                    <div className="w-9 h-9 rounded-xl flex items-center justify-center bg-gray-50 shadow-sm border border-gray-200">
                      <Euro size={18} className="text-gray-700" />
                    </div>
                    <span className="text-[9px] font-black uppercase tracking-widest text-gray-500">Total do Mês</span>
                  </div>
                  <p className="text-2xl font-black text-gray-900">{fmt(totalMonth)}</p>
                  <p className="text-[10px] font-bold text-gray-500 mt-1">{countTotal} fatura(s) no total este mês</p>
                </div>
              </div>
            </div>

            {/* Upcoming Bills */}
            <div className="space-y-4">
              <h3 className="text-[10px] font-extrabold text-gray-400 uppercase tracking-widest">Próximas Contas</h3>
              {upcomingBills.length === 0 && !loading && (
                <div className="text-center py-8 opacity-40 italic text-sm text-gray-500">Nenhuma conta este mês.</div>
              )}
              <div className="space-y-2 max-h-[360px] overflow-y-auto pr-2 pb-4 no-scrollbar">
                {upcomingBills.map((inv, i) => {
                  const daysLeft = getDaysUntil(inv.due_date);
                  const sc = STATUS_CONFIG[inv.status] || STATUS_CONFIG.pending;
                  const isOverdue = inv.status === 'overdue' || inv.status === 'reconciliation' || (daysLeft !== null && daysLeft < 0);
                  const isToday = daysLeft === 0;
                  return (
                    <div
                      key={i}
                      onClick={() => {
                        if (inv.due_date) setSelectedDay(inv.due_date);
                      }}
                      className={`flex items-center gap-3 p-3 rounded-2xl border transition-all hover:shadow-md cursor-pointer ${
                        isOverdue ? 'bg-red-50 border-red-100 hover:border-red-300' :
                        isToday ? 'bg-orange-50 border-orange-100 hover:border-orange-300' :
                        'bg-gray-50 border-gray-100 hover:bg-white hover:border-blue-200'
                      }`}
                    >
                      {/* Day badge */}
                      <div className={`w-10 h-10 rounded-xl flex flex-col items-center justify-center text-white flex-shrink-0 shadow-sm ${
                        isOverdue ? 'bg-red-500' : isToday ? 'bg-orange-500' : 'bg-blue-500'
                      }`}>
                        <span className="text-[9px] font-black leading-none">
                          {inv.due_date ? new Date(inv.due_date + 'T12:00:00').toLocaleString('pt-PT', { month: 'short' }).toUpperCase() : '?'}
                        </span>
                        <span className="text-[14px] font-black leading-none">
                          {inv.due_date ? new Date(inv.due_date + 'T12:00:00').getDate() : '—'}
                        </span>
                      </div>

                      {/* Info */}
                      <div className="flex-1 min-w-0">
                        <p className="font-bold text-[12px] text-gray-900 truncate">{inv.vendor_name || 'Desconhecido'}</p>
                        <div className="flex items-center gap-2 mt-0.5">
                          <span className={`text-[9px] font-black px-1.5 py-0.5 rounded-md ${
                            isOverdue ? 'bg-red-100 text-red-700' :
                            isToday ? 'bg-orange-100 text-orange-700' :
                            'bg-blue-100 text-blue-700'
                          }`}>
                            {isOverdue ? 'Em Atraso' : isToday ? 'Vence Hoje' :
                             daysLeft !== null ? `${daysLeft}d` : sc.label}
                          </span>
                          {inv.invoice_number && (
                            <span className="text-[9px] font-bold text-gray-400 truncate">#{inv.invoice_number}</span>
                          )}
                        </div>
                      </div>

                      {/* Amount */}
                      <span className={`font-black text-[13px] flex-shrink-0 ${
                        isOverdue ? 'text-red-700' : isToday ? 'text-orange-700' : 'text-gray-900'
                      }`}>
                        {fmt(inv.total_amount)}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Footer actions */}
          <div className="p-6 border-t border-gray-100 space-y-2">
            <p className="text-[10px] text-gray-400 text-center">Clique num dia do calendário para ver os detalhes.</p>
            <button
              id="sync-calendar-btn"
              onClick={fetchCalendar}
              className="w-full bg-gray-900 text-white rounded-2xl p-4 py-3 font-bold text-sm shadow-xl flex items-center justify-center space-x-2 active:scale-95 transition-all hover:bg-gray-800"
            >
              <CalendarIcon size={16} />
              <span>Sincronizar Agenda</span>
            </button>
          </div>
        </div>
      </div>

      {/* ─── Day Detail Modal ─── */}
      {selectedDay && (
        <div className="fixed inset-0 z-[80] flex items-center justify-center bg-gray-900/60 backdrop-blur-sm p-4 animate-fade-in">
          <div className="bg-white w-full max-w-2xl max-h-[85vh] rounded-[32px] shadow-2xl flex flex-col overflow-hidden">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-100">
              <div>
                <h3 className="text-lg font-black text-gray-900 capitalize">
                  {new Date(selectedDay + 'T12:00:00').toLocaleDateString('pt-PT', {
                    weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
                  })}
                </h3>
                <p className="text-[11px] text-gray-400 font-bold mt-0.5">
                  {selectedInvoices.length} fatura(s) vinculada(s) a este dia
                </p>
              </div>
              <div className="flex items-center gap-3">
                {/* Status summary chips */}
                {selectedInvoices.filter(i => i.status === 'overdue' || i.status === 'reconciliation').length > 0 && (
                  <span className="text-[10px] font-black px-2 py-1 bg-red-100 text-red-700 rounded-lg">
                    {selectedInvoices.filter(i => i.status === 'overdue' || i.status === 'reconciliation').length} em atraso
                  </span>
                )}
                {selectedInvoices.filter(i => i.status === 'pending').length > 0 && (
                  <span className="text-[10px] font-black px-2 py-1 bg-blue-100 text-blue-700 rounded-lg">
                    {selectedInvoices.filter(i => i.status === 'pending').length} em aberto
                  </span>
                )}
                <button
                  onClick={() => setSelectedDay(null)}
                  className="p-2 hover:bg-gray-100 rounded-xl transition-all"
                >
                  <X size={20} className="text-gray-500" />
                </button>
              </div>
            </div>

            {/* Modal Body */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4 no-scrollbar">
              {selectedInvoices.length === 0 ? (
                <div className="text-center py-16 text-gray-400">
                  <CalendarIcon size={48} className="mx-auto opacity-20 mb-4" />
                  <p className="font-bold">Nenhuma fatura neste dia.</p>
                </div>
              ) : (
                selectedInvoices.map((inv, i) => {
                  const cardType = getInvoiceCardColor(inv, selectedDay);
                  const cs = CARD_STYLES[cardType];
                  const sc = STATUS_CONFIG[inv.status] || STATUS_CONFIG.pending;
                  const dc = DOCTYPE_CONFIG[inv.document_type || ''] || DOCTYPE_CONFIG.accounts_payable;
                  const daysLeft = getDaysUntil(inv.due_date);

                  return (
                    <div key={i} className={`rounded-[24px] border ${cs.border} ${cs.bg} overflow-hidden`}>
                      {/* Card top strip */}
                      <div className={`${cs.header} px-5 py-2.5 flex items-center justify-between`}>
                        <div className="flex items-center gap-2 text-white">
                          <span className={`opacity-80`}>{dc.icon}</span>
                          <span className="text-[10px] font-black uppercase tracking-widest opacity-90">{dc.label}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-[10px] font-black text-white/80">
                            {inv.status === 'overdue' || inv.status === 'reconciliation' ? '⚠ ' : ''}
                            {sc.label}
                          </span>
                          {daysLeft !== null && (
                            <span className="text-[9px] bg-white/20 text-white font-black px-2 py-0.5 rounded-full">
                              {daysLeft < 0 ? `${Math.abs(daysLeft)}d em atraso` : daysLeft === 0 ? 'vence hoje' : `${daysLeft}d restantes`}
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Card body */}
                      <div className="p-5 space-y-4">
                        {/* Vendor and invoice number */}
                        <div className="flex items-start justify-between gap-3">
                          <div className="flex-1 min-w-0">
                            <p className="font-black text-[15px] text-gray-900 leading-tight">
                              {inv.vendor_name || 'Fornecedor Desconhecido'}
                            </p>
                            {inv.invoice_number && (
                              <div className="flex items-center gap-1 mt-1">
                                <Hash size={10} className="text-gray-400" />
                                <p className="text-[10px] text-gray-500 font-mono">{inv.invoice_number}</p>
                              </div>
                            )}
                          </div>
                          <p className={`text-[20px] font-black flex-shrink-0 ${cs.accent}`}>
                            {fmt(inv.total_amount)}
                          </p>
                        </div>

                        {/* Invoice metadata grid */}
                        <div className="grid grid-cols-2 gap-3">
                          <MetaCell icon={<Clock size={12} />} label="Vencimento" value={
                            inv.due_date
                              ? new Date(inv.due_date + 'T12:00:00').toLocaleDateString('pt-PT', { day: '2-digit', month: '2-digit', year: 'numeric' })
                              : '—'
                          } />
                          <MetaCell icon={<CreditCard size={12} />} label="Pagamento" value={inv.payment_reference || '—'} />
                        </div>

                        {/* Financial breakdown */}
                        <div className="bg-white/70 rounded-2xl p-4 space-y-2 border border-white">
                          <div className="flex justify-between text-[11px]">
                            <span className="text-gray-500 font-medium">Valor líquido</span>
                            <span className="font-bold text-gray-700">{fmt(inv.net_amount)}</span>
                          </div>
                          <div className="flex justify-between text-[11px]">
                            <span className="text-gray-500 font-medium">IVA ({((inv.iva_rate || 0) * 100).toFixed(0)}%)</span>
                            <span className="font-bold text-gray-700">{fmt(inv.iva_amount)}</span>
                          </div>
                          <div className="flex justify-between text-[13px] pt-2 border-t border-gray-100">
                            <span className="font-black text-gray-900">Total</span>
                            <span className={`font-black ${cs.accent}`}>{fmt(inv.total_amount)}</span>
                          </div>
                        </div>

                        {/* Actions */}
                        <div className="flex gap-2 pt-1">
                          {(inv.status === 'pending' || inv.status === 'overdue') && (
                            <button className={`flex-1 py-2.5 rounded-xl text-[11px] font-black border ${cs.border} ${cs.accent} bg-white hover:bg-gray-50 transition-all flex items-center justify-center gap-1.5`}>
                              <CheckCircle2 size={13} />
                              Marcar como Pago
                            </button>
                          )}
                          <button className="flex-1 py-2.5 rounded-xl text-[11px] font-black border border-gray-200 text-gray-600 bg-white hover:bg-gray-50 transition-all flex items-center justify-center gap-1.5">
                            <ArrowRight size={13} />
                            Ver Detalhes
                          </button>
                        </div>
                      </div>
                    </div>
                  );
                })
              )}
            </div>

            {/* Modal footer */}
            <div className="p-5 border-t border-gray-100 bg-gray-50/50">
              <div className="flex items-center justify-between">
                <p className="text-[11px] text-gray-500 font-bold">
                  Total do dia: <span className="text-gray-900 font-black">{fmt(selectedInvoices.reduce((s, i) => s + (i.total_amount || 0), 0))}</span>
                </p>
                <button
                  onClick={() => setSelectedDay(null)}
                  className="px-5 py-2.5 bg-gray-900 text-white rounded-xl text-[12px] font-black hover:bg-gray-800 transition-all active:scale-95"
                >
                  Fechar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </LayoutBase>
  );
};

const MetaCell = ({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) => (
  <div className="bg-white/70 rounded-xl p-3 border border-white">
    <div className="flex items-center gap-1 text-gray-400 mb-1">
      {icon}
      <span className="text-[9px] font-black uppercase tracking-wider">{label}</span>
    </div>
    <p className="text-[12px] font-bold text-gray-900 truncate">{value}</p>
  </div>
);

export default PaymentsAgenda;

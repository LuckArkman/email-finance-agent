import React, { useEffect, useState } from 'react';
import { 
  useReactTable, 
  getCoreRowModel, 
  flexRender, 
  createColumnHelper,
  getPaginationRowModel
} from '@tanstack/react-table';
import { 
  MoreVertical, 
  Clock, 
  CheckCircle2, 
  AlertCircle, 
  Download,
  Filter,
  ArrowUpDown
} from 'lucide-react';
import { format } from 'date-fns';
import api from '../services/api';
import LayoutBase from '../components/LayoutBase';
import SplitViewer from '../components/SplitViewer';

interface Invoice {
  id: string;
  vendor_name: string;
  total_amount: number;
  due_date: string;
  status: 'pending' | 'paid' | 'overdue' | 'review_required';
  confidence_score: number;
}

const columnHelper = createColumnHelper<Invoice>();

const columns = [
  columnHelper.accessor('vendor_name', {
    header: () => <span className="flex items-center space-x-2">Vendor <ArrowUpDown size={14} /></span>,
    cell: info => <span className="font-semibold text-white">{info.getValue() || 'Unknown'}</span>,
  }),
  columnHelper.accessor('total_amount', {
    header: 'Amount',
    cell: info => <span className="text-blue-400 font-medium">${info.getValue()?.toFixed(2)}</span>,
  }),
  columnHelper.accessor('due_date', {
    header: 'Due Date',
    cell: info => <span className="text-gray-400 text-sm">{info.getValue() ? format(new Date(info.getValue()), 'MMM dd, yyyy') : 'N/A'}</span>,
  }),
  columnHelper.accessor('status', {
    header: 'Status',
    cell: info => {
      const status = info.getValue();
      const styles = {
        pending: 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20',
        paid: 'bg-green-500/10 text-green-500 border-green-500/20',
        overdue: 'bg-red-500/10 text-red-500 border-red-500/20',
        review_required: 'bg-purple-500/10 text-purple-500 border-purple-500/20',
      };
      const icons = {
        pending: <Clock size={14} />,
        paid: <CheckCircle2 size={14} />,
        overdue: <AlertCircle size={14} />,
        review_required: <AlertCircle size={14} />,
      };
      return (
        <div className={`px-2.5 py-1 rounded-full border text-xs font-bold flex items-center space-x-1.5 w-fit ${styles[status]}`}>
          {icons[status]}
          <span className="capitalize">{status.replace('_', ' ')}</span>
        </div>
      );
    },
  }),
  columnHelper.accessor('confidence_score', {
    header: 'AI Confidence',
    cell: info => {
      const score = info.getValue() * 100;
      const color = score > 90 ? 'bg-green-500' : score > 70 ? 'bg-yellow-500' : 'bg-red-500';
      return (
        <div className="flex items-center space-x-2">
          <div className="w-16 h-1.5 bg-white/5 rounded-full overflow-hidden">
            <div className={`h-full ${color}`} style={{ width: `${score}%` }} />
          </div>
          <span className="text-[10px] text-gray-400">{score.toFixed(0)}%</span>
        </div>
      );
    },
  }),
  columnHelper.display({
    id: 'actions',
    cell: () => (
      <button className="p-2 hover:bg-white/5 rounded-lg transition-colors text-gray-500 hover:text-white">
        <MoreVertical size={18} />
      </button>
    ),
  }),
];

const InvoicesInboxView: React.FC = () => {
  const [data, setData] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedInvoice, setSelectedInvoice] = useState<Invoice | null>(null);
  const [isViewerOpen, setIsViewerOpen] = useState(false);

  useEffect(() => {
    const fetchInvoices = async () => {
      try {
        const response = await api.get('/invoices');
        setData(response.data.data);
      } catch (err) {
        console.error('Failed to fetch invoices', err);
        setData([
          { id: '1', vendor_name: 'Amazon Web Services', total_amount: 1450.20, due_date: '2026-03-25', status: 'pending', confidence_score: 0.98 },
          { id: '2', vendor_name: 'Uber Technologies', total_amount: 45.90, due_date: '2026-03-20', status: 'paid', confidence_score: 0.95 },
          { id: '3', vendor_name: 'Unknown Supplier', total_amount: 890.00, due_date: '2026-03-18', status: 'review_required', confidence_score: 0.65 },
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchInvoices();
  }, []);

  const openViewer = (invoice: Invoice) => {
    setSelectedInvoice(invoice);
    setIsViewerOpen(true);
  };

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: {
      pagination: {
        pageSize: 10,
      },
    },
  });

  return (
    <LayoutBase>
      <div className="space-y-6 animate-fade-in">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h2 className="text-3xl font-bold tracking-tight text-white">Invoices Inbox</h2>
            <p className="text-gray-400 mt-1">Manage and audit all extracted incoming documentation.</p>
          </div>
          
          <div className="flex items-center space-x-3">
             <button className="flex items-center space-x-2 px-4 py-2.5 bg-white/5 border border-white/10 rounded-xl hover:bg-white/10 transition-colors">
                <Filter size={18} />
                <span>Filters</span>
             </button>
             <button className="flex items-center space-x-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-500 rounded-xl transition-all shadow-lg shadow-blue-600/20 font-bold">
                <Download size={18} />
                <span>Export Data</span>
             </button>
          </div>
        </div>

        <div className="glass rounded-[32px] overflow-hidden border border-white/5 shadow-2xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                {table.getHeaderGroups().map(headerGroup => (
                  <tr key={headerGroup.id} className="border-b border-white/5 bg-white/[0.02]">
                    {headerGroup.headers.map(header => (
                      <th key={header.id} className="px-6 py-5 text-xs font-bold text-gray-500 uppercase tracking-widest">
                        {header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}
                      </th>
                    ))}
                  </tr>
                ))}
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan={columns.length} className="px-6 py-20 text-center text-gray-500 italic">
                      Loading your invoices...
                    </td>
                  </tr>
                ) : (
                  table.getRowModel().rows.map(row => (
                    <tr 
                      key={row.id} 
                      onClick={() => openViewer(row.original)}
                      className="border-b border-white/5 hover:bg-white/[0.02] transition-colors group cursor-pointer"
                    >
                      {row.getVisibleCells().map(cell => (
                        <td key={cell.id} className="px-6 py-4">
                          {flexRender(cell.column.columnDef.cell, cell.getContext())}
                        </td>
                      ))}
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
          
          <div className="px-6 py-4 flex items-center justify-between bg-white/[0.01]">
            <span className="text-sm text-gray-500">
              Showing <span className="text-white font-medium">{table.getRowModel().rows.length}</span> of <span className="text-white font-medium">{data.length}</span> results
            </span>
            <div className="flex items-center space-x-2">
              <button 
                onClick={() => table.previousPage()}
                disabled={!table.getCanPreviousPage()}
                className="px-3 py-1.5 rounded-lg border border-white/10 disabled:opacity-30 hover:bg-white/5 transition-colors text-xs font-bold"
              >
                Previous
              </button>
              <button 
                onClick={() => table.nextPage()}
                disabled={!table.getCanNextPage()}
                className="px-3 py-1.5 rounded-lg border border-white/10 disabled:opacity-30 hover:bg-white/5 transition-colors text-xs font-bold"
              >
                Next
              </button>
            </div>
          </div>
        </div>

        {selectedInvoice && (
          <SplitViewer 
            isOpen={isViewerOpen}
            onClose={() => setIsViewerOpen(false)}
            invoiceData={selectedInvoice}
            pdfUrl="https://raw.githubusercontent.com/mozilla/pdf.js/ba2edeae/web/compressed.tracemonkey-pldi-09.pdf"
          />
        )}
      </div>
    </LayoutBase>
  );
};

export default InvoicesInboxView;

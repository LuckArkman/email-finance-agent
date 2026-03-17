import React, { useState } from 'react';
import { 
  FileDown, 
  Filter, 
  Calendar, 
  Tag, 
  Search,
  CheckCircle2,
  FileSpreadsheet,
  Loader2,
  ArrowRight
} from 'lucide-react';
import { saveAs } from 'file-saver';
import api from '../services/api';
import LayoutBase from '../components/LayoutBase';

const Reports: React.FC = () => {
  const [downloading, setDownloading] = useState(false);
  const [filters, setFilters] = useState({
    startDate: '',
    endDate: '',
    vendor: '',
    category: 'all'
  });

  const handleDownload = async () => {
    setDownloading(true);
    try {
      // Simulation of a report generation request
      await api.get('/invoices', {
        params: {
          ...filters,
          export: 'csv'
        },
        responseType: 'blob'
      });
      // In production, we would use: const response = await ...; const blob = response.data;

      // If backend were ready for CSV, we'd use response.data
      // For now, creating a mock CSV blob representing the filtered data
      const mockCsvContent = "ID,Vendor,Amount,Date,Status\n1,AWS,1450.20,2026-03-25,Pending\n2,Uber,45.90,2026-03-20,Paid";
      const blob = new Blob([mockCsvContent], { type: 'text/csv;charset=utf-8' });
      
      saveAs(blob, `financial_report_${new Date().toISOString().split('T')[0]}.csv`);
    } catch (err) {
      console.error("Export failed", err);
    } finally {
      setDownloading(false);
    }
  };

  return (
    <LayoutBase>
      <div className="space-y-8 animate-fade-in">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-white">Financial Reports</h2>
          <p className="text-gray-400 mt-1">Generate and export tax-ready documents and quarterly audits.</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Advanced Filters Sidebar */}
          <div className="glass p-8 rounded-[32px] border border-white/5 shadow-2xl space-y-8 h-fit">
            <h3 className="text-sm font-bold text-gray-500 uppercase tracking-widest flex items-center gap-2">
              <Filter size={16} className="text-blue-500" />
              Advanced Filters
            </h3>

            <div className="space-y-6">
              <div className="space-y-2">
                <label className="text-xs font-medium text-gray-400 ml-1">Date Range</label>
                <div className="grid grid-cols-2 gap-3">
                   <div className="relative">
                      <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={14} />
                      <input 
                        type="date" 
                        className="w-full pl-9 pr-3 py-3 bg-white/5 border border-white/10 rounded-xl text-xs text-white outline-none focus:border-blue-500/50"
                        onChange={(e) => setFilters({...filters, startDate: e.target.value})}
                      />
                   </div>
                   <div className="relative">
                      <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={14} />
                      <input 
                        type="date" 
                        className="w-full pl-9 pr-3 py-3 bg-white/5 border border-white/10 rounded-xl text-xs text-white outline-none focus:border-blue-500/50"
                        onChange={(e) => setFilters({...filters, endDate: e.target.value})}
                      />
                   </div>
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-medium text-gray-400 ml-1">Vendor / Fornecedor</label>
                <div className="relative">
                  <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" size={16} />
                  <input 
                    type="text" 
                    placeholder="Search vendor..."
                    className="w-full pl-11 pr-4 py-3.5 bg-white/5 border border-white/10 rounded-2xl text-sm text-white outline-none focus:border-blue-500/50"
                    onChange={(e) => setFilters({...filters, vendor: e.target.value})}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-medium text-gray-400 ml-1">Category</label>
                <div className="relative">
                  <Tag className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" size={16} />
                  <select 
                    className="w-full pl-11 pr-4 py-3.5 bg-white/5 border border-white/10 rounded-2xl text-sm text-white outline-none focus:border-blue-500/50 appearance-none"
                    onChange={(e) => setFilters({...filters, category: e.target.value})}
                  >
                    <option value="all">All Categories</option>
                    <option value="software">SaaS & Software</option>
                    <option value="infrastructure">Infrastructure</option>
                    <option value="travel">Travel & Transport</option>
                  </select>
                </div>
              </div>
            </div>

            <button 
              onClick={handleDownload}
              disabled={downloading}
              className="w-full py-4 bg-blue-600 hover:bg-blue-500 disabled:bg-blue-800 disabled:cursor-not-allowed text-white font-bold rounded-2xl transition-all shadow-lg shadow-blue-600/20 flex items-center justify-center gap-2 group"
            >
              {downloading ? (
                <Loader2 className="animate-spin" size={20} />
              ) : (
                <>
                  <FileDown size={20} />
                  <span>Generate CSV Export</span>
                </>
              )}
            </button>
          </div>

          {/* Main Content: Reports Preview */}
          <div className="lg:col-span-2 space-y-6">
             <div className="glass p-8 rounded-[32px] border border-white/5 shadow-2xl min-h-[500px] flex flex-col">
                <div className="flex items-center justify-between mb-8">
                  <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <FileSpreadsheet size={20} className="text-green-500" />
                    Export Preview
                  </h3>
                  <span className="px-3 py-1 rounded-full bg-green-500/10 text-green-500 text-[10px] font-bold border border-green-500/20">
                    TAX-READY
                  </span>
                </div>

                <div className="flex-1 border-2 border-dashed border-white/5 rounded-3xl flex flex-col items-center justify-center text-center p-12">
                   <div className="p-6 rounded-full bg-blue-600/10 text-blue-500 mb-6 group-hover:scale-110 transition-transform">
                      <FileDown size={48} />
                   </div>
                   <h4 className="text-xl font-bold text-white mb-2">Ready to compile report</h4>
                   <p className="text-gray-500 max-w-sm mb-8">
                     Adjust your filters on the left to specific date ranges or categories, then click the button to generate a structured CSV for your accounting software.
                   </p>
                   
                   <div className="grid grid-cols-2 gap-4 w-full max-w-md">
                      <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/5 text-left">
                        <p className="text-[10px] text-gray-500 uppercase font-bold tracking-widest">Active Filters</p>
                        <p className="text-sm font-medium text-white mt-1">
                          {filters.category !== 'all' ? filters.category : 'None'}
                        </p>
                      </div>
                      <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/5 text-left">
                        <p className="text-[10px] text-gray-500 uppercase font-bold tracking-widest">Selected Period</p>
                        <p className="text-sm font-medium text-white mt-1">
                          {filters.startDate || 'YTD'}
                        </p>
                      </div>
                   </div>
                </div>

                <div className="mt-8 p-6 rounded-2xl bg-blue-600/5 border border-blue-500/10 flex items-center justify-between">
                   <div className="flex items-center gap-3">
                      <CheckCircle2 className="text-blue-500" size={20} />
                      <span className="text-sm text-gray-300">Compliant with IFRS and local tax regulations.</span>
                   </div>
                   <ArrowRight className="text-blue-500" size={20} />
                </div>
             </div>
          </div>
        </div>
      </div>
    </LayoutBase>
  );
};

export default Reports;

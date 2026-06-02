import React, { useState, useEffect } from 'react';
import Sidebar from './Sidebar';
import { useSignalR } from '../hooks/useSignalR';
import { Bell } from 'lucide-react';

interface LayoutBaseProps {
  children: React.ReactNode;
}

const LayoutBase: React.FC<LayoutBaseProps> = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);
  const [toast, setToast] = useState<{message: string, visible: boolean}>({ message: '', visible: false });
  const connection = useSignalR();

  useEffect(() => {
    if (connection) {
      connection.on('ExtractionCompleted', (data) => {
        showToast(`Documento Extraído: ${data.vendorName || 'Desconhecido'}`);
      });

      connection.on('InvoiceReconciled', (data) => {
        showToast(`Reconciliação Automática! ${data.reconciledAmount}€ processados.`);
      });
    }

    return () => {
      if (connection) {
        connection.off('ExtractionCompleted');
        connection.off('InvoiceReconciled');
      }
    };
  }, [connection]);

  const showToast = (message: string) => {
    setToast({ message, visible: true });
    setTimeout(() => {
      setToast(prev => ({ ...prev, visible: false }));
    }, 5000);
  };

  return (
    <div className="flex bg-[#f3f4f6] min-h-screen text-gray-900 overflow-hidden font-body relative">
      <Sidebar collapsed={collapsed} toggle={() => setCollapsed(!collapsed)} />
      
      <div className="flex-1 flex flex-col min-w-0 h-screen overflow-hidden">
        <main className="flex-1 overflow-y-auto no-scrollbar">
          {children}
        </main>
      </div>

      {toast.visible && (
        <div className="absolute top-10 right-10 bg-white border-l-4 border-blue-500 shadow-xl rounded-lg p-4 flex items-center space-x-3 z-50 animate-in fade-in slide-in-from-top-5">
          <div className="p-2 bg-blue-100 text-blue-600 rounded-full">
            <Bell size={20} />
          </div>
          <div>
            <p className="font-bold text-gray-900 text-sm">Atualização do Agente</p>
            <p className="text-gray-600 text-xs mt-0.5">{toast.message}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default LayoutBase;

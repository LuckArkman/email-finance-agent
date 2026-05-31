import React, { useEffect, useState } from 'react';
import { X, Loader2, Download } from 'lucide-react';
import api from '../services/api';

interface DocumentViewerModalProps {
  invoiceId: string;
  filename: string;
  onClose: () => void;
}

const DocumentViewerModal: React.FC<DocumentViewerModalProps> = ({ invoiceId, filename, onClose }) => {
  const [fileUrl, setFileUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDocument = async () => {
      try {
        setLoading(true);
        // Fetch the file as a blob so that the Authorization header is included
        const response = await api.get(`/invoices/${invoiceId}/file`, {
          responseType: 'blob',
        });
        
        // Create an object URL from the blob
        const contentType = (response.headers['content-type'] as string) || 'application/pdf';
        const blob = new Blob([response.data], { type: contentType });
        const objectUrl = URL.createObjectURL(blob);
        setFileUrl(objectUrl);
      } catch (err) {
        console.error('Failed to load document', err);
        setError('Não foi possível carregar o documento. Pode ter sido apagado ou não está disponível.');
      } finally {
        setLoading(false);
      }
    };

    fetchDocument();

    return () => {
      if (fileUrl) {
        URL.revokeObjectURL(fileUrl);
      }
    };
  }, [invoiceId]);

  const isImage = filename.match(/\.(jpeg|jpg|gif|png)$/i) != null;
  const isPdf = filename.match(/\.(pdf)$/i) != null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-gray-900/80 backdrop-blur-sm p-4 animate-fade-in">
      <div className="bg-white w-full max-w-5xl h-[90vh] rounded-3xl shadow-2xl flex flex-col overflow-hidden relative">
        
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-100 bg-white">
          <div className="flex items-center space-x-3">
            <h3 className="font-bold text-gray-900">{filename}</h3>
          </div>
          <div className="flex items-center space-x-2">
            {fileUrl && (
              <a 
                href={fileUrl} 
                download={filename}
                className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors flex items-center space-x-2"
              >
                <Download size={20} />
                <span className="text-sm font-bold">Transferir</span>
              </a>
            )}
            <button 
              onClick={onClose} 
              className="p-2 text-gray-400 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X size={24} />
            </button>
          </div>
        </div>

        {/* Content Area */}
        <div className="flex-1 bg-gray-50 flex items-center justify-center p-4 relative overflow-auto">
          {loading && (
            <div className="flex flex-col items-center space-y-4">
              <Loader2 size={40} className="animate-spin text-blue-500" />
              <p className="text-gray-500 font-bold">A carregar documento...</p>
            </div>
          )}

          {error && !loading && (
            <div className="text-center space-y-4">
              <p className="text-red-500 font-bold">{error}</p>
            </div>
          )}

          {fileUrl && !loading && !error && (
            <div className="w-full h-full flex items-center justify-center">
              {isImage ? (
                <img 
                  src={fileUrl} 
                  alt={filename} 
                  className="max-w-full max-h-full object-contain rounded-lg shadow-sm border border-gray-200"
                />
              ) : isPdf ? (
                <iframe 
                  src={`${fileUrl}#toolbar=0`} 
                  className="w-full h-full rounded-lg shadow-sm border border-gray-200"
                  title={filename}
                />
              ) : (
                <iframe 
                  src={fileUrl} 
                  className="w-full h-full rounded-lg shadow-sm border border-gray-200 bg-white"
                  title={filename}
                />
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DocumentViewerModal;

import React, { useState } from 'react';
import Sidebar from './Sidebar';

interface LayoutBaseProps {
  children: React.ReactNode;
}

const LayoutBase: React.FC<LayoutBaseProps> = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className="flex bg-[#f3f4f6] min-h-screen text-gray-900 overflow-hidden font-body">
      <Sidebar collapsed={collapsed} toggle={() => setCollapsed(!collapsed)} />
      
      <div className="flex-1 flex flex-col min-w-0 h-screen overflow-hidden">
        <main className="flex-1 overflow-y-auto no-scrollbar">
          {children}
        </main>
      </div>
    </div>
  );
};

export default LayoutBase;

import React, { useState, useEffect } from 'react';
import Sidebar from './Sidebar';
import NavBar from './NavBar';

interface LayoutBaseProps {
  children: React.ReactNode;
}

const LayoutBase: React.FC<LayoutBaseProps> = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);
  const [darkMode, setDarkMode] = useState(true);

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  return (
    <div className="flex bg-background min-h-screen text-foreground transition-colors duration-300">
      <Sidebar collapsed={collapsed} toggle={() => setCollapsed(!collapsed)} />
      
      <div className="flex-1 flex flex-col min-w-0">
        <NavBar darkMode={darkMode} toggleTheme={() => setDarkMode(!darkMode)} />
        
        <main className="flex-1 p-8 overflow-y-auto animate-fade-in">
          {children}
        </main>
      </div>
    </div>
  );
};

export default LayoutBase;

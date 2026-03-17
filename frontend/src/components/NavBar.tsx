import React from 'react';
import { Bell, Search, User, Sun, Moon } from 'lucide-react';

interface NavBarProps {
  darkMode: boolean;
  toggleTheme: () => void;
}

const NavBar: React.FC<NavBarProps> = ({ darkMode, toggleTheme }) => {
  return (
    <header className="h-20 glass border-b px-8 flex items-center justify-between sticky top-0 z-10 backdrop-blur-lg">
      <div className="relative w-96 group">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-primary transition-colors" size={18} />
        <input 
          type="text" 
          placeholder="Search invoices, vendors..."
          className="w-full pl-10 pr-4 py-2 bg-gray-100/50 dark:bg-gray-800/50 border border-transparent focus:border-primary/50 rounded-xl outline-none transition-all"
        />
      </div>

      <div className="flex items-center space-x-4">
        <button 
          onClick={toggleTheme}
          className="p-2.5 rounded-xl bg-gray-100 dark:bg-gray-800 hover:scale-110 transition-transform text-gray-500 hover:text-primary"
        >
          {darkMode ? <Sun size={20} /> : <Moon size={20} />}
        </button>

        <button className="p-2.5 rounded-xl bg-gray-100 dark:bg-gray-800 hover:scale-110 transition-transform text-gray-500 relative">
          <Bell size={20} />
          <span className="absolute top-2 right-2 w-2.5 h-2.5 bg-red-500 rounded-full border-2 border-white dark:border-gray-800"></span>
        </button>

        <div className="flex items-center space-x-3 pl-4 border-l border-gray-200 dark:border-gray-800">
          <div className="text-right hidden sm:block">
            <p className="text-sm font-bold">Admin Account</p>
            <p className="text-xs text-gray-500">Finance Manager</p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-blue-400 flex items-center justify-center text-white font-bold shadow-lg shadow-primary/20 cursor-pointer hover:scale-105 transition-transform">
            <User size={20} />
          </div>
        </div>
      </div>
    </header>
  );
};

export default NavBar;

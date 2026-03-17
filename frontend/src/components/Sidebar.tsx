import React from 'react';
import { 
  LayoutDashboard, 
  FileText, 
  Settings, 
  ChevronLeft, 
  ChevronRight,
  LogOut,
  BarChart3,
  AlertTriangle,
  FileSpreadsheet
} from 'lucide-react';
import { motion } from 'framer-motion';
import { Link, useLocation } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

interface SidebarProps {
  collapsed: boolean;
  toggle: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ collapsed, toggle }) => {
  const location = useLocation();
  const { logout } = useAuthStore();
  
  const menuItems = [
    { name: 'Dashboard', icon: <LayoutDashboard size={20} />, path: '/' },
    { name: 'Invoices', icon: <FileText size={20} />, path: '/invoices' },
    { name: 'Resolution', icon: <AlertTriangle size={20} />, path: '/resolution' },
    { name: 'Analytics', icon: <BarChart3 size={20} />, path: '/analytics' },
    { name: 'Reports', icon: <FileSpreadsheet size={20} />, path: '/reports' },
    { name: 'Settings', icon: <Settings size={20} />, path: '/settings' },
  ];

  return (
    <motion.div 
      animate={{ width: collapsed ? 80 : 260 }}
      className="h-screen glass border-r flex flex-col transition-all duration-300 relative z-20 border-white/5"
    >
      <div className="p-6 flex items-center justify-between">
        {!collapsed && (
          <motion.h1 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-xl font-bold bg-gradient-to-r from-blue-400 to-blue-600 bg-clip-text text-transparent"
          >
            LuckArkman
          </motion.h1>
        )}
        <button 
          onClick={toggle}
          className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 hover:scale-110 transition-all text-gray-400"
        >
          {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
        </button>
      </div>

      <nav className="flex-1 px-4 mt-4 space-y-2">
        {menuItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.name}
              to={item.path}
              className={`w-full flex items-center p-3 rounded-xl transition-all duration-200 group ${
                isActive 
                ? 'bg-blue-600/10 text-blue-500 border border-blue-500/20' 
                : 'text-gray-500 hover:bg-white/5 hover:text-gray-300'
              }`}
            >
              <span className={`transition-colors ${isActive ? 'text-blue-500' : 'group-hover:text-blue-400'}`}>
                {item.icon}
              </span>
              {!collapsed && (
                <motion.span 
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="ml-4 font-medium"
                >
                  {item.name}
                </motion.span>
              )}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-white/10">
        <button 
          onClick={logout}
          className="w-full flex items-center p-3 rounded-xl text-red-500/70 hover:bg-red-500/10 hover:text-red-500 transition-colors"
        >
          <LogOut size={20} />
          {!collapsed && <span className="ml-4 font-medium">Logout</span>}
        </button>
      </div>
    </motion.div>
  );
};

export default Sidebar;

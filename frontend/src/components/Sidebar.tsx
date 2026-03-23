import React from 'react';
import { 
  Inbox, 
  Clock, 
  Star,
  MessageCircle,
  Mail,
  Upload,
  Calendar,
  ShieldCheck,
  BarChart3,
  FileText,
  ChevronLeft,
  ChevronRight,
  Zap,
  Lock
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
  const {} = useAuthStore();
  
  const sections = [
    {
      title: 'PLATAFORMA',
      items: [
        { name: 'Dashboard', icon: <Inbox size={18} />, path: '/' },
        { name: 'Entrada (Emails)', icon: <Mail size={18} />, path: '/inbox' },
        { name: 'Arquivo Digital', icon: <FileText size={18} />, path: '/invoices' },
        { name: 'Agenda Pagamentos', icon: <Calendar size={18} />, path: '/agenda' },
        { name: 'Reconciliação', icon: <ShieldCheck size={18} />, path: '/reconcile' },
        { name: 'Vincular Email', icon: <Lock size={18} />, path: '/email-link' },
        { name: 'Relatórios', icon: <BarChart3 size={18} />, path: '/analytics' },
      ]
    },
    {
      title: 'ORIGENS',
      items: [
        { name: 'WhatsApp (Fotos)', icon: <MessageCircle size={18} />, path: '/whatsapp' },
        { name: 'Email (Anexos)', icon: <Mail size={18} />, path: '/inbox' },
        { name: 'Upload Manual', icon: <Upload size={18} />, path: '/upload' },
      ]
    },
    {
      title: 'FAVORITOS',
      items: [
        { name: 'Recentes', icon: <Clock size={18} />, path: '/recent' },
        { name: 'Importantes', icon: <Star size={18} />, path: '/important' },
      ]
    }
  ];

  return (
    <motion.div 
      animate={{ width: collapsed ? 80 : 260 }}
      className="h-screen bg-[#0d1117] border-r border-white/5 flex flex-col transition-all duration-300 relative z-20"
    >
      <div className="p-6 flex items-center justify-between mb-2">
        {!collapsed && (
          <div className="flex items-center space-x-2">
             <div className="flex space-x-1.5 px-2">
                <div className="w-3 h-3 rounded-full bg-red-400" />
                <div className="w-3 h-3 rounded-full bg-yellow-400" />
                <div className="w-3 h-3 rounded-full bg-green-400" />
             </div>
          </div>
        )}
        <button 
          onClick={toggle}
          className="p-1.5 rounded-lg hover:bg-white/5 transition-all text-gray-400"
        >
          {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
        </button>
      </div>

      <nav className="flex-1 px-4 overflow-y-auto no-scrollbar py-2">
        {sections.map((section, idx) => (
          <div key={section.title} className={`${idx !== 0 ? 'mt-8' : ''}`}>
             {!collapsed && (
               <h3 className="text-[10px] font-extrabold text-gray-400 tracking-[0.15em] px-3 mb-3">
                 {section.title}
               </h3>
             )}
             <div className="space-y-1">
               {section.items.map((item) => {
                 const isActive = location.pathname === item.path;
                 return (
                   <Link
                     key={item.name}
                     to={item.path}
                     className={`w-full flex items-center p-2.5 rounded-xl transition-all duration-200 group ${
                       isActive 
                       ? 'bg-white text-blue-600 shadow-sm' 
                       : 'text-gray-400 hover:bg-white/5 hover:text-white'
                     }`}
                   >
                     <span className={`transition-colors flex items-center justify-center w-6 ${isActive ? 'text-blue-500' : 'text-blue-500/70 group-hover:text-blue-500'}`}>
                       {item.icon}
                     </span>
                     {!collapsed && (
                       <motion.span 
                         initial={{ opacity: 0, x: -10 }}
                         animate={{ opacity: 1, x: 0 }}
                         className="ml-3 font-medium text-[13px]"
                       >
                         {item.name}
                       </motion.span>
                     )}
                   </Link>
                 );
               })}
             </div>
          </div>
        ))}
      </nav>

      <div className="p-4 mt-auto">
         <div className="bg-white/5 p-3 rounded-2xl border border-white/10 flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-lg shadow-blue-500/30">
               <Zap size={22} fill="white" />
            </div>
            {!collapsed && (
              <div className="flex flex-col overflow-hidden text-white">
                 <span className="font-bold text-[12px] truncate">Gestor Sustentacódigo</span>
                 <span className="text-[10px] text-green-500 font-medium">Sincronizado</span>
              </div>
            )}
         </div>
      </div>
    </motion.div>
  );
};

export default Sidebar;

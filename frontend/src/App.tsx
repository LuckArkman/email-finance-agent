import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './views/Login';
import Register from './views/Register';
import Dashboard from './views/Dashboard';
import InvoicesInbox from './views/InvoicesInbox';
import PaymentsAgenda from './views/PaymentsAgenda';
import ReconciliacaoBancaria from './views/ReconciliacaoBancaria';
import RelatoriosMetricas from './views/RelatoriosMetricas';
import UniversalInbox from './views/UniversalInbox';
import EmailLinking from './views/EmailLinking';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route 
          path="/" 
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/invoices" 
          element={
            <ProtectedRoute>
              <InvoicesInbox />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/agenda" 
          element={
            <ProtectedRoute>
              <PaymentsAgenda />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/reconcile" 
          element={
            <ProtectedRoute>
              <ReconciliacaoBancaria />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/inbox" 
          element={
            <ProtectedRoute>
              <UniversalInbox />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/email-link" 
          element={
            <ProtectedRoute>
              <EmailLinking />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/analytics" 
          element={
            <ProtectedRoute>
              <RelatoriosMetricas />
            </ProtectedRoute>
          } 
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;

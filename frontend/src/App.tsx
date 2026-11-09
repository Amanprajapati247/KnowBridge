import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { MainDashboard } from './pages/MainDashboard';
import { ProjectWorkspace } from './pages/ProjectWorkspace';
import { IncomingPortal } from './pages/IncomingPortal';
import { IncomingHandoverView } from './pages/IncomingHandoverView';

// Route Guards
const ProtectedRoute: React.FC<{ children: React.ReactNode; requiredRole?: 'PROJECT_LEAD' | 'INCOMING_MEMBER' }> = ({
  children,
  requiredRole
}) => {
  const { user, role, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 text-xs text-slate-500">
        Authenticating session...
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (requiredRole && role !== requiredRole) {
    // If incoming member tries to hit lead workspace, redirect to incoming portal
    if (role === 'INCOMING_MEMBER') {
      return <Navigate to="/incoming" replace />;
    }
  }

  return <>{children}</>;
};

export const AppContent: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Navbar />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Lead Workspace Protected Routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute requiredRole="PROJECT_LEAD">
                <MainDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/projects/:id"
            element={
              <ProtectedRoute requiredRole="PROJECT_LEAD">
                <ProjectWorkspace />
              </ProtectedRoute>
            }
          />

          {/* Incoming Member Protected Routes */}
          <Route
            path="/incoming"
            element={
              <ProtectedRoute>
                <IncomingPortal />
              </ProtectedRoute>
            }
          />
          <Route
            path="/incoming/:id"
            element={
              <ProtectedRoute>
                <IncomingHandoverView />
              </ProtectedRoute>
            }
          />

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </BrowserRouter>
  );
};

export default App;

import { lazy, Suspense } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import Navbar from "./shared/components/Navbar.jsx";
import Toast from "./shared/components/Toast.jsx";
import ErrorBoundary from "./shared/components/ErrorBoundary.jsx";
import Loader from "./shared/components/Loader.jsx";
import NotFound from "./shared/pages/NotFound.jsx";
import { ToastProvider } from "./shared/hooks/useToast.jsx";
import ProtectedRoute from "./modules/authentication/components/ProtectedRoute.jsx";
import { AuthProvider, useAuth } from "./modules/authentication/context/AuthContext.jsx";
import Login from "./modules/authentication/pages/Login.jsx";
import Register from "./modules/authentication/pages/Register.jsx";
import Dashboard from "./modules/workspace/pages/Dashboard.jsx";

const ProjectChat = lazy(() => import("./modules/chat/pages/ProjectChat.jsx"));
const ProjectDetails = lazy(() => import("./modules/workspace/pages/ProjectDetails.jsx"));

function AppLayout() {
  const { user, logout } = useAuth();

  return (
    <>
      <Navbar user={user} onLogout={user ? logout : null} />
      <Toast />
      <ErrorBoundary>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/projects/:id/c/:conversationId"
            element={
              <ProtectedRoute>
                <Suspense fallback={<Loader label="Loading chat..." />}>
                  <ProjectChat />
                </Suspense>
              </ProtectedRoute>
            }
          />
          <Route
            path="/projects/:id/settings"
            element={
              <ProtectedRoute>
                <Suspense fallback={<Loader label="Loading settings..." />}>
                  <ProjectDetails />
                </Suspense>
              </ProtectedRoute>
            }
          />
          <Route
            path="/projects/:id"
            element={
              <ProtectedRoute>
                <Suspense fallback={<Loader label="Loading chat..." />}>
                  <ProjectChat />
                </Suspense>
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </ErrorBoundary>
    </>
  );
}

export default function App() {
  return (
    <ToastProvider>
      <AuthProvider>
        <AppLayout />
      </AuthProvider>
    </ToastProvider>
  );
}

import React from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { CssBaseline } from "@mui/material";
import { useAuth } from "./state/AuthProvider";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import ScansPage from "./pages/ScansPage";
import ScanDetailPage from "./pages/ScanDetailPage";
import HuntingPage from "./pages/HuntingPage";
import HuntingDetailPage from "./pages/HuntingDetailPage";
import SettingsPage from "./pages/SettingsPage";
import AppShell from "./components/AppShell";

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { accessToken } = useAuth();
  if (!accessToken) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <>
      <CssBaseline />
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/"
          element={
            <PrivateRoute>
              <AppShell />
            </PrivateRoute>
          }
        >
          <Route index element={<DashboardPage />} />
          <Route path="scans" element={<ScansPage />} />
          <Route path="scans/:scanId" element={<ScanDetailPage />} />
          <Route path="hunting" element={<HuntingPage />} />
          <Route path="hunting/:sessionId" element={<HuntingDetailPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  );
}


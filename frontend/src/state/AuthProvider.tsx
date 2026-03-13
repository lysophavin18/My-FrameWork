import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import { api, setAuthToken } from "../api/client";

type AuthState = {
  accessToken: string | null;
  refreshToken: string | null;
  user: any | null;
};

type AuthContextValue = AuthState & {
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refresh: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

const STORAGE_KEY = "expl0v1n.auth";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>(() => {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return { accessToken: null, refreshToken: null, user: null };
    try {
      return JSON.parse(raw);
    } catch {
      return { accessToken: null, refreshToken: null, user: null };
    }
  });

  useEffect(() => {
    setAuthToken(state.accessToken);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }, [state.accessToken, state.refreshToken, state.user]);

  async function loadMe(token: string) {
    setAuthToken(token);
    const me = await api.get("/users/me");
    return me.data;
  }

  const value = useMemo<AuthContextValue>(
    () => ({
      ...state,
      login: async (email, password) => {
        const resp = await api.post("/auth/login", { email, password });
        const accessToken = resp.data.access_token as string;
        const refreshToken = resp.data.refresh_token as string;
        const user = await loadMe(accessToken);
        setState({ accessToken, refreshToken, user });
      },
      refresh: async () => {
        if (!state.refreshToken) throw new Error("no_refresh_token");
        const resp = await api.post("/auth/refresh", { refresh_token: state.refreshToken });
        const accessToken = resp.data.access_token as string;
        const refreshToken = resp.data.refresh_token as string;
        const user = await loadMe(accessToken);
        setState({ accessToken, refreshToken, user });
      },
      logout: () => {
        setState({ accessToken: null, refreshToken: null, user: null });
        setAuthToken(null);
        localStorage.removeItem(STORAGE_KEY);
      },
    }),
    [state]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("AuthProvider missing");
  return ctx;
}


import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { api, ensureCsrf, getAuthToken, setAuthToken } from "../api/client";
import type { LoginResponse, Organization, User } from "../types";

interface AuthState {
  user: User | null;
  loading: boolean;
  tenantOverride: number | null;
  organizations: Organization[];
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  setTenantOverride: (id: number | null) => void;
  effectiveTenantId: number | null;
  isReadOnly: boolean;
  canManage: boolean;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [tenantOverride, setTenantOverride] = useState<number | null>(null);
  const [organizations, setOrganizations] = useState<Organization[]>([]);

  useEffect(() => {
    const bootstrap = async () => {
      try {
        if (!getAuthToken()) await ensureCsrf();
        const me = await api<User>("/auth/me/");
        setUser(me);
        if (me.role === "super_admin") {
          const data = await api<{ results: Organization[] } | Organization[]>("/organizations/");
          setOrganizations(Array.isArray(data) ? data : data.results);
        }
      } catch {
        setAuthToken(null);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };
    bootstrap();
  }, []);

  const login = useCallback(
    async (username: string, password: string) => {
      await ensureCsrf();
      const me = await api<LoginResponse>("/auth/login/", {
        method: "POST",
        body: JSON.stringify({ username, password }),
      });
      setAuthToken(me.token);
      setUser(me);
      if (me.role === "super_admin") {
        const orgs = await api<{ results: Organization[] } | Organization[]>("/organizations/");
        setOrganizations(Array.isArray(orgs) ? orgs : orgs.results);
      }
    },
    [],
  );

  const logout = useCallback(async () => {
    try {
      await api("/auth/logout/", { method: "POST" });
    } finally {
      setAuthToken(null);
    }
    setUser(null);
    setTenantOverride(null);
    setOrganizations([]);
  }, []);

  const effectiveTenantId = user?.role === "super_admin" ? tenantOverride : user?.tenant ?? null;

  const value = useMemo(
    () => ({
      user,
      loading,
      tenantOverride,
      organizations,
      login,
      logout,
      setTenantOverride,
      effectiveTenantId,
      isReadOnly: user?.role === "fleet_auditor",
      canManage: user?.role === "branch_manager" || user?.role === "super_admin",
    }),
    [user, loading, tenantOverride, organizations, login, logout, effectiveTenantId],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

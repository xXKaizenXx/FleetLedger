import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { api, ensureCsrf } from "../api/client";
import type { Organization, User } from "../types";

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
    ensureCsrf()
      .then(() => api<User>("/auth/me/"))
      .then((me) => {
        setUser(me);
        if (me.role === "super_admin") {
          return api<{ results: Organization[] } | Organization[]>("/organizations/").then((data) => {
            setOrganizations(Array.isArray(data) ? data : data.results);
          });
        }
      })
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

  const login = useCallback(
    async (username: string, password: string) => {
      await ensureCsrf();
      const me = await api<User>("/auth/login/", {
        method: "POST",
        body: JSON.stringify({ username, password }),
      });
      setUser(me);
      if (me.role === "super_admin") {
        const orgs = await api<{ results: Organization[] } | Organization[]>("/organizations/");
        setOrganizations(Array.isArray(orgs) ? orgs : orgs.results);
      }
    },
    [],
  );

  const logout = useCallback(async () => {
    await api("/auth/logout/", { method: "POST" });
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

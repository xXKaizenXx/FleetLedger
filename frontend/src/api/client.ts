const API = (import.meta.env.VITE_API_BASE_URL as string | undefined) || "/api/v1";

const TOKEN_KEY = "fleetledger_auth_token";

/** In-memory token for cross-origin deploys (dashboard ≠ API host). */
let csrfTokenFromApi: string | null = null;

export function getAuthToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setAuthToken(token: string | null): void {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token);
  } else {
    localStorage.removeItem(TOKEN_KEY);
  }
}

function getCsrfToken(): string | null {
  if (csrfTokenFromApi) return csrfTokenFromApi;
  const match = document.cookie.match(/csrftoken=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : null;
}

export async function ensureCsrf(): Promise<void> {
  if (getAuthToken()) return;
  const res = await fetch(`${API}/auth/csrf/`, { credentials: "include" });
  if (!res.ok) {
    throw new Error("Could not initialize CSRF protection.");
  }
  const data = (await res.json()) as { csrfToken?: string };
  if (data.csrfToken) {
    csrfTokenFromApi = data.csrfToken;
  }
}

type RequestOptions = RequestInit & { tenantId?: number | null };

export async function api<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { tenantId, headers, ...rest } = options;
  const csrf = getCsrfToken();
  const token = getAuthToken();
  const res = await fetch(`${API}${path}`, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Token ${token}` } : {}),
      ...(csrf ? { "X-CSRFToken": csrf } : {}),
      ...(tenantId ? { "X-Tenant-ID": String(tenantId) } : {}),
      ...headers,
    },
    ...rest,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const detail = (body as { detail?: string }).detail || res.statusText;
    throw new Error(detail);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

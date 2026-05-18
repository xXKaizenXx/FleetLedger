const API = (import.meta.env.VITE_API_BASE_URL as string | undefined) || "/api/v1";

function getCsrfToken(): string | null {
  const match = document.cookie.match(/csrftoken=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : null;
}

export async function ensureCsrf(): Promise<void> {
  await fetch(`${API}/auth/csrf/`, { credentials: "include" });
}

type RequestOptions = RequestInit & { tenantId?: number | null };

export async function api<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { tenantId, headers, ...rest } = options;
  const csrf = getCsrfToken();
  const res = await fetch(`${API}${path}`, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
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

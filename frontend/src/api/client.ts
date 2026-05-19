const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '';

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    let detail = `API request failed: ${response.status}`;
    try {
      const body = await response.json();
      if (body?.detail) detail = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail);
    } catch {
      // Keep fallback message.
    }
    throw new Error(detail);
  }
  return response.json() as Promise<T>;
}

export function queryString(params: Record<string, string | number | boolean | null | undefined>) {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== '' && value !== false) search.set(key, String(value));
  }
  const text = search.toString();
  return text ? `?${text}` : '';
}

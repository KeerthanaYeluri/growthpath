import { getToken, clearAuth } from './auth'

const API = "/api"

export function authHeaders(): Record<string, string> {
  const t = getToken()
  return t
    ? { Authorization: `Bearer ${t}`, "Content-Type": "application/json" }
    : { "Content-Type": "application/json" }
}

export async function apiFetch(url: string, options: RequestInit = {}): Promise<Response> {
  const res = await fetch(`${API}${url}`, {
    ...options,
    headers: { ...authHeaders(), ...(options.headers as Record<string, string> || {}) },
  })
  if (res.status === 401) {
    clearAuth()
    window.location.reload()
    throw new Error("Session expired")
  }
  return res
}

export { API }

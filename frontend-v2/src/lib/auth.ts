export function getToken(): string | null {
  return localStorage.getItem("gp_token")
}

export function setToken(t: string) {
  localStorage.setItem("gp_token", t)
}

export function clearAuth() {
  localStorage.removeItem("gp_token")
  localStorage.removeItem("gp_user")
}

export function getUser(): any {
  try {
    return JSON.parse(localStorage.getItem("gp_user") || "null")
  } catch {
    return null
  }
}

export function setUser(u: any) {
  localStorage.setItem("gp_user", JSON.stringify(u))
}

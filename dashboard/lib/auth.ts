const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface User {
  id: string
  email: string
  name: string
  role: string
  tenant_id: string
}

export interface Tenant {
  id: string
  name: string
  plan: string
}

export interface AuthState {
  user: User | null
  tenant: Tenant | null
  isAuthenticated: boolean
  isLoading: boolean
}

// Token storage
const TOKEN_KEY = 'genesis_access_token'
const REFRESH_KEY = 'genesis_refresh_token'

export function getAccessToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem(TOKEN_KEY)
}

export function getRefreshToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem(REFRESH_KEY)
}

function setTokens(access: string, refresh: string) {
  localStorage.setItem(TOKEN_KEY, access)
  localStorage.setItem(REFRESH_KEY, refresh)
}

export function clearTokens() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(REFRESH_KEY)
}

// Auth headers for API calls
export function authHeaders(): Record<string, string> {
  const token = getAccessToken()
  if (token) {
    return { Authorization: `Bearer ${token}` }
  }
  return {}
}

// Authenticated fetch wrapper
export async function authFetch(url: string, options: RequestInit = {}): Promise<Response> {
  const headers = {
    ...authHeaders(),
    ...(options.headers || {}),
  }

  let res = await fetch(url, { ...options, headers })

  // If 401, try refreshing the token
  if (res.status === 401) {
    const refreshed = await refreshAccessToken()
    if (refreshed) {
      const retryHeaders = {
        ...authHeaders(),
        ...(options.headers || {}),
      }
      res = await fetch(url, { ...options, headers: retryHeaders })
    }
  }

  return res
}

// Register
export async function register(
  email: string,
  password: string,
  name: string,
  tenantName?: string
): Promise<{ user: User; tenant: Tenant } | null> {
  const res = await fetch(`${API_URL}/api/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, name, tenant_name: tenantName }),
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Registration failed')
  }

  const data = await res.json()
  setTokens(data.access_token, data.refresh_token)

  return { user: data.user, tenant: data.tenant }
}

// Login
export async function login(
  email: string,
  password: string
): Promise<{ user: User; tenant: Tenant } | null> {
  const res = await fetch(`${API_URL}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Login failed')
  }

  const data = await res.json()
  setTokens(data.access_token, data.refresh_token)

  return { user: data.user, tenant: data.tenant }
}

// Refresh token
async function refreshAccessToken(): Promise<boolean> {
  const refreshToken = getRefreshToken()
  if (!refreshToken) return false

  try {
    const res = await fetch(`${API_URL}/api/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    })

    if (!res.ok) {
      clearTokens()
      return false
    }

    const data = await res.json()
    localStorage.setItem(TOKEN_KEY, data.access_token)
    return true
  } catch {
    clearTokens()
    return false
  }
}

// Get current user
export async function getCurrentUser(): Promise<{ user: User; tenant: Tenant } | null> {
  const token = getAccessToken()
  if (!token) return null

  try {
    const res = await authFetch(`${API_URL}/api/auth/me`)
    if (!res.ok) {
      clearTokens()
      return null
    }
    return await res.json()
  } catch {
    return null
  }
}

// Logout
export function logout() {
  clearTokens()
  window.location.href = '/login'
}

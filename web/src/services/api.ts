import axios from 'axios'
import type { BackendGreska } from '@/types/api'

export class ApiGreska extends Error {
  constructor(
    public readonly code: string,
    message: string,
    public readonly status: number,
  ) {
    super(message)
    this.name = 'ApiGreska'
  }
}

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.set('Authorization', `Bearer ${token}`)
  return config
})

let osvjezavanjeUTijeku: Promise<void> | null = null

api.interceptors.response.use(
  (response) => response,
  async (error: unknown) => {
    if (!axios.isAxiosError(error) || !error.response) throw error

    const status = error.response.status
    const data = error.response.data as Partial<BackendGreska>

    const url = error.config?.url ?? ''
    const jeAuthEndpoint = url.includes('/auth/login') || url.includes('/auth/refresh')
    if (status !== 401 || jeAuthEndpoint) {
      throw new ApiGreska(
        data.code ?? 'unknown_error',
        data.message ?? error.message,
        status,
      )
    }

    try {
      if (!osvjezavanjeUTijeku) {
        const { useAuthStore } = await import('@/stores/auth')
        osvjezavanjeUTijeku = useAuthStore()
          .osvjeziToken()
          .finally(() => {
            osvjezavanjeUTijeku = null
          })
      }
      await osvjezavanjeUTijeku

      return api.request(error.config!)
    } catch {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      window.location.href = '/prijava'
      throw new ApiGreska('session_expired', 'Sesija je istekla.', 401)
    }
  },
)

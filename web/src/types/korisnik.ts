export interface KorisnikPodaci {
  id: number
  username: string
  email: string
  role: 'admin' | 'member'
  is_active: boolean
  hours_per_week: number
  pages_per_week: number
}

export interface KorisnikKreiranje {
  username: string
  email: string
  password: string
  role: 'admin' | 'member'
  is_active: boolean
  hours_per_week: number
  pages_per_week: number
}

export interface KorisnikAzuriranje {
  username?: string
  email?: string
  password?: string
  role?: 'admin' | 'member'
  is_active?: boolean
  hours_per_week?: number
  pages_per_week?: number
}

export interface KorisnikSamoAzuriranje {
  email?: string
  password?: string
  hours_per_week?: number
  pages_per_week?: number
}

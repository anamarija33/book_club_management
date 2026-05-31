export interface Klub {
  id: number
  name: string
  description: string | null
  max_members: number
  min_hours_per_week: number
  pages_per_week: number
  registration_deadline: string
  created_by: number
  member_count: number
}

export interface KlubKreiranje {
  name: string
  description: string | null
  max_members: number
  min_hours_per_week: number
  pages_per_week: number
  registration_deadline: string
}

export interface KlubAzuriranje {
  name?: string
  description?: string | null
  max_members?: number
  min_hours_per_week?: number
  pages_per_week?: number
  registration_deadline?: string
}

export interface Clanstvo {
  id: number
  user_id: number
  club_id: number
  status: 'pending' | 'approved' | 'rejected'
  created_at: string
  username: string | null
}

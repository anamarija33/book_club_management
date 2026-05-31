import { api } from '@/services/api'
import type { Clanstvo } from '@/types/clanstvo'

export async function dohvatiClanstva(clubId: number): Promise<Clanstvo[]> {
  const { data } = await api.get<Clanstvo[]>(`/clubs/${clubId}/memberships/`)
  return data
}

export async function kreirajClanstvo(clubId: number): Promise<Clanstvo> {
  const { data } = await api.post<Clanstvo>(`/clubs/${clubId}/memberships/`)
  return data
}

export async function azurirajClanstvo(
  clubId: number,
  membershipId: number,
  status: 'approved' | 'rejected',
): Promise<Clanstvo> {
  const { data } = await api.patch<Clanstvo>(`/clubs/${clubId}/memberships/${membershipId}`, {
    status,
  })
  return data
}

export async function obrisiClanstvo(clubId: number, membershipId: number): Promise<void> {
  await api.delete(`/clubs/${clubId}/memberships/${membershipId}`)
}

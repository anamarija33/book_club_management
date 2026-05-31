import { api } from './api'
import type { KorisnikAzuriranje, KorisnikKreiranje, KorisnikPodaci, KorisnikSamoAzuriranje } from '@/types/korisnik'

export async function dohvatiKorisnike(): Promise<KorisnikPodaci[]> {
  const { data } = await api.get<KorisnikPodaci[]>('/users/')
  return data
}

export async function dohvatiKorisnika(id: number): Promise<KorisnikPodaci> {
  const { data } = await api.get<KorisnikPodaci>(`/users/${id}`)
  return data
}

export async function kreirajKorisnika(tijelo: KorisnikKreiranje): Promise<KorisnikPodaci> {
  const { data } = await api.post<KorisnikPodaci>('/users/', tijelo)
  return data
}

export async function azurirajKorisnika(id: number, tijelo: KorisnikAzuriranje): Promise<KorisnikPodaci> {
  const { data } = await api.patch<KorisnikPodaci>(`/users/${id}`, tijelo)
  return data
}

export async function obrisiKorisnika(id: number): Promise<void> {
  await api.delete(`/users/${id}`)
}

export async function azurirajMojProfil(tijelo: KorisnikSamoAzuriranje): Promise<KorisnikPodaci> {
  const { data } = await api.patch<KorisnikPodaci>('/users/me/profile', tijelo)
  return data
}

export interface StatistikePodaci {
  total_users: number
  total_clubs: number
  total_books: number
  total_memberships: number
}

export async function dohvatiStatistike(): Promise<StatistikePodaci> {
  const { data } = await api.get<StatistikePodaci>('/stats/')
  return data
}

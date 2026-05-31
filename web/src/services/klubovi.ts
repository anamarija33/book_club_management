import { api } from '@/services/api'
import type { Klub, KlubKreiranje, KlubAzuriranje } from '@/types/klub'

export async function dohvatiKlubove(): Promise<Klub[]> {
  const { data } = await api.get<Klub[]>('/clubs/')
  return data
}

export async function dohvatiKlub(id: number): Promise<Klub> {
  const { data } = await api.get<Klub>(`/clubs/${id}`)
  return data
}

export async function kreirajKlub(tijelo: KlubKreiranje): Promise<Klub> {
  const { data } = await api.post<Klub>('/clubs/', tijelo)
  return data
}

export async function azurirajKlub(id: number, tijelo: KlubAzuriranje): Promise<Klub> {
  const { data } = await api.patch<Klub>(`/clubs/${id}`, tijelo)
  return data
}

export async function obrisiKlub(id: number): Promise<void> {
  await api.delete(`/clubs/${id}`)
}

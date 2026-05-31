import { api } from '@/services/api'
import type { Knjiga, KnjigaKreiranje, KnjigaAzuriranje, KorisnikKnjiga } from '@/types/knjiga'

export async function dohvatiKnjige(): Promise<Knjiga[]> {
  const { data } = await api.get<Knjiga[]>('/books')
  return data
}

export async function dohvatiKnjigu(id: number): Promise<Knjiga> {
  const { data } = await api.get<Knjiga>(`/books/${id}`)
  return data
}

export async function kreirajKnjigu(tijelo: KnjigaKreiranje): Promise<Knjiga> {
  const { data } = await api.post<Knjiga>('/books', tijelo)
  return data
}

export async function azurirajKnjigu(id: number, tijelo: KnjigaAzuriranje): Promise<Knjiga> {
  const { data } = await api.patch<Knjiga>(`/books/${id}`, tijelo)
  return data
}

export async function obrisiKnjigu(id: number): Promise<void> {
  await api.delete(`/books/${id}`)
}

export async function dohvatiMojeKnjige(): Promise<KorisnikKnjiga[]> {
  const { data } = await api.get<KorisnikKnjiga[]>('/users/me/books')
  return data
}

export async function oznaciProcitanu(bookId: number): Promise<KorisnikKnjiga> {
  const { data } = await api.post<KorisnikKnjiga>(`/users/me/books/${bookId}`)
  return data
}

export async function ukloniOznakuProcitane(bookId: number): Promise<void> {
  await api.delete(`/users/me/books/${bookId}`)
}

export interface Knjiga {
  id: number
  title: string
  author: string
  pages: number
  description: string | null
}

export interface KnjigaKreiranje {
  title: string
  author: string
  pages: number
  description: string | null
}

export interface KnjigaAzuriranje {
  title?: string
  author?: string
  pages?: number
  description?: string | null
}

export interface KorisnikKnjiga {
  book: Knjiga
  read_at: string
}

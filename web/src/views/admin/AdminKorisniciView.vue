<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useObavijestiStore } from '@/stores/obavijesti'
import { dohvatiKorisnike, azurirajKorisnika, obrisiKorisnika } from '@/services/korisnici'
import type { KorisnikPodaci } from '@/types/korisnik'

type Stanje = 'ucitavanje' | 'greska' | 'prazno' | 'spremno'

const obavijesti = useObavijestiStore()
const korisnici = ref<KorisnikPodaci[]>([])
const stanje = ref<Stanje>('ucitavanje')

async function ucitaj(): Promise<void> {
  stanje.value = 'ucitavanje'
  try {
    const podaci = await dohvatiKorisnike()
    korisnici.value = podaci
    stanje.value = podaci.length === 0 ? 'prazno' : 'spremno'
  } catch (e) {
    stanje.value = 'greska'
    obavijesti.greska(e instanceof Error ? e.message : 'Greška pri dohvatu korisnika.')
  }
}

async function toggleAktivan(k: KorisnikPodaci): Promise<void> {
  const akcija = k.is_active ? 'deaktivirati' : 'aktivirati'
  if (!confirm(`Želite li ${akcija} korisnika "${k.username}"?`)) return
  try {
    const azuriran = await azurirajKorisnika(k.id, { is_active: !k.is_active })
    const idx = korisnici.value.findIndex((u) => u.id === k.id)
    if (idx !== -1) korisnici.value[idx] = azuriran
    obavijesti.uspjeh(`Korisnik ${azuriran.is_active ? 'aktiviran' : 'deaktiviran'}.`)
  } catch (e) {
    obavijesti.greska(e instanceof Error ? e.message : 'Greška pri ažuriranju.')
  }
}

async function obrisi(k: KorisnikPodaci): Promise<void> {
  if (!confirm(`Obrisati korisnika "${k.username}"? Ova akcija je nepovratna.`)) return
  try {
    await obrisiKorisnika(k.id)
    korisnici.value = korisnici.value.filter((u) => u.id !== k.id)
    obavijesti.uspjeh('Korisnik obrisan.')
  } catch (e) {
    obavijesti.greska(e instanceof Error ? e.message : 'Greška pri brisanju.')
  }
}

onMounted(ucitaj)
</script>

<template>
  <div class="pogled">
    <div class="zaglavlje">
      <h1>Korisnici</h1>
      <RouterLink to="/admin/korisnici/novo">
        <button class="gumb-novo">+ Novi korisnik</button>
      </RouterLink>
    </div>

    <div v-if="stanje === 'ucitavanje'" class="stanje-poruka muted">Učitavanje...</div>
    <div v-else-if="stanje === 'greska'" class="stanje-poruka greska">Greška pri dohvatu.</div>
    <div v-else-if="stanje === 'prazno'" class="stanje-poruka muted">Nema korisnika.</div>

    <table v-else class="tablica">
      <thead>
        <tr>
          <th>Korisničko ime</th>
          <th>Email</th>
          <th>Uloga</th>
          <th>Sati/tjedan</th>
          <th>Stranica/tjedan</th>
          <th>Status</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="k in korisnici" :key="k.id" :class="{ 'red--neaktivan': !k.is_active }">
          <td>{{ k.username }}</td>
          <td class="muted">{{ k.email }}</td>
          <td>
            <span class="uloga-chip" :class="k.role === 'admin' ? 'uloga-chip--admin' : 'uloga-chip--clan'">
              {{ k.role === 'admin' ? 'Admin' : 'Član' }}
            </span>
          </td>
          <td>{{ k.hours_per_week }}</td>
          <td>{{ k.pages_per_week }}</td>
          <td>
            <span :class="k.is_active ? 'aktivan' : 'neaktivan'">
              {{ k.is_active ? 'Aktivan' : 'Neaktivan' }}
            </span>
          </td>
          <td class="akcije-celija">
            <RouterLink :to="`/admin/korisnici/${k.id}/uredi`" class="akcija">Uredi</RouterLink>
            <button class="akcija" @click="toggleAktivan(k)">
              {{ k.is_active ? 'Deaktiviraj' : 'Aktiviraj' }}
            </button>
            <button class="akcija akcija--opasnost" @click="obrisi(k)">Obriši</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.pogled {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.zaglavlje {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.gumb-novo {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  padding: 0.5rem 1.25rem;
  background: var(--boja-akcent);
  color: var(--boja-tekst);
  border: none;
  cursor: pointer;
}

.gumb-novo:hover { background: var(--boja-tekst); color: var(--boja-pozadina); }

.stanje-poruka {
  padding: 1rem;
  border: 1px solid var(--boja-rub);
  font-size: 0.875rem;
}

.stanje-poruka.greska { border-color: var(--boja-akcent); color: var(--boja-akcent); }

.tablica {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.tablica th {
  text-align: left;
  padding: 0.625rem 1rem;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--boja-tekst-mute);
  border-bottom: 2px solid var(--boja-rub);
}

.tablica td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--boja-rub);
}

.tablica tbody tr:hover td { background: var(--boja-povrsina); }
.red--neaktivan td { opacity: 0.5; }

.uloga-chip {
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: 0.2rem 0.5rem;
  border-radius: 100px;
}

.uloga-chip--admin { background: rgba(192, 139, 58, 0.15); color: var(--boja-akcent); }
.uloga-chip--clan  { background: rgba(90, 140, 82, 0.15);  color: var(--boja-uspjeh); }

.aktivan   { font-size: 0.75rem; color: var(--boja-uspjeh); }
.neaktivan { font-size: 0.75rem; color: var(--boja-tekst-mute); }

.akcije-celija { display: flex; gap: 1rem; }

.akcija {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--boja-tekst-mute);
  transition: color var(--tranzicija);
  background: none;
  border: none;
  cursor: pointer;
}

.akcija:hover { color: var(--boja-tekst); }
.akcija--opasnost:hover { color: var(--boja-akcent); }
</style>

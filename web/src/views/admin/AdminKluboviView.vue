<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useObavijestiStore } from '@/stores/obavijesti'
import { dohvatiKlubove, obrisiKlub } from '@/services/klubovi'
import type { Klub } from '@/types/klub'

type Stanje = 'ucitavanje' | 'greska' | 'prazno' | 'spremno'

const obavijesti = useObavijestiStore()
const klubovi = ref<Klub[]>([])
const stanje = ref<Stanje>('ucitavanje')

async function ucitaj(): Promise<void> {
  stanje.value = 'ucitavanje'
  try {
    const podaci = await dohvatiKlubove()
    klubovi.value = podaci
    stanje.value = podaci.length === 0 ? 'prazno' : 'spremno'
  } catch (e) {
    stanje.value = 'greska'
    obavijesti.greska(e instanceof Error ? e.message : 'Greška pri dohvatu klubova.')
  }
}

async function obrisi(id: number, naziv: string): Promise<void> {
  if (!confirm(`Obrisati klub "${naziv}"?`)) return
  try {
    await obrisiKlub(id)
    obavijesti.uspjeh('Klub obrisan.')
    await ucitaj()
  } catch (e) {
    obavijesti.greska(e instanceof Error ? e.message : 'Greška pri brisanju.')
  }
}

function formatirajDatum(d: string): string {
  return new Date(d).toLocaleDateString('hr-HR')
}

onMounted(ucitaj)
</script>

<template>
  <div class="pogled">
    <div class="zaglavlje">
      <h1>Knjižni klubovi</h1>
      <RouterLink to="/admin/klubovi/novo">
        <button class="gumb-novo">+ Novi klub</button>
      </RouterLink>
    </div>

    <div v-if="stanje === 'ucitavanje'" class="stanje-poruka muted">Učitavanje...</div>
    <div v-else-if="stanje === 'greska'" class="stanje-poruka greska">Greška pri dohvatu.</div>
    <div v-else-if="stanje === 'prazno'" class="stanje-poruka muted">Nema knjižnih klubova.</div>

    <table v-else class="tablica">
      <thead>
        <tr>
          <th>Naziv</th>
          <th>Maks. članova</th>
          <th>Sati/tjedan</th>
          <th>Stranica/tjedan</th>
          <th>Rok prijave</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="k in klubovi" :key="k.id">
          <td>{{ k.name }}</td>
          <td>{{ k.max_members }}</td>
          <td>{{ k.min_hours_per_week }}</td>
          <td>{{ k.pages_per_week }}</td>
          <td>{{ formatirajDatum(k.registration_deadline) }}</td>
          <td class="akcije-celija">
            <RouterLink :to="`/admin/klubovi/${k.id}/clanstva`" class="akcija">Članovi</RouterLink>
            <RouterLink :to="`/admin/klubovi/${k.id}/uredi`" class="akcija">Uredi</RouterLink>
            <button class="akcija akcija--opasnost" @click="obrisi(k.id, k.name)">Obriši</button>
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

.akcije-celija {
  display: flex;
  gap: 1rem;
}

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

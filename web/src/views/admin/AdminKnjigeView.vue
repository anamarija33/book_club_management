<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useObavijestiStore } from '@/stores/obavijesti'
import { dohvatiKnjige, obrisiKnjigu } from '@/services/knjige'
import type { Knjiga } from '@/types/knjiga'

type Stanje = 'ucitavanje' | 'greska' | 'prazno' | 'spremno'

const obavijesti = useObavijestiStore()
const knjige = ref<Knjiga[]>([])
const stanje = ref<Stanje>('ucitavanje')

async function ucitaj(): Promise<void> {
  stanje.value = 'ucitavanje'
  try {
    const podaci = await dohvatiKnjige()
    knjige.value = podaci
    stanje.value = podaci.length === 0 ? 'prazno' : 'spremno'
  } catch (e) {
    stanje.value = 'greska'
    obavijesti.greska(e instanceof Error ? e.message : 'Greška pri dohvatu knjiga.')
  }
}

async function obrisi(id: number, naslov: string): Promise<void> {
  if (!confirm(`Obrisati knjigu "${naslov}"?`)) return
  try {
    await obrisiKnjigu(id)
    obavijesti.uspjeh('Knjiga obrisana.')
    await ucitaj()
  } catch (e) {
    obavijesti.greska(e instanceof Error ? e.message : 'Greška pri brisanju.')
  }
}

onMounted(ucitaj)
</script>

<template>
  <div class="pogled">
    <div class="zaglavlje">
      <h1>Katalog knjiga</h1>
      <RouterLink to="/admin/knjige/novo">
        <button class="gumb-novo">+ Nova knjiga</button>
      </RouterLink>
    </div>

    <div v-if="stanje === 'ucitavanje'" class="stanje-poruka muted">Učitavanje...</div>
    <div v-else-if="stanje === 'greska'" class="stanje-poruka greska">Greška pri dohvatu.</div>
    <div v-else-if="stanje === 'prazno'" class="stanje-poruka muted">Nema knjiga u katalogu.</div>

    <table v-else class="tablica">
      <thead>
        <tr>
          <th>Naslov</th>
          <th>Autor</th>
          <th>Stranice</th>
          <th>Opis</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="k in knjige" :key="k.id">
          <td>{{ k.title }}</td>
          <td>{{ k.author }}</td>
          <td>{{ k.pages }}</td>
          <td class="muted opis">{{ k.description ?? '—' }}</td>
          <td class="akcije-celija">
            <RouterLink :to="`/admin/knjige/${k.id}/uredi`" class="akcija">Uredi</RouterLink>
            <button class="akcija akcija--opasnost" @click="obrisi(k.id, k.title)">Obriši</button>
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

.opis {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

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

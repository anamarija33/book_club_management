<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useObavijestiStore } from '@/stores/obavijesti'
import { dohvatiMojeKnjige, ukloniOznakuProcitane } from '@/services/knjige'
import type { KorisnikKnjiga } from '@/types/knjiga'

type Stanje = 'ucitavanje' | 'greska' | 'prazno' | 'spremno'

const obavijesti = useObavijestiStore()
const knjige = ref<KorisnikKnjiga[]>([])
const stanje = ref<Stanje>('ucitavanje')

async function ucitaj(): Promise<void> {
  stanje.value = 'ucitavanje'
  try {
    const podaci = await dohvatiMojeKnjige()
    knjige.value = podaci
    stanje.value = podaci.length === 0 ? 'prazno' : 'spremno'
  } catch (e) {
    stanje.value = 'greska'
    obavijesti.greska(e instanceof Error ? e.message : 'Greška pri dohvatu knjiga.')
  }
}

async function ukloni(mk: KorisnikKnjiga): Promise<void> {
  try {
    await ukloniOznakuProcitane(mk.book.id)
    knjige.value = knjige.value.filter((k) => k.book.id !== mk.book.id)
    if (knjige.value.length === 0) stanje.value = 'prazno'
    obavijesti.uspjeh(`"${mk.book.title}" uklonjena iz pročitanih.`)
  } catch (e) {
    obavijesti.greska(e instanceof Error ? e.message : 'Greška pri uklanjanju.')
  }
}

function formatirajDatum(d: string): string {
  return new Date(d).toLocaleDateString('hr-HR')
}

onMounted(ucitaj)
</script>

<template>
  <div class="pogled">
    <h1>Pročitane knjige</h1>

    <div v-if="stanje === 'ucitavanje'" class="stanje-poruka muted">Učitavanje...</div>
    <div v-else-if="stanje === 'greska'" class="stanje-poruka greska">Greška pri dohvatu.</div>
    <div v-else-if="stanje === 'prazno'" class="stanje-poruka muted">
      Još nisi označio nijednu knjigu kao pročitanu.
      <RouterLink to="/clan/knjige" class="veza">Pregledaj katalog →</RouterLink>
    </div>

    <table v-else class="tablica">
      <thead>
        <tr>
          <th>Naslov</th>
          <th>Autor</th>
          <th>Stranice</th>
          <th>Pročitano</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="mk in knjige" :key="mk.book.id">
          <td>{{ mk.book.title }}</td>
          <td>{{ mk.book.author }}</td>
          <td>{{ mk.book.pages }}</td>
          <td class="muted">{{ formatirajDatum(mk.read_at) }}</td>
          <td>
            <button class="akcija akcija--opasnost" @click="ukloni(mk)">Ukloni</button>
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

.stanje-poruka {
  padding: 1rem;
  border: 1px solid var(--boja-rub);
  font-size: 0.875rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.stanje-poruka.greska { border-color: var(--boja-akcent); color: var(--boja-akcent); }

.veza {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--boja-tekst-mute);
  transition: color var(--tranzicija);
}

.veza:hover { color: var(--boja-tekst); }

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

.akcija--opasnost:hover { color: var(--boja-akcent); }
</style>

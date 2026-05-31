<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useObavijestiStore } from '@/stores/obavijesti'
import { dohvatiKnjige, dohvatiMojeKnjige, oznaciProcitanu, ukloniOznakuProcitane } from '@/services/knjige'
import type { Knjiga, KorisnikKnjiga } from '@/types/knjiga'

type Stanje = 'ucitavanje' | 'greska' | 'prazno' | 'spremno'

const obavijesti = useObavijestiStore()
const knjige = ref<Knjiga[]>([])
const procitaneIds = ref<Set<number>>(new Set())
const stanje = ref<Stanje>('ucitavanje')
const pretrazivanje = ref('')

onMounted(async () => {
  try {
    const [sveknjige, mojeKnjige] = await Promise.all([dohvatiKnjige(), dohvatiMojeKnjige()])
    knjige.value = sveknjige
    procitaneIds.value = new Set(mojeKnjige.map((mk: KorisnikKnjiga) => mk.book.id))
    stanje.value = sveknjige.length === 0 ? 'prazno' : 'spremno'
  } catch (e) {
    stanje.value = 'greska'
    obavijesti.greska(e instanceof Error ? e.message : 'Greška pri dohvatu kataloga.')
  }
})

function filtrirane(): Knjiga[] {
  const upit = pretrazivanje.value.toLowerCase()
  if (!upit) return knjige.value
  return knjige.value.filter(
    (k) => k.title.toLowerCase().includes(upit) || k.author.toLowerCase().includes(upit),
  )
}

async function oznaci(knjiga: Knjiga): Promise<void> {
  try {
    await oznaciProcitanu(knjiga.id)
    procitaneIds.value.add(knjiga.id)
    obavijesti.uspjeh(`"${knjiga.title}" označena kao pročitana.`)
  } catch (e) {
    obavijesti.greska(e instanceof Error ? e.message : 'Greška pri označavanju.')
  }
}

async function ukloniOznaku(knjiga: Knjiga): Promise<void> {
  try {
    await ukloniOznakuProcitane(knjiga.id)
    procitaneIds.value.delete(knjiga.id)
    obavijesti.uspjeh(`"${knjiga.title}" uklonjena iz pročitanih.`)
  } catch (e) {
    obavijesti.greska(e instanceof Error ? e.message : 'Greška pri uklanjanju oznake.')
  }
}
</script>

<template>
  <div class="pogled">
    <div class="zaglavlje">
      <h1>Katalog knjiga</h1>
      <input
        v-model="pretrazivanje"
        class="pretraga"
        type="text"
        placeholder="Pretraži naslov ili autora..."
      />
    </div>

    <div v-if="stanje === 'ucitavanje'" class="stanje-poruka muted">Učitavanje...</div>
    <div v-else-if="stanje === 'greska'" class="stanje-poruka greska">Greška pri dohvatu.</div>
    <div v-else-if="stanje === 'prazno'" class="stanje-poruka muted">Katalog je prazan.</div>

    <template v-else>
      <div v-if="filtrirane().length === 0" class="stanje-poruka muted">
        Nema knjiga koje odgovaraju pretrazi.
      </div>

      <table v-else class="tablica">
        <thead>
          <tr>
            <th>Naslov</th>
            <th>Autor</th>
            <th>Stranice</th>
            <th>Status</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="k in filtrirane()" :key="k.id">
            <td>{{ k.title }}</td>
            <td>{{ k.author }}</td>
            <td>{{ k.pages }}</td>
            <td>
              <span v-if="procitaneIds.has(k.id)" class="badge-procitana">Pročitana</span>
              <span v-else class="muted">—</span>
            </td>
            <td>
              <button
                v-if="!procitaneIds.has(k.id)"
                class="akcija"
                @click="oznaci(k)"
              >
                Označi pročitanom
              </button>
              <button
                v-else
                class="akcija akcija--opasnost"
                @click="ukloniOznaku(k)"
              >
                Ukloni oznaku
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </template>
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
  gap: 1rem;
  flex-wrap: wrap;
}

.pretraga {
  background: var(--boja-pozadina);
  border: 1px solid var(--boja-rub);
  color: var(--boja-tekst);
  padding: 0.5rem 0.875rem;
  font-size: 0.875rem;
  width: 280px;
}

.pretraga:focus { outline: none; border-color: var(--boja-akcent); }

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

.badge-procitana {
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  padding: 0.2rem 0.5rem;
  border: 1px solid var(--boja-uspjeh);
  color: var(--boja-uspjeh);
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

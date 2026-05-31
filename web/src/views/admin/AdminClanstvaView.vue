<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useObavijestiStore } from '@/stores/obavijesti'
import { dohvatiKlub } from '@/services/klubovi'
import { dohvatiClanstva, azurirajClanstvo, obrisiClanstvo } from '@/services/clanstva'
import StatusBadge from '@/components/StatusBadge.vue'
import type { Klub } from '@/types/klub'
import type { Clanstvo } from '@/types/clanstvo'

const route = useRoute()
const obavijesti = useObavijestiStore()
const clubId = Number(route.params['clubId'])

const klub = ref<Klub | null>(null)
const clanstva = ref<Clanstvo[]>([])
const ucitava = ref(true)

onMounted(async () => {
  try {
    const [k, c] = await Promise.all([dohvatiKlub(clubId), dohvatiClanstva(clubId)])
    klub.value = k
    clanstva.value = c
  } catch (e) {
    obavijesti.greska(e instanceof Error ? e.message : 'Greška pri dohvatu podataka.')
  } finally {
    ucitava.value = false
  }
})

async function odobri(clanstvo: Clanstvo): Promise<void> {
  try {
    const azurirano = await azurirajClanstvo(clubId, clanstvo.id, 'approved')
    clanstvo.status = azurirano.status
    obavijesti.uspjeh(`Prijava korisnika ${clanstvo.username ?? clanstvo.user_id} odobrena.`)
  } catch (e) {
    obavijesti.greska(e instanceof Error ? e.message : 'Greška pri odobravanju.')
  }
}

async function odbij(clanstvo: Clanstvo): Promise<void> {
  try {
    const azurirano = await azurirajClanstvo(clubId, clanstvo.id, 'rejected')
    clanstvo.status = azurirano.status
    obavijesti.uspjeh(`Prijava korisnika ${clanstvo.username ?? clanstvo.user_id} odbijena.`)
  } catch (e) {
    obavijesti.greska(e instanceof Error ? e.message : 'Greška pri odbijanju.')
  }
}

async function obrisi(clanstvo: Clanstvo): Promise<void> {
  if (!confirm(`Obrisati prijavu korisnika ${clanstvo.username ?? clanstvo.user_id}?`)) return
  try {
    await obrisiClanstvo(clubId, clanstvo.id)
    clanstva.value = clanstva.value.filter((c) => c.id !== clanstvo.id)
    obavijesti.uspjeh('Prijava obrisana.')
  } catch (e) {
    obavijesti.greska(e instanceof Error ? e.message : 'Greška pri brisanju.')
  }
}

function formatirajDatum(d: string): string {
  return new Date(d).toLocaleDateString('hr-HR')
}
</script>

<template>
  <div class="pogled">
    <RouterLink to="/admin/klubovi" class="natrag">← Klubovi</RouterLink>
    <h1>{{ klub?.name ?? 'Članovi' }}</h1>

    <div v-if="ucitava" class="stanje-poruka muted">Učitavanje...</div>

    <template v-else>
      <div v-if="clanstva.length === 0" class="stanje-poruka muted">
        Nema prijava za ovaj klub.
      </div>

      <table v-else class="tablica">
        <thead>
          <tr>
            <th>Korisnik</th>
            <th>Status</th>
            <th>Datum prijave</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in clanstva" :key="c.id">
            <td>{{ c.username ?? c.user_id }}</td>
            <td><StatusBadge :status="c.status" /></td>
            <td class="muted">{{ formatirajDatum(c.created_at) }}</td>
            <td class="akcije-celija">
              <button
                v-if="c.status === 'pending'"
                class="akcija akcija--uspjeh"
                @click="odobri(c)"
              >
                Odobri
              </button>
              <button
                v-if="c.status === 'pending'"
                class="akcija akcija--opasnost"
                @click="odbij(c)"
              >
                Odbij
              </button>
              <button class="akcija akcija--opasnost" @click="obrisi(c)">Obriši</button>
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

.natrag {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--boja-tekst-mute);
  transition: color var(--tranzicija);
}

.natrag:hover { color: var(--boja-tekst); }

.stanje-poruka {
  padding: 1rem;
  border: 1px solid var(--boja-rub);
  font-size: 0.875rem;
}

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

.akcije-celija { display: flex; gap: 0.75rem; }

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

.akcija--uspjeh:hover { color: var(--boja-uspjeh); }
.akcija--opasnost:hover { color: var(--boja-akcent); }
</style>

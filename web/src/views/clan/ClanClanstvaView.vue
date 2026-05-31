<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useObavijestiStore } from '@/stores/obavijesti'
import { dohvatiKlubove } from '@/services/klubovi'
import { dohvatiClanstva, obrisiClanstvo } from '@/services/clanstva'
import StatusBadge from '@/components/StatusBadge.vue'
import type { Klub } from '@/types/klub'
import type { Clanstvo } from '@/types/clanstvo'

interface ClanstvoProsieno {
  clanstvo: Clanstvo
  klub: Klub
}

const auth = useAuthStore()
const obavijesti = useObavijestiStore()
const stavke = ref<ClanstvoProsieno[]>([])
const ucitava = ref(true)

onMounted(async () => {
  try {
    const sviKlubovi = await dohvatiKlubove()
    const sva: ClanstvoProsieno[] = []
    await Promise.allSettled(
      sviKlubovi.map(async (k) => {
        const clanstvaKluba = await dohvatiClanstva(k.id)
        const mojeUKlubu = clanstvaKluba.filter((c) => c.user_id === auth.user?.id)
        for (const c of mojeUKlubu) {
          sva.push({ clanstvo: c, klub: k })
        }
      }),
    )
    stavke.value = sva
  } catch (e) {
    obavijesti.greska(e instanceof Error ? e.message : 'Greška pri dohvatu članstava.')
  } finally {
    ucitava.value = false
  }
})

async function povuci(stavka: ClanstvoProsieno): Promise<void> {
  if (!confirm(`Povući prijavu iz kluba "${stavka.klub.name}"?`)) return
  try {
    await obrisiClanstvo(stavka.klub.id, stavka.clanstvo.id)
    stavke.value = stavke.value.filter((s) => s.clanstvo.id !== stavka.clanstvo.id)
    obavijesti.uspjeh('Prijava povučena.')
  } catch (e) {
    obavijesti.greska(e instanceof Error ? e.message : 'Greška pri povlačenju prijave.')
  }
}

function formatirajDatum(d: string): string {
  return new Date(d).toLocaleDateString('hr-HR')
}
</script>

<template>
  <div class="pogled">
    <h1>Moja članstva</h1>

    <div v-if="ucitava" class="stanje-poruka muted">Učitavanje...</div>
    <div v-else-if="stavke.length === 0" class="stanje-poruka muted">
      Nisi prijavljen ni u jedan knjižni klub.
      <RouterLink to="/clan/klubovi" class="veza">Pregledaj klubove →</RouterLink>
    </div>

    <table v-else class="tablica">
      <thead>
        <tr>
          <th>Klub</th>
          <th>Status</th>
          <th>Datum prijave</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="s in stavke" :key="s.clanstvo.id">
          <td>{{ s.klub.name }}</td>
          <td><StatusBadge :status="s.clanstvo.status" /></td>
          <td class="muted">{{ formatirajDatum(s.clanstvo.created_at) }}</td>
          <td>
            <button
              v-if="s.clanstvo.status === 'pending'"
              class="akcija akcija--opasnost"
              @click="povuci(s)"
            >
              Povuci
            </button>
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

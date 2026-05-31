<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useObavijestiStore } from '@/stores/obavijesti'
import { dohvatiKlubove } from '@/services/klubovi'
import { dohvatiClanstva, kreirajClanstvo, obrisiClanstvo } from '@/services/clanstva'
import StatusBadge from '@/components/StatusBadge.vue'
import type { Klub } from '@/types/klub'
import type { Clanstvo } from '@/types/clanstvo'

const auth = useAuthStore()
const obavijesti = useObavijestiStore()
const klubovi = ref<Klub[]>([])
const svaClanstva = ref<Clanstvo[]>([])
const ucitava = ref(true)

onMounted(async () => {
  try {
    const sviKlubovi = await dohvatiKlubove()
    klubovi.value = sviKlubovi

    const clanstvaPoKlubu = await Promise.allSettled(
      sviKlubovi.map((k) => dohvatiClanstva(k.id)),
    )
    const sva: Clanstvo[] = []
    for (const r of clanstvaPoKlubu) {
      if (r.status === 'fulfilled') sva.push(...r.value)
    }
    svaClanstva.value = sva.filter((c) => c.user_id === auth.user?.id)
  } catch (e) {
    obavijesti.greska(e instanceof Error ? e.message : 'Greška pri dohvatu klubova.')
  } finally {
    ucitava.value = false
  }
})

function mojeClanstvoZaKlub(clubId: number): Clanstvo | undefined {
  return svaClanstva.value.find((c) => c.club_id === clubId)
}

const rokIstekao = computed(() => (klub: Klub) => new Date(klub.registration_deadline) < new Date())

async function prijaviSe(klub: Klub): Promise<void> {
  try {
    const novo = await kreirajClanstvo(klub.id)
    svaClanstva.value.push(novo)
    obavijesti.uspjeh(`Prijava u "${klub.name}" poslana.`)
  } catch (e) {
    obavijesti.greska(e instanceof Error ? e.message : 'Greška pri prijavi.')
  }
}

async function povuciPrijavu(klub: Klub): Promise<void> {
  const clanstvo = mojeClanstvoZaKlub(klub.id)
  if (!clanstvo) return
  if (!confirm(`Povući prijavu iz kluba "${klub.name}"?`)) return
  try {
    await obrisiClanstvo(klub.id, clanstvo.id)
    svaClanstva.value = svaClanstva.value.filter((c) => c.id !== clanstvo.id)
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
    <h1>Knjižni klubovi</h1>

    <div v-if="ucitava" class="stanje-poruka muted">Učitavanje...</div>
    <div v-else-if="klubovi.length === 0" class="stanje-poruka muted">Nema dostupnih klubova.</div>

    <table v-else class="tablica">
      <thead>
        <tr>
          <th>Naziv</th>
          <th>Popunjenost</th>
          <th>Sati/tjedan</th>
          <th>Stranica/tjedan</th>
          <th>Rok prijave</th>
          <th>Status</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="k in klubovi" :key="k.id">
          <td>
            <span>{{ k.name }}</span>
            <span v-if="k.description" class="opis muted"> — {{ k.description }}</span>
          </td>
          <td>
            <span :class="{ 'puno': k.member_count >= k.max_members }">
              {{ k.member_count }}/{{ k.max_members }}
            </span>
          </td>
          <td>{{ k.min_hours_per_week }}</td>
          <td>{{ k.pages_per_week }}</td>
          <td :class="{ muted: rokIstekao(k) }">{{ formatirajDatum(k.registration_deadline) }}</td>
          <td>
            <StatusBadge
              v-if="mojeClanstvoZaKlub(k.id)"
              :status="mojeClanstvoZaKlub(k.id)!.status"
            />
            <span v-else class="muted">—</span>
          </td>
          <td class="akcije-celija">
            <template v-if="!mojeClanstvoZaKlub(k.id)">
              <button
                class="akcija"
                :disabled="rokIstekao(k) || k.member_count >= k.max_members"
                :title="rokIstekao(k) ? 'Rok prijave je istekao.' : k.member_count >= k.max_members ? 'Klub je popunjen.' : undefined"
                @click="prijaviSe(k)"
              >
                Prijavi se
              </button>
            </template>
            <template v-else-if="mojeClanstvoZaKlub(k.id)?.status === 'pending'">
              <button class="akcija akcija--opasnost" @click="povuciPrijavu(k)">Povuci</button>
            </template>
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

.opis { font-size: 0.8rem; }

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

.akcija:hover:not(:disabled) { color: var(--boja-tekst); }
.akcija--opasnost:hover:not(:disabled) { color: var(--boja-akcent); }
.akcija:disabled { opacity: 0.35; cursor: not-allowed; }
.puno { color: var(--boja-akcent); }
</style>

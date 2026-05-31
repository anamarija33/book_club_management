<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useObavijestiStore } from '@/stores/obavijesti'
import { dohvatiKlub, kreirajKlub, azurirajKlub } from '@/services/klubovi'
import FormaPolje from '@/components/FormaPolje.vue'
import Gumb from '@/components/Gumb.vue'

const route = useRoute()
const router = useRouter()
const obavijesti = useObavijestiStore()

const id = computed(() => {
  const p = route.params['id']
  return p ? Number(p) : null
})
const jeUredi = computed(() => id.value !== null)

const naziv = ref('')
const opis = ref('')
const maxClanova = ref('')
const minSatiTjedan = ref('')
const stranicaTjedan = ref('')
const rokPrijave = ref('')
const ucitava = ref(false)

const greske = ref({
  naziv: '',
  maxClanova: '',
  minSatiTjedan: '',
  stranicaTjedan: '',
  rokPrijave: '',
})

onMounted(async () => {
  if (!jeUredi.value || !id.value) return
  try {
    const k = await dohvatiKlub(id.value)
    naziv.value = k.name
    opis.value = k.description ?? ''
    maxClanova.value = String(k.max_members)
    minSatiTjedan.value = String(k.min_hours_per_week)
    stranicaTjedan.value = String(k.pages_per_week)
    rokPrijave.value = k.registration_deadline.slice(0, 16)
  } catch {
    obavijesti.greska('Greška pri dohvatu kluba.')
    router.push('/admin/klubovi')
  }
})

function validiraj(): boolean {
  greske.value.naziv = naziv.value.trim() ? '' : 'Naziv je obavezan.'
  greske.value.maxClanova = maxClanova.value && Number(maxClanova.value) > 0 ? '' : 'Unesite pozitivan broj.'
  greske.value.minSatiTjedan = minSatiTjedan.value && Number(minSatiTjedan.value) >= 0 ? '' : 'Unesite broj >= 0.'
  greske.value.stranicaTjedan = stranicaTjedan.value && Number(stranicaTjedan.value) >= 0 ? '' : 'Unesite broj >= 0.'
  greske.value.rokPrijave = rokPrijave.value ? '' : 'Rok prijave je obavezan.'
  return !Object.values(greske.value).some(Boolean)
}

async function spremi(): Promise<void> {
  if (!validiraj()) return
  ucitava.value = true
  try {
    const tijelo = {
      name: naziv.value.trim(),
      description: opis.value.trim() || null,
      max_members: Number(maxClanova.value),
      min_hours_per_week: Number(minSatiTjedan.value),
      pages_per_week: Number(stranicaTjedan.value),
      registration_deadline: rokPrijave.value,
    }
    if (jeUredi.value && id.value) {
      await azurirajKlub(id.value, tijelo)
      obavijesti.uspjeh('Klub ažuriran.')
    } else {
      await kreirajKlub(tijelo)
      obavijesti.uspjeh('Klub kreiran.')
    }
    await router.push('/admin/klubovi')
  } catch (e) {
    obavijesti.greska(e instanceof Error ? e.message : 'Greška pri spremanju.')
  } finally {
    ucitava.value = false
  }
}
</script>

<template>
  <div class="pogled">
    <RouterLink to="/admin/klubovi" class="natrag">← Klubovi</RouterLink>
    <h1>{{ jeUredi ? 'Uredi klub' : 'Novi klub' }}</h1>

    <form class="forma" @submit.prevent="spremi">
      <FormaPolje
        oznaka="Naziv"
        v-model="naziv"
        :greska="greske.naziv"
        :obavezno="true"
      />
      <div class="polje">
        <label for="opis">Opis</label>
        <textarea id="opis" v-model="opis" class="textarea" rows="3" placeholder="Neobavezno..." />
      </div>
      <FormaPolje
        oznaka="Maks. broj članova"
        v-model="maxClanova"
        vrsta="number"
        :greska="greske.maxClanova"
        :obavezno="true"
      />
      <FormaPolje
        oznaka="Min. sati čitanja tjedno"
        v-model="minSatiTjedan"
        vrsta="number"
        :greska="greske.minSatiTjedan"
        :obavezno="true"
      />
      <FormaPolje
        oznaka="Stranica tjedno"
        v-model="stranicaTjedan"
        vrsta="number"
        :greska="greske.stranicaTjedan"
        :obavezno="true"
      />
      <FormaPolje
        oznaka="Rok prijave"
        v-model="rokPrijave"
        vrsta="datetime-local"
        :greska="greske.rokPrijave"
        :obavezno="true"
      />

      <div class="akcije">
        <RouterLink to="/admin/klubovi">
          <Gumb vrsta="sekundarni">Odustani</Gumb>
        </RouterLink>
        <Gumb tip="submit" :ucitava="ucitava">Spremi</Gumb>
      </div>
    </form>
  </div>
</template>

<style scoped>
.pogled {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  max-width: 520px;
}

.natrag {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--boja-tekst-mute);
  transition: color var(--tranzicija);
}

.natrag:hover { color: var(--boja-tekst); }

.forma {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  padding: 2rem;
  background: var(--boja-povrsina);
  border: 1px solid var(--boja-rub);
}

.polje { display: flex; flex-direction: column; gap: 0.4rem; }

.polje label {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--boja-tekst-mute);
}

.textarea {
  background: var(--boja-pozadina);
  border: 1px solid var(--boja-rub);
  color: var(--boja-tekst);
  padding: 0.625rem 0.875rem;
  font-family: var(--font-body);
  font-size: 0.875rem;
  resize: vertical;
}

.textarea:focus { outline: none; border-color: var(--boja-akcent); }

.akcije {
  display: flex;
  gap: 1rem;
  margin-top: 0.5rem;
}
</style>

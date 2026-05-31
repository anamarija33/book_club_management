<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useObavijestiStore } from '@/stores/obavijesti'
import { dohvatiKnjigu, kreirajKnjigu, azurirajKnjigu } from '@/services/knjige'
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

const naslov = ref('')
const autor = ref('')
const stranice = ref('')
const opis = ref('')
const ucitava = ref(false)

const greske = ref({
  naslov: '',
  autor: '',
  stranice: '',
})

onMounted(async () => {
  if (!jeUredi.value || !id.value) return
  try {
    const k = await dohvatiKnjigu(id.value)
    naslov.value = k.title
    autor.value = k.author
    stranice.value = String(k.pages)
    opis.value = k.description ?? ''
  } catch {
    obavijesti.greska('Greška pri dohvatu knjige.')
    router.push('/admin/knjige')
  }
})

function validiraj(): boolean {
  greske.value.naslov = naslov.value.trim() ? '' : 'Naslov je obavezan.'
  greske.value.autor = autor.value.trim() ? '' : 'Autor je obavezan.'
  greske.value.stranice = stranice.value && Number(stranice.value) > 0 ? '' : 'Unesite pozitivan broj stranica.'
  return !Object.values(greske.value).some(Boolean)
}

async function spremi(): Promise<void> {
  if (!validiraj()) return
  ucitava.value = true
  try {
    const tijelo = {
      title: naslov.value.trim(),
      author: autor.value.trim(),
      pages: Number(stranice.value),
      description: opis.value.trim() || null,
    }
    if (jeUredi.value && id.value) {
      await azurirajKnjigu(id.value, tijelo)
      obavijesti.uspjeh('Knjiga ažurirana.')
    } else {
      await kreirajKnjigu(tijelo)
      obavijesti.uspjeh('Knjiga dodana u katalog.')
    }
    await router.push('/admin/knjige')
  } catch (e) {
    obavijesti.greska(e instanceof Error ? e.message : 'Greška pri spremanju.')
  } finally {
    ucitava.value = false
  }
}
</script>

<template>
  <div class="pogled">
    <RouterLink to="/admin/knjige" class="natrag">← Knjige</RouterLink>
    <h1>{{ jeUredi ? 'Uredi knjigu' : 'Nova knjiga' }}</h1>

    <form class="forma" @submit.prevent="spremi">
      <FormaPolje
        oznaka="Naslov"
        v-model="naslov"
        :greska="greske.naslov"
        :obavezno="true"
      />
      <FormaPolje
        oznaka="Autor"
        v-model="autor"
        :greska="greske.autor"
        :obavezno="true"
      />
      <FormaPolje
        oznaka="Broj stranica"
        v-model="stranice"
        vrsta="number"
        :greska="greske.stranice"
        :obavezno="true"
      />
      <div class="polje">
        <label for="opis">Opis</label>
        <textarea id="opis" v-model="opis" class="textarea" rows="4" placeholder="Neobavezno..." />
      </div>

      <div class="akcije">
        <RouterLink to="/admin/knjige">
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

.akcije { display: flex; gap: 1rem; margin-top: 0.5rem; }
</style>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useObavijestiStore } from '@/stores/obavijesti'
import { dohvatiKorisnika, kreirajKorisnika, azurirajKorisnika } from '@/services/korisnici'

const route = useRoute()
const router = useRouter()
const obavijesti = useObavijestiStore()

const jeUredivanje = computed(() => !!route.params.id)
const naslov = computed(() => jeUredivanje.value ? 'Uredi korisnika' : 'Novi korisnik')

const username = ref('')
const email = ref('')
const password = ref('')
const role = ref<'admin' | 'member'>('member')
const isActive = ref(true)
const hoursPerWeek = ref(0)
const pagesPerWeek = ref(0)
const ucitava = ref(false)
const ucitavaPodatke = ref(false)

onMounted(async () => {
  if (!jeUredivanje.value) return
  ucitavaPodatke.value = true
  try {
    const k = await dohvatiKorisnika(Number(route.params.id))
    username.value = k.username
    email.value = k.email
    role.value = k.role
    isActive.value = k.is_active
    hoursPerWeek.value = k.hours_per_week
    pagesPerWeek.value = k.pages_per_week
  } catch (e) {
    obavijesti.greska(e instanceof Error ? e.message : 'Greška pri dohvatu korisnika.')
    await router.push('/admin/korisnici')
  } finally {
    ucitavaPodatke.value = false
  }
})

async function spremi(): Promise<void> {
  ucitava.value = true
  try {
    if (jeUredivanje.value) {
      const tijelo: Record<string, unknown> = {
        username: username.value,
        email: email.value,
        role: role.value,
        is_active: isActive.value,
        hours_per_week: hoursPerWeek.value,
        pages_per_week: pagesPerWeek.value,
      }
      if (password.value) tijelo.password = password.value
      await azurirajKorisnika(Number(route.params.id), tijelo)
      obavijesti.uspjeh('Korisnik ažuriran.')
    } else {
      await kreirajKorisnika({
        username: username.value,
        email: email.value,
        password: password.value,
        role: role.value,
        is_active: isActive.value,
        hours_per_week: hoursPerWeek.value,
        pages_per_week: pagesPerWeek.value,
      })
      obavijesti.uspjeh('Korisnik kreiran.')
    }
    await router.push('/admin/korisnici')
  } catch (e) {
    obavijesti.greska(e instanceof Error ? e.message : 'Greška pri spremanju.')
  } finally {
    ucitava.value = false
  }
}
</script>

<template>
  <div class="pogled">
    <div class="zaglavlje">
      <RouterLink to="/admin/korisnici" class="natrag">← Korisnici</RouterLink>
      <h1>{{ naslov }}</h1>
    </div>

    <div v-if="ucitavaPodatke" class="muted">Učitavanje...</div>

    <form v-else class="forma" @submit.prevent="spremi">
      <div class="sekcija">
        <div class="polje">
          <label for="username">Korisničko ime *</label>
          <input id="username" v-model="username" type="text" required autocomplete="off" />
        </div>
        <div class="polje">
          <label for="email">Email *</label>
          <input id="email" v-model="email" type="email" required />
        </div>
        <div class="polje">
          <label for="lozinka">
            Lozinka {{ jeUredivanje ? '(ostavite prazno za zadržavanje)' : '*' }}
          </label>
          <input
            id="lozinka"
            v-model="password"
            type="password"
            :required="!jeUredivanje"
            autocomplete="new-password"
            minlength="8"
          />
        </div>
      </div>

      <div class="sekcija">
        <div class="polje">
          <label for="uloga">Uloga</label>
          <select id="uloga" v-model="role">
            <option value="member">Član</option>
            <option value="admin">Admin</option>
          </select>
        </div>
        <div class="polje polje--checkbox">
          <label class="checkbox-oznaka">
            <input type="checkbox" v-model="isActive" />
            <span>Aktivan račun</span>
          </label>
        </div>
      </div>

      <div class="sekcija">
        <div class="polje">
          <label for="sati">Sati čitanja / tjedan</label>
          <input id="sati" v-model.number="hoursPerWeek" type="number" min="0" step="0.5" />
        </div>
        <div class="polje">
          <label for="stranice">Stranica / tjedan</label>
          <input id="stranice" v-model.number="pagesPerWeek" type="number" min="0" />
        </div>
      </div>

      <div class="akcije">
        <RouterLink to="/admin/korisnici" class="gumb-odustani">Odustani</RouterLink>
        <button type="submit" class="gumb-spremi" :disabled="ucitava">
          {{ ucitava ? 'Spremanje...' : 'Spremi' }}
        </button>
      </div>
    </form>
  </div>
</template>

<style scoped>
.pogled {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  max-width: 640px;
}

.zaglavlje {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.natrag {
  font-size: 0.75rem;
  color: var(--boja-tekst-mute);
  transition: color var(--tranzicija);
}

.natrag:hover { color: var(--boja-tekst); }

.forma { display: flex; flex-direction: column; gap: 2rem; }

.sekcija {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1.25rem;
}

.polje {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.polje--checkbox {
  justify-content: flex-end;
  padding-bottom: 0.1rem;
}

label {
  font-size: 0.75rem;
  color: var(--boja-tekst-mute);
  letter-spacing: 0.03em;
}

input, select {
  background: var(--boja-pozadina);
  border: 1px solid var(--boja-rub);
  border-radius: var(--radijus);
  color: var(--boja-tekst);
  padding: 0.625rem 0.875rem;
  transition: border-color var(--tranzicija);
}

input:focus, select:focus {
  outline: none;
  border-color: var(--boja-akcent);
}

.checkbox-oznaka {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
  color: var(--boja-tekst);
}

.checkbox-oznaka input[type="checkbox"] { width: 1rem; height: 1rem; cursor: pointer; }

.akcije {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding-top: 0.5rem;
  border-top: 1px solid var(--boja-rub);
}

.gumb-spremi {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  padding: 0.625rem 1.5rem;
  background: var(--boja-akcent);
  color: var(--boja-tekst);
  border: none;
  cursor: pointer;
  transition: background var(--tranzicija), opacity var(--tranzicija);
}

.gumb-spremi:hover:not(:disabled) { background: var(--boja-tekst); color: var(--boja-pozadina); }
.gumb-spremi:disabled { opacity: 0.5; cursor: not-allowed; }

.gumb-odustani {
  font-size: 0.8rem;
  color: var(--boja-tekst-mute);
  transition: color var(--tranzicija);
}

.gumb-odustani:hover { color: var(--boja-tekst); }
</style>

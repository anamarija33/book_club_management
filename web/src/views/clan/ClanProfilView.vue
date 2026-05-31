<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useObavijestiStore } from '@/stores/obavijesti'
import { azurirajMojProfil } from '@/services/korisnici'

const auth = useAuthStore()
const obavijesti = useObavijestiStore()

const email = ref(auth.user?.email ?? '')
const novaLozinka = ref('')
const potvrdiLozinku = ref('')
const hoursPerWeek = ref(auth.user?.hours_per_week ?? 0)
const pagesPerWeek = ref(auth.user?.pages_per_week ?? 0)
const ucitava = ref(false)

async function spremi(): Promise<void> {
  if (novaLozinka.value && novaLozinka.value !== potvrdiLozinku.value) {
    obavijesti.greska('Lozinke se ne podudaraju.')
    return
  }
  if (novaLozinka.value && novaLozinka.value.length < 8) {
    obavijesti.greska('Lozinka mora imati najmanje 8 znakova.')
    return
  }

  ucitava.value = true
  try {
    const tijelo: Record<string, unknown> = {
      email: email.value,
      hours_per_week: hoursPerWeek.value,
      pages_per_week: pagesPerWeek.value,
    }
    if (novaLozinka.value) tijelo.password = novaLozinka.value

    await azurirajMojProfil(tijelo)
    await auth.dohvatiMene()
    novaLozinka.value = ''
    potvrdiLozinku.value = ''
    obavijesti.uspjeh('Profil ažuriran.')
  } catch (e) {
    obavijesti.greska(e instanceof Error ? e.message : 'Greška pri ažuriranju profila.')
  } finally {
    ucitava.value = false
  }
}
</script>

<template>
  <div class="pogled">
    <h1>Moj profil</h1>
    <p class="muted">Ažurirajte svoje podatke i tempo čitanja.</p>

    <form class="forma" @submit.prevent="spremi">
      <div class="sekcija">
        <h2 class="sekcija-naslov">Osnovni podaci</h2>
        <div class="polja">
          <div class="polje">
            <label for="korisnicko-ime">Korisničko ime</label>
            <input
              id="korisnicko-ime"
              :value="auth.user?.username"
              type="text"
              disabled
              class="onemoguceno"
            />
            <span class="pomoc">Korisničko ime nije moguće promijeniti.</span>
          </div>
          <div class="polje">
            <label for="email">Email *</label>
            <input id="email" v-model="email" type="email" required />
          </div>
        </div>
      </div>

      <div class="sekcija">
        <h2 class="sekcija-naslov">Promjena lozinke</h2>
        <div class="polja">
          <div class="polje">
            <label for="nova-lozinka">Nova lozinka</label>
            <input
              id="nova-lozinka"
              v-model="novaLozinka"
              type="password"
              placeholder="Ostavite prazno za zadržavanje"
              autocomplete="new-password"
            />
          </div>
          <div class="polje">
            <label for="potvrdi-lozinku">Potvrdi lozinku</label>
            <input
              id="potvrdi-lozinku"
              v-model="potvrdiLozinku"
              type="password"
              placeholder="Ponovite novu lozinku"
              autocomplete="new-password"
            />
          </div>
        </div>
      </div>

      <div class="sekcija">
        <h2 class="sekcija-naslov">Tempo čitanja</h2>
        <p class="muted sekcija-opis">
          Ovi podaci se uspoređuju s minimalnim uvjetima knjižnih klubova pri prijavi.
        </p>
        <div class="polja">
          <div class="polje">
            <label for="sati">Sati čitanja tjedno</label>
            <input id="sati" v-model.number="hoursPerWeek" type="number" min="0" step="0.5" />
          </div>
          <div class="polje">
            <label for="stranice">Stranica tjedno</label>
            <input id="stranice" v-model.number="pagesPerWeek" type="number" min="0" />
          </div>
        </div>
      </div>

      <div class="akcije">
        <button type="submit" class="gumb-spremi" :disabled="ucitava">
          {{ ucitava ? 'Spremanje...' : 'Spremi promjene' }}
        </button>
      </div>
    </form>
  </div>
</template>

<style scoped>
.pogled {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-width: 680px;
}

.forma {
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
  margin-top: 1.5rem;
}

.sekcija {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.sekcija-naslov {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--boja-tekst-mute);
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--boja-rub);
}

.sekcija-opis {
  font-size: 0.8rem;
  margin-top: -0.5rem;
}

.polja {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1.25rem;
}

.polje {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

label {
  font-size: 0.75rem;
  color: var(--boja-tekst-mute);
  letter-spacing: 0.03em;
}

input {
  background: var(--boja-pozadina);
  border: 1px solid var(--boja-rub);
  border-radius: var(--radijus);
  color: var(--boja-tekst);
  padding: 0.625rem 0.875rem;
  transition: border-color var(--tranzicija);
}

input:focus {
  outline: none;
  border-color: var(--boja-akcent);
}

input.onemoguceno {
  opacity: 0.4;
  cursor: not-allowed;
}

.pomoc {
  font-size: 0.72rem;
  color: var(--boja-tekst-mute);
}

.akcije {
  padding-top: 0.5rem;
  border-top: 1px solid var(--boja-rub);
}

.gumb-spremi {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  padding: 0.625rem 1.75rem;
  background: var(--boja-akcent);
  color: var(--boja-tekst);
  border: none;
  cursor: pointer;
  transition: background var(--tranzicija), opacity var(--tranzicija);
}

.gumb-spremi:hover:not(:disabled) { background: var(--boja-tekst); color: var(--boja-pozadina); }
.gumb-spremi:disabled { opacity: 0.5; cursor: not-allowed; }
</style>

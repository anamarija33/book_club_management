<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useObavijestiStore } from '@/stores/obavijesti'
import { ApiGreska } from '@/services/api'

const router = useRouter()
const auth = useAuthStore()
const obavijesti = useObavijestiStore()

const korisnickoIme = ref('')
const lozinka = ref('')
const ucitava = ref(false)

async function prijava(): Promise<void> {
  ucitava.value = true
  try {
    await auth.login(korisnickoIme.value, lozinka.value)
    const odrediste = auth.isAdmin ? '/admin/pocetna' : '/clan/pocetna'
    await router.push(odrediste)
  } catch (e) {
    obavijesti.greska(e instanceof ApiGreska ? e.message : 'Greška pri prijavi.')
  } finally {
    ucitava.value = false
  }
}
</script>

<template>
  <div class="stranica">
    <div class="lijeva-strana">
      <div class="citat">
        <span class="navodnici">"</span>
        <p>A reader lives a thousand lives before he dies. The man who never reads lives only one.</p>
        <span class="autor">— George R.R. Martin</span>
      </div>
    </div>

    <div class="desna-strana">
      <div class="forma-kontejner">
        <div class="zaglavlje">
          <span class="ikona">📖</span>
          <h1>Book Club</h1>
          <p class="podnaslov">Prijava u sustav</p>
        </div>

        <form class="forma" @submit.prevent="prijava">
          <div class="polje">
            <label for="korisnicko-ime">Korisničko ime</label>
            <input
              id="korisnicko-ime"
              data-testid="korisnicko-ime"
              v-model="korisnickoIme"
              type="text"
              placeholder="unesite korisničko ime"
              autocomplete="username"
              required
            />
          </div>
          <div class="polje">
            <label for="lozinka">Lozinka</label>
            <input
              id="lozinka"
              data-testid="lozinka"
              v-model="lozinka"
              type="password"
              placeholder="••••••••"
              autocomplete="current-password"
              required
            />
          </div>
          <button type="submit" data-testid="submit" class="gumb-prijava" :disabled="ucitava">
            <span v-if="ucitava" class="spinner" />
            {{ ucitava ? 'Prijava...' : 'Prijava' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stranica {
  display: flex;
  min-height: 100vh;
  width: 100%;
}

/* ---- Lijeva strana ---- */
.lijeva-strana {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  background: var(--boja-povrsina);
  border-right: 1px solid var(--boja-rub);
}

.citat {
  max-width: 380px;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.navodnici {
  font-family: var(--font-display);
  font-size: 6rem;
  color: var(--boja-akcent);
  opacity: 0.4;
  line-height: 0.5;
}

.citat p {
  font-family: var(--font-display);
  font-style: italic;
  font-size: 1.25rem;
  line-height: 1.6;
  color: var(--boja-tekst);
}

.autor {
  font-size: 0.8rem;
  color: var(--boja-tekst-mute);
  letter-spacing: 0.04em;
}

/* ---- Desna strana ---- */
.desna-strana {
  flex: 0 0 440px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: var(--boja-pozadina);
}

.forma-kontejner {
  width: 100%;
  max-width: 360px;
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
}

.zaglavlje {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.ikona {
  font-size: 2.5rem;
  line-height: 1;
}

h1 {
  font-family: var(--font-display);
  font-size: 2.25rem;
  color: var(--boja-tekst);
}

.podnaslov {
  font-size: 0.875rem;
  color: var(--boja-tekst-mute);
}

.forma {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.polje {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

label {
  font-size: 0.75rem;
  color: var(--boja-tekst-mute);
  letter-spacing: 0.04em;
}

input {
  background: var(--boja-povrsina);
  border: 1px solid var(--boja-rub);
  border-radius: var(--radijus);
  color: var(--boja-tekst);
  padding: 0.75rem 1rem;
  transition: border-color var(--tranzicija), box-shadow var(--tranzicija);
}

input:focus {
  outline: none;
  border-color: var(--boja-akcent);
  box-shadow: 0 0 0 3px rgba(192, 139, 58, 0.12);
}

input::placeholder {
  color: var(--boja-tekst-mute);
  opacity: 0.5;
}

.gumb-prijava {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background: var(--boja-akcent);
  color: var(--boja-pozadina);
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 1rem;
  letter-spacing: 0.04em;
  padding: 0.875rem;
  border-radius: var(--radijus);
  margin-top: 0.5rem;
  transition: background var(--tranzicija), opacity var(--tranzicija);
}

.gumb-prijava:hover:not(:disabled) {
  background: var(--boja-akcent-svijetla);
}

.gumb-prijava:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(0, 0, 0, 0.2);
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  flex-shrink: 0;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Mobile: stack vertically */
@media (max-width: 640px) {
  .stranica { flex-direction: column; }
  .lijeva-strana { display: none; }
  .desna-strana { flex: 1; }
}
</style>

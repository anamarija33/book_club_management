<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

async function odjava(): Promise<void> {
  auth.logout()
  await router.push('/prijava')
}
</script>

<template>
  <nav class="nav">
    <div class="nav-lijevo">
      <RouterLink to="/" class="brand">
        <span class="brand-ikona">📖</span>
        <span class="brand-tekst">Book Club</span>
      </RouterLink>

      <div v-if="auth.isAdmin" class="linkovi">
        <RouterLink to="/admin/pocetna" class="link">Početna</RouterLink>
        <RouterLink to="/admin/klubovi" class="link">Klubovi</RouterLink>
        <RouterLink to="/admin/knjige" class="link">Knjige</RouterLink>
        <RouterLink to="/admin/korisnici" class="link">Korisnici</RouterLink>
      </div>

      <div v-else-if="auth.isMember" class="linkovi">
        <RouterLink to="/clan/pocetna" class="link">Početna</RouterLink>
        <RouterLink to="/clan/klubovi" class="link">Klubovi</RouterLink>
        <RouterLink to="/clan/clanstva" class="link">Članstva</RouterLink>
        <RouterLink to="/clan/knjige" class="link">Katalog</RouterLink>
        <RouterLink to="/clan/moje-knjige" class="link">Pročitane</RouterLink>
        <RouterLink to="/clan/profil" class="link">Profil</RouterLink>
      </div>
    </div>

    <div v-if="auth.isAuthenticated" class="nav-desno">
      <span class="korisnik-chip">
        <span class="korisnik-uloga">{{ auth.isAdmin ? 'Admin' : 'Član' }}</span>
        <span class="korisnik-ime">{{ auth.user?.username }}</span>
      </span>
      <button class="gumb-odjava" @click="odjava">Odjava</button>
    </div>
  </nav>
</template>

<style scoped>
.nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
  height: 60px;
  background: var(--boja-povrsina);
  border-bottom: 1px solid var(--boja-rub);
  box-shadow: 0 1px 8px rgba(0, 0, 0, 0.4);
}

.nav-lijevo {
  display: flex;
  align-items: center;
  gap: 2.5rem;
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
}

.brand-ikona {
  font-size: 1.25rem;
  line-height: 1;
}

.brand-tekst {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 1.1rem;
  color: var(--boja-akcent);
  letter-spacing: 0.02em;
}

.linkovi {
  display: flex;
  align-items: center;
  gap: 0.125rem;
}

.link {
  font-size: 0.8rem;
  color: var(--boja-tekst-mute);
  padding: 0.4rem 0.875rem;
  border-radius: var(--radijus);
  transition: color var(--tranzicija), background var(--tranzicija);
  letter-spacing: 0.02em;
}

.link:hover {
  color: var(--boja-tekst);
  background: var(--boja-povrsina-2);
}

.link.router-link-active {
  color: var(--boja-akcent);
  background: rgba(192, 139, 58, 0.1);
}

.nav-desno {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.korisnik-chip {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  background: var(--boja-povrsina-2);
  border: 1px solid var(--boja-rub);
  border-radius: 100px;
}

.korisnik-uloga {
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--boja-akcent);
}

.korisnik-ime {
  font-size: 0.75rem;
  color: var(--boja-tekst-mute);
}

.gumb-odjava {
  font-size: 0.75rem;
  color: var(--boja-tekst-mute);
  padding: 0.3rem 0.75rem;
  border: 1px solid var(--boja-rub);
  border-radius: var(--radijus);
  transition: color var(--tranzicija), border-color var(--tranzicija);
}

.gumb-odjava:hover {
  color: var(--boja-tekst);
  border-color: var(--boja-tekst-mute);
}
</style>

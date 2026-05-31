<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { dohvatiStatistike } from '@/services/korisnici'

const auth = useAuthStore()

const stats = ref<{ total_users: number; total_clubs: number; total_books: number; total_memberships: number } | null>(null)

onMounted(async () => {
  try {
    stats.value = await dohvatiStatistike()
  } catch {
    // Statistike su neobavezne
  }
})
</script>

<template>
  <div class="pogled">
    <h1>Administratorska ploča</h1>
    <p class="muted">Dobrodošli, {{ auth.user?.username }}.</p>

    <div class="kartice">
      <div class="kartica">
        <span class="kartica-broj">{{ stats?.total_users ?? '—' }}</span>
        <span class="kartica-oznaka">Korisnika</span>
        <RouterLink to="/admin/korisnici" class="kartica-veza">Upravljaj →</RouterLink>
      </div>
      <div class="kartica">
        <span class="kartica-broj">{{ stats?.total_clubs ?? '—' }}</span>
        <span class="kartica-oznaka">Knjižnih klubova</span>
        <RouterLink to="/admin/klubovi" class="kartica-veza">Upravljaj →</RouterLink>
      </div>
      <div class="kartica">
        <span class="kartica-broj">{{ stats?.total_books ?? '—' }}</span>
        <span class="kartica-oznaka">Knjiga u katalogu</span>
        <RouterLink to="/admin/knjige" class="kartica-veza">Upravljaj →</RouterLink>
      </div>
      <div class="kartica">
        <span class="kartica-broj">{{ stats?.total_memberships ?? '—' }}</span>
        <span class="kartica-oznaka">Prijava u klubove</span>
        <span class="kartica-veza muted">Ukupno</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.pogled {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.kartice {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.kartica {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1.5rem;
  background: var(--boja-povrsina);
  border: 1px solid var(--boja-rub);
}

.kartica-broj {
  font-family: var(--font-display);
  font-size: 3rem;
  font-weight: 900;
  color: var(--boja-akcent);
  line-height: 1;
}

.kartica-oznaka {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--boja-tekst-mute);
}

.kartica-veza {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--boja-tekst-mute);
  margin-top: 0.5rem;
  transition: color var(--tranzicija);
}

.kartica-veza:hover { color: var(--boja-tekst); }
</style>

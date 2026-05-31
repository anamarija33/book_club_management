<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { dohvatiMojeKnjige } from '@/services/knjige'
import type { KorisnikKnjiga } from '@/types/knjiga'

const auth = useAuthStore()
const mojeKnjige = ref<KorisnikKnjiga[]>([])

onMounted(async () => {
  try {
    mojeKnjige.value = await dohvatiMojeKnjige()
  } catch {
    // Statistike su neobavezne
  }
})
</script>

<template>
  <div class="pogled">
    <h1>Dobrodošli</h1>
    <p class="muted">Prijavljeni kao {{ auth.user?.username }}.</p>

    <div class="kartice">
      <div class="kartica">
        <span class="kartica-broj">{{ mojeKnjige.length }}</span>
        <span class="kartica-oznaka">Pročitanih knjiga</span>
        <RouterLink to="/clan/moje-knjige" class="kartica-veza">Prikaži →</RouterLink>
      </div>
      <div class="kartica">
        <span class="kartica-broj">{{ auth.user?.hours_per_week ?? 0 }}</span>
        <span class="kartica-oznaka">Sati tjedno</span>
      </div>
      <div class="kartica">
        <span class="kartica-broj">{{ auth.user?.pages_per_week ?? 0 }}</span>
        <span class="kartica-oznaka">Stranica tjedno</span>
      </div>
    </div>

    <div class="brze-veze">
      <RouterLink to="/clan/klubovi" class="veza-kartica">
        <span class="veza-naslov">Knjižni klubovi</span>
        <span class="muted">Pregledaj i prijavi se u klub</span>
      </RouterLink>
      <RouterLink to="/clan/knjige" class="veza-kartica">
        <span class="veza-naslov">Katalog knjiga</span>
        <span class="muted">Označi knjige kao pročitane</span>
      </RouterLink>
      <RouterLink to="/clan/clanstva" class="veza-kartica">
        <span class="veza-naslov">Moja članstva</span>
        <span class="muted">Status tvojih prijava u klubove</span>
      </RouterLink>
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
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
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

.brze-veze {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1rem;
}

.veza-kartica {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  padding: 1.25rem 1.5rem;
  border: 1px solid var(--boja-rub);
  transition: border-color var(--tranzicija);
}

.veza-kartica:hover { border-color: var(--boja-tekst-mute); }

.veza-naslov {
  font-family: var(--font-display);
  font-size: 1rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.veza-kartica .muted { font-size: 0.75rem; }
</style>

<script setup lang="ts">
defineProps<{
  vrsta?: 'primarni' | 'sekundarni' | 'opasnost'
  velicina?: 'mali' | 'normalni'
  ucitava?: boolean
  onemoguceno?: boolean
  tip?: 'button' | 'submit' | 'reset'
  razlogOnemogucen?: string
}>()
</script>

<template>
  <button
    :type="tip ?? 'button'"
    :disabled="onemoguceno || ucitava"
    :title="onemoguceno ? razlogOnemogucen : undefined"
    :class="['gumb', `gumb--${vrsta ?? 'primarni'}`, `gumb--${velicina ?? 'normalni'}`]"
  >
    <slot>{{ ucitava ? 'Učitavanje...' : '' }}</slot>
  </button>
</template>

<style scoped>
.gumb {
  font-family: var(--font-display);
  font-weight: 600;
  letter-spacing: 0.03em;
  cursor: pointer;
  border-radius: var(--radijus);
  transition: background var(--tranzicija), color var(--tranzicija), border-color var(--tranzicija), opacity var(--tranzicija);
}

.gumb:disabled { opacity: 0.4; cursor: not-allowed; }

.gumb--normalni { padding: 0.6rem 1.5rem; font-size: 0.9rem; }
.gumb--mali    { padding: 0.3rem 0.875rem; font-size: 0.78rem; }

.gumb--primarni { background: var(--boja-akcent); color: var(--boja-pozadina); border: 1px solid transparent; }
.gumb--primarni:hover:not(:disabled) { background: var(--boja-akcent-svijetla); }

.gumb--sekundarni { background: transparent; color: var(--boja-tekst-mute); border: 1px solid var(--boja-rub); }
.gumb--sekundarni:hover:not(:disabled) { color: var(--boja-tekst); border-color: var(--boja-tekst-mute); }

.gumb--opasnost { background: transparent; color: var(--boja-akcent); border: 1px solid var(--boja-akcent); }
.gumb--opasnost:hover:not(:disabled) { background: rgba(192, 139, 58, 0.1); }
</style>

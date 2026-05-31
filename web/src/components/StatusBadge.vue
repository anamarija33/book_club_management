<script setup lang="ts">
defineProps<{ status: string }>()

const LABELE: Record<string, string> = {
  pending: 'Na čekanju',
  approved: 'Odobren',
  rejected: 'Odbijen',
}
</script>

<template>
  <span :class="['badge', `badge--${status}`]">{{ LABELE[status] ?? status }}</span>
</template>

<style scoped>
.badge {
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  padding: 0.2rem 0.5rem;
  border: 1px solid currentColor;
  white-space: nowrap;
}

.badge--pending   { color: var(--boja-upozorenje); }
.badge--approved  { color: var(--boja-uspjeh); }
.badge--rejected  { color: var(--boja-akcent); }
</style>

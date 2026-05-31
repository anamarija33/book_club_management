<script setup lang="ts">
// Layout za javne stranice (prijava, 404)
</script>

<template>
  <div class="layout-gost">
    <slot />
  </div>
</template>

<style scoped>
.layout-gost {
  min-height: 100vh;
  display: flex;
  align-items: stretch;
}
</style>

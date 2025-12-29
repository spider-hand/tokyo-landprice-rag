<template>
  <div ref="mapContainer" class="h-full w-full" />
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'

const mapContainer = ref<HTMLElement | null>(null)
let map: maplibregl.Map | null = null

onMounted(() => {
  if (mapContainer.value) {
    map = new maplibregl.Map({
      container: mapContainer.value,
      // @see: https://docs.carto.com/faqs/carto-basemaps
      style: 'https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json',
      center: [139.6917, 35.6895], // Tokyo
      zoom: 10,
    })

    map.addControl(new maplibregl.NavigationControl(), 'bottom-left')
  }
})

onUnmounted(() => {
  if (map) {
    map.remove()
    map = null
  }
})
</script>

<template>
  <div ref="mapContainer" class="h-full w-full" />
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import * as pmtiles from 'pmtiles'

const COLOR_PALETTE = ['#ffffb2', '#fecc5c', '#fd8d3c', '#f03b20', '#bd0026']

const mapContainer = ref<HTMLElement | null>(null)
let map: maplibregl.Map | null = null

const protocol = new pmtiles.Protocol()
maplibregl.addProtocol('pmtiles', protocol.tile)

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

    map.on('load', () => {
      map!.addSource('land-price', {
        type: 'vector',
        url: 'pmtiles://http://localhost:9000/tokyo-landprice-rag/land_price.pmtiles',
      })

      map!.addLayer({
        id: 'land-price-layer',
        type: 'circle',
        source: 'land-price',
        'source-layer': 'land_price',
        paint: {
          'circle-radius': 5,
          'circle-color': [
            'step',
            ['get', 'L01_006'],
            COLOR_PALETTE[0] as string,
            215000,
            COLOR_PALETTE[1] as string,
            370000,
            COLOR_PALETTE[2] as string,
            579000,
            COLOR_PALETTE[3] as string,
            1040000,
            COLOR_PALETTE[4] as string,
          ],
          'circle-opacity': 0.8,
          'circle-stroke-width': 1,
          'circle-stroke-color': '#ffffff',
          'circle-stroke-opacity': 0.2,
        },
      })
    })
  }
})

onUnmounted(() => {
  if (map) {
    map.remove()
    map = null
  }
})
</script>

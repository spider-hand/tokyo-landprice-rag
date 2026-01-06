<template>
  <div ref="mapContainer" class="h-full w-full" />
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import * as pmtiles from 'pmtiles'

const COLOR_PALETTE = [
  'rgb(153, 102, 255)',
  'rgb(54, 162, 235)',
  'rgb(75, 192, 192)',
  'rgb(255, 205, 86)',
  'rgb(255, 159, 64)',
  'rgb(255, 99, 132)',
]

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
        // @see: https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-L01-2025.html
        url: 'pmtiles:///data/L01-25_13.pmtiles',
      })

      map!.addLayer({
        id: 'land-price-layer',
        type: 'circle',
        source: 'land-price',
        'source-layer': 'L0125_13',
        paint: {
          'circle-radius': 5,
          'circle-color': [
            'step',
            ['get', 'L01_008'],
            COLOR_PALETTE[0] as string,
            35590,
            COLOR_PALETTE[1] as string,
            149000,
            COLOR_PALETTE[2] as string,
            514500,
            COLOR_PALETTE[3] as string,
            2520000,
            COLOR_PALETTE[4] as string,
            17287000,
            COLOR_PALETTE[5] as string,
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

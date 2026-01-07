<template>
  <div class="relative h-full w-full">
    <div ref="mapContainer" class="h-full w-full" />
    <div class="bg-background absolute bottom-4 left-4 rounded-lg p-2 shadow-lg">
      <div class="flex items-end gap-2 px-2 mb-1">
        <div class="font-semibold">Land Price in 2025</div>
        <div class="text-sm">(JPY per square meter)</div>
      </div>
      <ItemGroup>
        <Item v-for="(item, index) in legendItems" :key="index" class="flex items-center px-2 py-1">
          <div class="h-2 w-2 rounded-full" :style="{ backgroundColor: item.color }" />
          <span>{{ item.label }}</span>
        </Item>
      </ItemGroup>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import * as pmtiles from 'pmtiles'
import ItemGroup from './ui/item/ItemGroup.vue'
import Item from './ui/item/Item.vue'

const COLOR_PALETTE = [
  'rgb(153, 102, 255)',
  'rgb(54, 162, 235)',
  'rgb(75, 192, 192)',
  'rgb(255, 205, 86)',
  'rgb(255, 159, 64)',
  'rgb(255, 99, 132)',
]

const legendItems = [
  { color: COLOR_PALETTE[5], label: 'Top 1% (> ¥17,287,000)' },
  { color: COLOR_PALETTE[4], label: 'Top 10% (¥2,520,000 - ¥17,287,000)' },
  { color: COLOR_PALETTE[3], label: 'Top 50% (¥514,500 - ¥2,520,000)' },
  { color: COLOR_PALETTE[2], label: 'Bottom 50% (¥149,000 - ¥514,500)' },
  { color: COLOR_PALETTE[1], label: 'Bottom 10% (¥35,590 - ¥149,000)' },
  { color: COLOR_PALETTE[0], label: 'Bottom 1% (< ¥35,590)' },
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

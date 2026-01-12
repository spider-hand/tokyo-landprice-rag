<template>
  <div class="relative h-full w-full">
    <div ref="mapContainer" class="h-full w-full" />
    <div class="bg-background absolute bottom-4 left-4 rounded-lg p-2 shadow-lg">
      <div class="flex items-end gap-2 px-2 mb-1">
        <div class="font-semibold">{{ t.landPriceIn2025 }}</div>
        <div class="text-sm">({{ t.jpyPerSquareMeter }})</div>
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
import { onMounted, onUnmounted, ref, computed } from 'vue'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import * as pmtiles from 'pmtiles'
import ItemGroup from './ui/item/ItemGroup.vue'
import Item from './ui/item/Item.vue'
import useLanguage from '@/composables/useLanguage'

export interface MapClickEvent {
  lat: number
  lon: number
  isPoint: boolean
  address?: string
}

const emit = defineEmits<{
  mapClick: [event: MapClickEvent]
}>()

const { t } = useLanguage()

const COLOR_PALETTE = [
  'rgb(153, 102, 255)',
  'rgb(54, 162, 235)',
  'rgb(75, 192, 192)',
  'rgb(255, 205, 86)',
  'rgb(255, 159, 64)',
  'rgb(255, 99, 132)',
]

const legendItems = computed(() => [
  { color: COLOR_PALETTE[5], label: `${t.value.top} 1% (> ¥17,287,000)` },
  { color: COLOR_PALETTE[4], label: `${t.value.top} 10% (¥2,520,000 - ¥17,287,000)` },
  { color: COLOR_PALETTE[3], label: `${t.value.top} 50% (¥514,500 - ¥2,520,000)` },
  { color: COLOR_PALETTE[2], label: `${t.value.bottom} 50% (¥149,000 - ¥514,500)` },
  { color: COLOR_PALETTE[1], label: `${t.value.bottom} 10% (¥35,590 - ¥149,000)` },
  { color: COLOR_PALETTE[0], label: `${t.value.bottom} 1% (< ¥35,590)` },
])

const mapContainer = ref<HTMLElement | null>(null)
let map: maplibregl.Map | null = null

const protocol = new pmtiles.Protocol()
maplibregl.addProtocol('pmtiles', protocol.tile)

onMounted(() => {
  if (mapContainer.value) {
    map = new maplibregl.Map({
      container: mapContainer.value,
      style: {
        version: 8,
        sources: {
          'raster-tiles': {
            type: 'raster',
            tiles: [
              `https://api.mapbox.com/styles/v1/mapbox/streets-v12/tiles/{z}/{x}/{y}?access_token=${import.meta.env.VITE_MAPBOX_TOKEN}`,
            ],
            tileSize: 512,
            attribution:
              '© <a href="https://www.mapbox.com/about/maps/">Mapbox</a> © <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> <strong><a href="https://www.mapbox.com/map-feedback/" target="_blank">Improve this map</a></strong>',
          },
        },
        layers: [
          {
            id: 'raster-tiles-layer',
            type: 'raster',
            source: 'raster-tiles',
          },
        ],
      },
      center: [139.5803, 35.7023],
      zoom: 10,
      minZoom: 10,
      maxZoom: 16,
      maxBounds: [
        [138.8, 35.4],
        [140.1, 35.95],
      ],
    })

    map.on('load', () => {
      map!.addSource('land-price', {
        type: 'vector',
        url: import.meta.env.VITE_PMTILES_URL,
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

      map!.on('mouseenter', 'land-price-layer', () => {
        map!.getCanvas().style.cursor = 'pointer'
      })

      map!.on('mouseleave', 'land-price-layer', () => {
        map!.getCanvas().style.cursor = ''
      })

      map!.on('click', (e) => {
        const features = map!.queryRenderedFeatures(e.point, {
          layers: ['land-price-layer'],
        })

        if (features.length > 0) {
          // Handle click on a point feature
          const feature = features[0]!
          const geometry = feature.geometry as GeoJSON.Point
          const coordinates = geometry.coordinates
          emit('mapClick', {
            lat: coordinates[1] as number,
            lon: coordinates[0] as number,
            isPoint: true,
            address: feature.properties?.L01_025 as string | undefined,
          })
        } else {
          // Handle click on a non-feature area
          emit('mapClick', {
            lat: e.lngLat.lat,
            lon: e.lngLat.lng,
            isPoint: false,
          })
        }
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

<template>
  <SidebarProvider :default-open="true" style="--sidebar-width: 25rem" class="h-screen">
    <ChatComponent ref="chatComponent" />
    <SidebarInset>
      <MapComponent @map-click="handleMapClick" />
    </SidebarInset>
  </SidebarProvider>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { SidebarProvider, SidebarInset } from '@/components/ui/sidebar'
import ChatComponent from './components/ChatComponent.vue'
import MapComponent from '@/components/MapComponent.vue'
import type { MapClickEvent } from '@/components/MapComponent.vue'

const chatComponent = ref<InstanceType<typeof ChatComponent> | null>(null)

const handleMapClick = (event: MapClickEvent) => {
  chatComponent.value?.sendMapQuery(event)
}
</script>

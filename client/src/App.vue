<template>
  <SidebarProvider :default-open="true" style="--sidebar-width: 25rem" class="h-screen">
    <ChatComponent />
    <SidebarInset>
      <MapComponent />
    </SidebarInset>
  </SidebarProvider>
</template>

<script setup lang="ts">
import { SidebarProvider, SidebarInset } from '@/components/ui/sidebar'
import ChatComponent from './components/ChatComponent.vue'
import MapComponent from '@/components/MapComponent.vue'
</script>

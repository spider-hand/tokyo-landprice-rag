<template>
  <Sidebar collapsible="none">
    <SidebarHeader>
      <h1 class="text-lg font-semibold">Tokyo Land Price RAG</h1>
    </SidebarHeader>
    <SidebarContent>
      <ChatMessageComponent v-for="message in messages" :key="message.id" :message="message" />
    </SidebarContent>
    <SidebarFooter>
      <div class="flex flex-col rounded-md border border-input bg-background shadow-xs">
        <Textarea
          v-model="userInput"
          placeholder="Type your message..."
          class="min-h-20 resize-none border-0 p-3 shadow-none focus-visible:ring-0"
        />
        <div class="flex justify-end p-2">
          <Button size="icon" class="rounded-full">
            <ArrowRight />
          </Button>
        </div>
      </div>
    </SidebarFooter>
  </Sidebar>
</template>

<script setup lang="ts">
import { ArrowRight } from 'lucide-vue-next'
import Button from './ui/button/Button.vue'
import Sidebar from './ui/sidebar/Sidebar.vue'
import SidebarContent from './ui/sidebar/SidebarContent.vue'
import SidebarFooter from './ui/sidebar/SidebarFooter.vue'
import SidebarHeader from './ui/sidebar/SidebarHeader.vue'
import Textarea from './ui/textarea/Textarea.vue'
import { ref } from 'vue'
import ChatMessageComponent from './ChatMessageComponent.vue'

const userInput = ref('')

const messages = ref([
  { id: 1, role: 'agent', content: 'Hello! How can I help you today?' },
  { id: 2, role: 'user', content: 'Can you show me information about land prices in Tokyo?' },
  {
    id: 3,
    role: 'agent',
    content:
      'Sure! I can help you explore land price data in Tokyo. What specific area are you interested in?',
  },
])
</script>

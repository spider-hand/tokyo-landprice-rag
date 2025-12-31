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
          @keydown.enter.exact.prevent="sendMessage"
        />
        <div class="flex justify-end p-2">
          <Button
            size="icon"
            class="rounded-full"
            :disabled="isLoading || !userInput.trim()"
            @click="sendMessage"
          >
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
import { computed, ref } from 'vue'
import ChatMessageComponent from './ChatMessageComponent.vue'
import { MessagesApi } from '@/services'
import useApi from '@/composables/useApi'

interface ChatMessage {
  id: number
  role: 'user' | 'agent'
  content: string
}

const userInput = ref('')
const messages = ref<ChatMessage[]>([])
const isLoading = ref(false)

const nextMessageId = computed(() => messages.value.length)

const { apiConfig } = useApi()
const messagesApi = new MessagesApi(apiConfig)

const sendMessage = async () => {
  const message = userInput.value.trim()
  if (!message || isLoading.value) return

  messages.value.push({
    id: nextMessageId.value,
    role: 'user',
    content: message,
  })
  userInput.value = ''
  isLoading.value = true

  try {
    const response = await messagesApi.postMessage({
      postMessageRequest: { message },
    })
    messages.value.push({
      id: nextMessageId.value,
      role: 'agent',
      content: response.response ?? '',
    })
  } catch (error) {
    console.error('Failed to send message:', error)
  } finally {
    isLoading.value = false
  }
}
</script>

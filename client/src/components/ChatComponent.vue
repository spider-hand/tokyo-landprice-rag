<template>
  <Sidebar collapsible="none">
    <SidebarHeader>
      <h1 class="text-lg font-semibold">Tokyo Land Price RAG</h1>
    </SidebarHeader>
    <SidebarContent ref="chatContainer">
      <ChatMessageComponent v-for="message in messages" :key="message.id" :message="message" />
      <div v-if="isLoading" class="flex items-center p-4">
        <div class="flex items-center justify-center h-8 w-8">
          <Circle class="h-2 w-2 animate-ping fill-current" />
        </div>
      </div>
    </SidebarContent>
    <SidebarFooter>
      <div class="flex flex-col rounded-md border border-input bg-background shadow-xs">
        <Textarea
          v-model="userInput"
          placeholder="Type your message..."
          class="min-h-20 resize-none border-0 p-3 shadow-none focus-visible:ring-0"
          @keydown="handleKeydown"
          @compositionstart="isComposing = true"
          @compositionend="isComposing = false"
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
import { computed, ref, nextTick } from 'vue'
import ChatMessageComponent from './ChatMessageComponent.vue'
import { MessagesApi } from '@/services'
import useApi from '@/composables/useApi'
import { Circle } from 'lucide-vue-next'
import type { MapClickEvent } from './MapComponent.vue'

interface ChatMessage {
  id: number
  role: 'user' | 'agent'
  content: string
}

const userInput = ref('')
const messages = ref<ChatMessage[]>([])
const isLoading = ref(false)
// To handle IME composition events
const isComposing = ref(false)
const chatContainer = ref<InstanceType<typeof SidebarContent> | null>(null)

const nextMessageId = computed(() => messages.value.length)

const { apiConfig } = useApi()
const messagesApi = new MessagesApi(apiConfig)

const handleKeydown = (event: KeyboardEvent) => {
  // Prevent the message from being sent when composing text with an IME
  if (event.key === 'Enter' && !event.shiftKey && !isComposing.value) {
    event.preventDefault()
    sendMessage()
  }
}

const scrollToBottom = async () => {
  await nextTick()
  const el = chatContainer.value?.$el as HTMLElement | undefined
  if (el) {
    el.scrollTo({
      top: el.scrollHeight,
      behavior: 'smooth',
    })
  }
}

const sendMessage = async (event?: MapClickEvent) => {
  const message = userInput.value.trim()
  if (!message || isLoading.value) return

  messages.value.push({
    id: nextMessageId.value,
    role: 'user',
    content: message,
  })
  userInput.value = ''
  isLoading.value = true

  scrollToBottom()

  try {
    const response = await messagesApi.postMessage({
      postMessageRequest: {
        message,
        lat: event?.lat,
        lon: event?.lon,
        isPoint: event?.isPoint,
      },
    })
    messages.value.push({
      id: nextMessageId.value,
      role: 'agent',
      content: response.response ?? '',
    })

    scrollToBottom()
  } catch (error) {
    console.error('Failed to send message:', error)
  } finally {
    isLoading.value = false
  }
}

const sendMapQuery = (event: MapClickEvent) => {
  if (isLoading.value) return

  const message = event.isPoint
    ? `この地点について教えてください。`
    : `この周辺エリアについて教えてください。`

  userInput.value = message

  sendMessage(event)
}

defineExpose({
  sendMapQuery,
})
</script>

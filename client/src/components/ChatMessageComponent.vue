<template>
  <Item size="sm" class="items-start">
    <ItemMedia>
      <Avatar>
        <AvatarFallback class="bg-muted">
          <User v-if="message.role === 'user'" />
          <Bot v-else />
        </AvatarFallback>
      </Avatar>
    </ItemMedia>
    <ItemContent class="bg-muted p-3 rounded-2xl">
      <p class="text-sm" v-html="renderedContent"></p>
    </ItemContent>
  </Item>
</template>

<script setup lang="ts">
import type { PropType } from 'vue'
import Avatar from './ui/avatar/Avatar.vue'
import AvatarFallback from './ui/avatar/AvatarFallback.vue'
import Item from './ui/item/Item.vue'
import ItemContent from './ui/item/ItemContent.vue'
import ItemMedia from './ui/item/ItemMedia.vue'
import { micromark } from 'micromark'
import { User, Bot } from 'lucide-vue-next'

const props = defineProps({
  message: {
    type: Object as PropType<{ id: number; role: string; content: string }>,
    required: true,
  },
})

const renderedContent = micromark(props.message.content)
</script>

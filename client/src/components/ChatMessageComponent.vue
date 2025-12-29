<template>
  <Item variant="muted" size="sm" class="items-start">
    <ItemMedia>
      <Avatar>
        <AvatarFallback>
          {{ message.role === 'user' ? 'U' : 'A' }}
        </AvatarFallback>
      </Avatar>
    </ItemMedia>
    <ItemContent>
      <p class="text-sm">{{ message.content }}</p>
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

defineProps({
  message: {
    type: Object as PropType<{ id: number; role: string; content: string }>,
    required: true,
  },
})
</script>

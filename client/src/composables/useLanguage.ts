import { ref, computed } from 'vue'

const translations = {
  en: {
    placeholder: 'Type your message...',
    pointQuery: 'Tell me about this location.',
    areaQuery: 'Tell me about this area.',
    landPriceIn2025: 'Land Price in 2025',
    jpyPerSquareMeter: 'JPY per square meter',
    top: 'Top',
    bottom: 'Bottom',
  },
  ja: {
    placeholder: 'メッセージを入力...',
    pointQuery: 'この地点について教えてください。',
    areaQuery: 'この周辺エリアについて教えてください。',
    landPriceIn2025: '2025年の地価',
    jpyPerSquareMeter: '円/㎡',
    top: '上位',
    bottom: '下位',
  },
}

const isJapanese = ref(false)

const useLanguage = () => {
  const t = computed(() => (isJapanese.value ? translations.ja : translations.en))
  const code = computed(() => (isJapanese.value ? 'ja' : 'en'))

  return { isJapanese, t, code }
}

export default useLanguage

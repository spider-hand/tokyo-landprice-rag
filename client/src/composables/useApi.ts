import { Configuration } from '@/services'

const useApi = () => {
  const apiConfig = new Configuration({
    basePath: import.meta.env.VITE_API_BASE_URL,
  })

  return { apiConfig }
}

export default useApi

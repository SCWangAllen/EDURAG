import { ref } from 'vue'

export function useModal() {
  const isOpen = ref(false)
  const data = ref(null)

  const open = (d = null) => {
    data.value = d
    isOpen.value = true
  }

  const close = () => {
    isOpen.value = false
    data.value = null
  }

  return { isOpen, data, open, close }
}

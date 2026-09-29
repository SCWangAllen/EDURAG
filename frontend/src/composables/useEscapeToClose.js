import { watch, onUnmounted } from 'vue'

/**
 * 視窗開著時按 Esc 就關閉。用 document 層級監聽:視窗多半是 Teleport 或焦點還停在
 * 觸發按鈕上,掛在視窗內部的 @keydown.esc 收不到事件。
 * @param {() => boolean} isOpen  回傳視窗是否開啟(例如 () => props.visible)
 * @param {() => void} onClose    關閉動作(例如 () => emit('close'))
 */
export function useEscapeToClose(isOpen, onClose) {
  const handler = (event) => {
    if (event.key === 'Escape') onClose()
  }
  const add = () => document.addEventListener('keydown', handler)
  const remove = () => document.removeEventListener('keydown', handler)
  watch(isOpen, (open) => (open ? add() : remove()), { immediate: true })
  onUnmounted(remove)
}

import { onScopeDispose } from 'vue'

export function useRequestSequence() {
  let version = 0
  let active = true
  onScopeDispose(() => { active = false; version++ })
  return () => {
    const request = ++version
    return () => active && request === version
  }
}

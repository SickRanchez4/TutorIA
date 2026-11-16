import { computed, reactive, watch } from 'vue'

const states = new Map()
export function useListState(key) {
  if (!states.has(key)) states.set(key, reactive({ search: '', page: 1, pageSize: 10 }))
  return states.get(key)
}

export function clearListStates() {
  states.clear()
}

export function usePagination(source, state = reactive({ page: 1, pageSize: 10 }), ready = () => true) {
  const total = computed(() => source.value.length)
  const pages = computed(() => Math.max(1, Math.ceil(total.value / state.pageSize)))
  watch([pages, () => state.page, ready], () => {
    if (!ready()) return
    state.page = Math.min(Math.max(1, state.page), pages.value)
  }, { immediate: true })
  watch(() => state.pageSize, () => { state.page = 1 })
  if ('search' in state) watch(() => state.search, () => { state.page = 1 })
  return reactive({
    state,
    total,
    items: computed(() => source.value.slice((state.page - 1) * state.pageSize, state.page * state.pageSize)),
  })
}

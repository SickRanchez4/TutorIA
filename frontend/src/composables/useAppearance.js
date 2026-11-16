import { readonly, shallowRef } from 'vue'

const state = shallowRef(window.tutoriaAppearance.getState())

export function connectAppearance(vuetify) {
  return window.tutoriaAppearance.subscribe(value => {
    state.value = value
    vuetify.theme.change(`tutoria-${value.resolved}`)
  })
}

export function useAppearance() {
  return {
    appearance: readonly(state),
    setAppearance: value => window.tutoriaAppearance.setSelection(value),
  }
}

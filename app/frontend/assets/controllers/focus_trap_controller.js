import { Controller } from '@hotwired/stimulus'

const KEYCODE_TAB = 9
const KEY_TAB = 'Tab'
const focusElementsquerySelectorString =
  "a[href]:not([tabindex='-1']), area[href]:not([tabindex='-1']), input:not([disabled]):not([tabindex='-1']), select:not([disabled]):not([tabindex='-1']),textarea:not([disabled]):not([tabindex='-1']),button:not([disabled]):not([tabindex='-1']),iframe:not([tabindex='-1']),[tabindex]:not([tabindex='-1']),[contentEditable=true]:not([tabindex='-1'])"

export default class extends Controller {
  initialize() {
    this.element.controllers = this.element.controllers || {}
    this.element.controllers[this.identifier] = this
    this.focusBranch = null
    this.lastFocusElement = null
  }
  connect() {
    console.log(`${this.identifier} connected`)
    document.addEventListener('keydown', (e) => {
      this.keyDownHandler(e)
    })
  }
  getFocusableElements() {
    return this.focusBranch.querySelectorAll(focusElementsquerySelectorString)
  }
  setBranchElement(elem) {
    this.focusBranch = elem
    this.lastFocusElement = document.activeElement
    const focusableElements = this.getFocusableElements()
    if (focusableElements.length) {
      setTimeout(() => {
        focusableElements[0].focus()
      }, 100)
    }
  }
  removeBranchElement() {
    this.focusBranch = null
    this.lastFocusElement.focus()
  }
  keyDownHandler(e) {
    if (this.focusBranch) {
      var doSomething = e.key === KEY_TAB || e.keyCode === KEYCODE_TAB
      if (!doSomething) {
        return
      }
      const focusableElements = this.getFocusableElements()
      if (e.shiftKey) {
        /* shift + tab */ if (document.activeElement === focusableElements[0]) {
          focusableElements[focusableElements.length - 1].focus()
          e.preventDefault()
        }
      } /* tab */ else {
        if (document.activeElement === focusableElements[focusableElements.length - 1]) {
          focusableElements[0].focus()
          e.preventDefault()
        }
      }
    }
  }
}
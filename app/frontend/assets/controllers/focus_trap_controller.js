import { Controller } from '@hotwired/stimulus'

const KEYCODE_TAB = 9
const KEY_TAB = 'Tab'
const focusElementsquerySelectorString =
  "a[href]:not([tabindex='-1']), area[href]:not([tabindex='-1']), input:not([disabled]):not([tabindex='-1']), select:not([disabled]):not([tabindex='-1']),textarea:not([disabled]):not([tabindex='-1']),button:not([disabled]):not([tabindex='-1']),iframe:not([tabindex='-1']),[tabindex]:not([tabindex='-1']),[contentEditable=true]:not([tabindex='-1'])"

export default class extends Controller {
  static targets = ['branch']
  initialize() {
    this.element.controllers = this.element.controllers || {}
    this.element.controllers[this.identifier] = this
    this.focusBranch = null
    this.lastFocusElement = null
    this.visibilityOptions = {
      checkDisplayNone: true,
      // visibilityProperty: true,
      // opacityProperty: true,
      // contentVisibilityAuto: true,
    }
  }
  connect() {
    console.log(`${this.identifier} connected`)
    document.addEventListener('keydown', (e) => {
      this.keyDownHandler(e)
    })
  }
  isGenerallyVisible = (element) => {
    const style = window.getComputedStyle(element)
    console.log(style)
    return style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0'
  }
  isVisibleInViewport = (element) => {
    const rect = element.getBoundingClientRect()
    console.log('')
    console.log(element)
    console.log(rect)
    const vis =
      rect.top >= 0 &&
      rect.left >= 0 &&
      rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
      rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    console.log(vis)
    console.log(!!vis)
    console.log('')
    return vis
  }
  branchTargetConnected(target) {
    console.log('branch connected')
    this.setBranchElement(target)
  }
  branchTargetDisconnected() {
    this.removeBranchElement()
  }
  getFocusableElements() {
    return Array.from(this.focusBranch.querySelectorAll(focusElementsquerySelectorString)).filter(
      (elem) => this.isVisibleInViewport(elem)
    )
    // return Array.from(this.focusBranch.querySelectorAll(focusElementsquerySelectorString)).filter(elem => elem.checkVisibility(this.visibilityOptions))
  }
  setBranchElement(elem) {
    this.focusBranch = elem
    this.lastFocusElement = document.activeElement
    const focusableElements = this.getFocusableElements()
    console.log(focusableElements.length)
    // console.log(focusableElements[focusableElements.length - 1].checkVisibility(this.visibilityOptions))
    console.log(this.isVisibleInViewport(focusableElements[focusableElements.length - 1]))
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
      console.log(focusableElements.length)
      console.log('active: ', document.activeElement)
      console.log('last elem: ', focusableElements[focusableElements.length - 1])
      console.log(
        'last elem is visible: ',
        this.isVisibleInViewport(focusableElements[focusableElements.length - 1])
      )
      console.log(
        'active is last element: ',
        document.activeElement === focusableElements[focusableElements.length - 1]
      )
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

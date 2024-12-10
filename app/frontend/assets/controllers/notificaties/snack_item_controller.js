import { Controller } from '@hotwired/stimulus'

const SWIPE_TRESHOLD = 100
const MAX_CHARACTERS = 200
export default class extends Controller {
  static targets = ['content', 'titel']

  initialize() {
    this.element.controller = this
    this.manager = null
    this.initialTouchX = null
    this.finalTouchX = null
    this.deltaX = null

    if ('ontouchstart' in window) {
      this.element.addEventListener('touchstart', (event) => {
        event.preventDefault()
        this.initialTouchX = event.touches[0].clientX
        const currentWidth = this.element.clientWidth
        this.element.style.width = `${currentWidth}px`
      })

      this.element.addEventListener('touchmove', (event) => {
        event.preventDefault()
        this.deltaX = this.initialTouchX - event.changedTouches[0].clientX
        this.element.style.marginLeft = `-${this.deltaX}px`
      })

      this.element.addEventListener('touchend', (event) => {
        event.preventDefault()
        this.finalTouchX = event.changedTouches[0].clientX
        if (this.deltaX < SWIPE_TRESHOLD) {
          this.element.style.marginLeft = 0
        }
        if (event.target.classList.contains('btn-close--small')) {
          this.manager.markeerSnackAlsGelezen(this.element.dataset.id)
        } else if (event.target.nodeName.toLowerCase() === 'a') {
          if (event.target.getAttribute('data-action')) {
            this[`${event.target.getAttribute('data-action').split('#')[1]}`]()
          }
        } else {
          this.handleSwipe(this.initialTouchX, this.finalTouchX)
        }
      })

      window.addEventListener('click', () => {
        if (this.element.closest('.container__notification')) {
          this.element.closest('.container__notification').classList.remove('expanded')
          this.element.closest('.container__notification').classList.add('collapsed')
        }
      })
    }
  }

  contentTargetConnected() {
    this.contentString = null
    let truncatedString = null
    if (this.hasContentTarget) {
      this.contentString = this.contentTarget.innerText
      if (this.contentString.length > MAX_CHARACTERS) {
        truncatedString = `${this.contentString.slice(
          0,
          MAX_CHARACTERS - 13
        )}... <a href="" data-action="notificaties--snack-item#readMore">Lees meer</a>`
        this.contentTarget.innerHTML = truncatedString
        setTimeout(() => {
          this.contentTarget.style.height = `${this.contentTarget.clientHeight}px`
          console.log('on TargetConnected, height: ', this.contentTarget.clientHeight)
        }, 500)
      }
    }
  }

  initializeManager(manager) {
    this.manager = manager

    setTimeout(() => {
      // if (!this.snackLijstTarget.classList.contains('expanded')) {
      this.element.classList.add('collapsed')
      // }
    }, 5000)
  }
  disconnect() {
    if ('ontouchstart' in window) {
      window.removeEventListener('click', () => {
        this.element.closest('.container__notification').classList.remove('expanded')
        this.element.closest('.container__notification').classList.add('collapsed')
      })
    }
  }
  readMore(e = null) {
    e?.preventDefault()
    this.contentTarget.style.height = `${this.contentTarget.clientHeight}px`
    console.log('before readMore, height: ', this.contentTarget.clientHeight)
    this.contentTarget.innerText = this.contentString
    this.contentTarget.style.height = `${this.contentTarget.scrollHeight}px`
    console.log('after readMore, height: ', this.contentTarget.style.height)
  }
  markeerAlsGelezen() {
    this.element.classList.add('hide')
    this.element.addEventListener('transitionend', () => {
      this.element.remove()
    })
  }
  sluitSnack() {
    this.manager.markeerSnackAlsGelezen(this.element.dataset.id)
  }
  handleSwipe() {
    this.element.closest('.container__notification').classList.remove('collapsed')
    this.element.closest('.container__notification').classList.add('expanded')
    if (this.initialTouchX - this.finalTouchX > SWIPE_TRESHOLD) {
      this.manager.markeerSnackAlsGelezen(this.element.dataset.id)
    }
  }
}

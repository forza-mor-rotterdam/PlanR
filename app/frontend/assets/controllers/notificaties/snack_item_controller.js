import { Controller } from '@hotwired/stimulus'

const SWIPE_TRESHOLD = 30
const MAX_CHARACTERS = 200
export default class extends Controller {
  static targets = ['content', 'titel']

  initialize() {
    this.element.controller = this
    this.manager = null
    this.startX = 0
    this.startY = 0
    this.currentX = 0
    this.currentY = 0
    this.isSwiping = false

    if ('ontouchstart' in window) {
      this.element.addEventListener('touchstart', (e) => {
        if (e.target.closest('A')) return
        this.startX = e.touches[0].clientX
        this.startY = e.touches[0].clientY
        this.currentX = this.startX // in het geval gebruiker alleen mmar tapt ipv swipet
        this.currentY = this.startY
        this.isSwiping = true
      })

      this.element.addEventListener('touchmove', (e) => {
        if (!this.isSwiping) return
        this.currentX = e.touches[0].clientX
        this.currentY = e.touches[0].clientY

        const deltaX = this.currentX - this.startX
        const deltaY = this.currentY - this.startY

        // Controlleer of de gebruiker horizontaal of verticaal swipet
        if (Math.abs(deltaX) > Math.abs(deltaY)) {
          // Horizontale swipe, voorkom scrollen
          e.preventDefault()
          if (deltaX < 0) {
            // only swipe to left
            this.element.style.transform = `translateX(${deltaX}px)`
          }
        }
      })

      this.element.addEventListener('touchend', (e) => {
        if (!this.isSwiping) return
        const swipeDistance = this.startX - this.currentX
        if (e.target.classList.contains('btn-close--small')) {
          this.manager.markeerSnackAlsGelezen(this.element.dataset.id, true)
        } else if (e.target.nodeName.toLowerCase() === 'a') {
          if (e.target.getAttribute('data-action')) {
            this[`${e.target.getAttribute('data-action').split('#')[1]}`]()
          }
        } else {
          if (swipeDistance > SWIPE_TRESHOLD) {
            this.element.style.transform = `translateX(-100%)`
            this.manager.markeerSnackAlsGelezen(this.element.dataset.id, false)
          } else if (swipeDistance < 10) {
            // Reset positie als swipe te kort is
            this.element.style.transform = `translateX(0)`
            this.element.closest('.container__notification').classList.remove('collapsed')
            this.element.closest('.container__notification').classList.add('expanded')
          } else {
            // Reset positie als swipe te kort is
            this.element.style.transform = `translateX(0)`
          }
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
  markeerAlsGelezen(hideByClass = true) {
    if (hideByClass) this.element.classList.add('hide')
    this.element.addEventListener('transitionend', () => {
      this.element.remove()
    })
  }
  sluitSnack() {
    this.manager.markeerSnackAlsGelezen(this.element.dataset.id, true)
  }
}

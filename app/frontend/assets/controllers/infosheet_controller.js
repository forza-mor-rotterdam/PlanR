import { Controller } from '@hotwired/stimulus'

const SWIPE_TRESHOLD = 100
let scrollPositionForDialog = 0
export default class extends Controller {
  static targets = ['infosheet', 'scrollHandle', 'infosheetTurboframe', 'toplevelContainer']

  connect() {
    this.handleKeydown = this.handleKeydown.bind(this)
    document.addEventListener('keydown', this.handleKeydown)
  }

  disconnect() {
    document.removeEventListener('keydown', this.handleKeydown)
  }

  handleKeydown(event) {
    if (event.key === 'Escape') {
      event.preventDefault()
      this.closeInfosheet()
    }
  }

  scrollHandleTargetConnected(element) {
    this.startX = 0
    this.startY = 0
    this.currentX = 0
    this.currentY = 0
    this.isSwiping = false
    if ('ontouchstart' in window) {
      element.addEventListener('touchstart', (e) => {
        this.handleTouchStart(e)
      })

      element.addEventListener('touchmove', (e) => {
        this.handleTouchMove(e)
      })

      element.addEventListener('touchend', () => {
        this.handleTouchEnd()
      })
    }
  }

  handleTouchStart(e) {
    this.startX = e.touches[0].clientX
    this.startY = e.touches[0].clientY
    this.currentX = this.startX // in het geval gebruiker alleen mmar tapt ipv swipet
    this.currentY = this.startY
    this.isSwiping = true
  }
  handleTouchMove(e) {
    if (!this.isSwiping) return
    this.currentX = e.touches[0].clientX
    this.currentY = e.touches[0].clientY

    const deltaX = this.currentX - this.startX
    const deltaY = this.currentY - this.startY

    if (Math.abs(deltaY) > Math.abs(deltaX)) {
      e.preventDefault()
      if (deltaY > 0) {
        this.infosheetTarget.style.transform = `translateY(${deltaY}px)`
      }
    }
  }

  handleTouchEnd() {
    if (!this.isSwiping) return
    const swipeDistance = this.startY + this.currentY
    if (swipeDistance > SWIPE_TRESHOLD) {
      this.infosheetTarget.style.transform = ``
      this.closeInfosheet()
    } else if (swipeDistance < 10) {
      // Reset positie als swipe te kort is
      this.infosheetTarget.style.transform = `translateY(0)`
    } else {
      // Reset positie als swipe te kort is
      this.infosheetTarget.style.transform = `translateY(0)`
    }
  }

  openInfosheet(e) {
    if (this.hasInfosheetTarget) {
      e.preventDefault()
      scrollPositionForDialog = window.scrollY
      this.infosheetTurboframeTarget.setAttribute('src', e.params.action)
      this.infosheetTarget.showModal()
      document.body.style.top = `-${scrollPositionForDialog}px`
      document.body.style.position = 'fixed'
      document.body.style.overflow = 'hidden'
      this.infosheetTarget.addEventListener('click', (event) => {
        if (event.target === event.currentTarget) {
          event.stopPropagation()
          this.closeInfosheet()
        }
      })
    }
  }

  closeInfosheet() {
    if (this.hasInfosheetTarget) {
      if (this.infosheetTarget.open) {
        this.infosheetTarget.classList.add('closing')
        console.log('closeInfosheet')
        setTimeout(() => (this.infosheetTurboframeTarget.innerHTML = ''), 400)
        setTimeout(() => {
          this.infosheetTarget.close()
          document.body.style.position = ''
          document.body.style.top = ''
          window.scrollTo({ top: scrollPositionForDialog, left: 0, behavior: 'instant' })
          this.infosheetTarget.classList.remove('closing')
        }, 500)
      }
    }
    document.body.style.overflow = ''
    this.infosheetTarget.removeEventListener('click', (event) => {
      if (event.target !== this.infosheetTarget.querySelector('.content')) {
        this.closeInfosheet()
      }
    })
  }
}

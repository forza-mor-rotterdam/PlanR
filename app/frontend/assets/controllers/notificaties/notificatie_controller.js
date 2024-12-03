import { Controller } from '@hotwired/stimulus'

const SWIPE_TRESHOLD = 100
const MAX_CHARACTERS = 200
export default class extends Controller {
  static targets = ['content']

  static values = {
    duration: String,
  }

  connect() {
    console.log(`Connect: ${this.identifier}`)
    let contentString = null
    let truncatedString = null
    if (this.hasContentTarget) {
      if (!this.contentTarget.parentNode.querySelector('.message--truncated')) {
        contentString = this.contentTarget.innerText
        if (contentString.length > MAX_CHARACTERS) {
          truncatedString = `${contentString.slice(
            0,
            MAX_CHARACTERS - 13
          )}... <a href="" data-action="notificatie#readMore">Lees meer</a>`

          this.element.classList.add('show-truncated')
          const paragraph = document.createElement('p')
          paragraph.innerHTML = truncatedString
          paragraph.classList.add('message--truncated')
          this.contentTarget.classList.add('message--initial')
          this.contentTarget.parentNode.appendChild(paragraph)
          this.contentTarget.style.height = `${paragraph.clientHeight}px`
        }
      }
    }
    if (this.hasDurationValue) {
      setTimeout(() => {
        this.hideNotification()
      }, Number(this.durationValue))
    }

    if ('ontouchstart' in window) {
      this.element.addEventListener('touchstart', (event) => {
        event.preventDefault()
        self.initialTouchX = event.touches[0].clientX
        const currentWidth = this.element.clientWidth
        this.element.style.width = `${currentWidth}px`
      })

      this.element.addEventListener('touchmove', (event) => {
        event.preventDefault()
        self.deltaX = self.initialTouchX - event.changedTouches[0].clientX
        this.element.style.marginLeft = `-${self.deltaX}px`
      })

      this.element.addEventListener('touchend', (event) => {
        event.preventDefault()
        self.finalTouchX = event.changedTouches[0].clientX
        if (self.deltaX < SWIPE_TRESHOLD) {
          this.element.style.marginLeft = 0
        }
        if (event.target.classList.contains('btn-close--small')) {
          this.hideNotification()
        } else if (event.target.nodeName.toLowerCase() === 'a') {
          if (event.target.getAttribute('data-action')) {
            this[`${event.target.getAttribute('data-action').split('#')[1]}`]()
          }
        } else {
          this.handleSwipe(self.initialTouchX, self.finalTouchX)
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
  initByManager(managerController, index, referenceOffsetHeight) {
    this.managerController = managerController
    this.index = index
    this.referenceOffsetHeight = referenceOffsetHeight
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
    this.element.classList.remove('show-truncated')
    this.contentTarget.style.height = `${this.contentTarget.scrollHeight}px`
    setTimeout(() => {
      this.dispatchRedraw, 500
    })
  }

  dispatchRedraw() {
    this.element.dispatchEvent(
      new CustomEvent('notificatieVerwijderd', {
        bubbles: true,
      })
    )
  }
  async notificatieSeen(notificatieUrl) {
    const url = notificatieUrl
    try {
      const response = await fetch(`${url}`)
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`)
      }
      return response
    } catch (error) {
      console.error('Error fetching address details:', error.message)
    }
  }
  hideNotification() {
    console.log(this.identifier)
    if (this.element.dataset.verwijderUrl) {
      const profiel_notificatie_lijst = document.querySelector(
        "[data-controller='profiel-notificatie-lijst']"
      )
      if (profiel_notificatie_lijst) {
        profiel_notificatie_lijst.controller.markNotificatieAsWatched(`profiel_${this.element.id}`)
      }
      this.notificatieSeen(this.element.dataset.verwijderUrl)
      this.removeNotification()
    }
  }
  removeNotification() {
    const notificatie = this.element
    notificatie.classList.add('hide')

    notificatie.addEventListener('transitionend', () => {
      this.dispatchRedraw()
      notificatie.remove()
    })
  }

  handleSwipe() {
    let self = this
    this.element.closest('.container__notification').classList.remove('collapsed')
    this.element.closest('.container__notification').classList.add('expanded')
    if (self.initialTouchX - self.finalTouchX > SWIPE_TRESHOLD) {
      this.hideNotification()
    }
  }
}

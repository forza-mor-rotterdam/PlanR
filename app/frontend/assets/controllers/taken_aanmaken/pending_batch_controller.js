import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  connect() {
    this.batchUuid = this.element.dataset.batchUuid
    this.countdown = Number.parseInt(this.element.dataset.countdown || '0', 10)
    this.remaining = Number.isFinite(this.countdown) ? this.countdown : 0
    this.verstuurUrl = this.element.dataset.verstuurUrl
    const csrfInput = this.element.querySelector('input[name="csrfmiddlewaretoken"]')
    this.csrfToken = csrfInput?.value || this.element.dataset.csrfToken || this.getCsrfToken()
    this.isPaused = false
    this.isFinalized = false
    this.intervalId = null

    this.taken = Array.from(this.element.querySelectorAll('[data-taak-uuid]')).map((item) => ({
      uuid: item.dataset.taakUuid,
      titel: item.textContent?.trim() || 'Taak',
      annuleerUrl: item.dataset.annuleerUrl,
      pauseUrl: item.dataset.pauseUrl,
      resumeUrl: item.dataset.resumeUrl,
    }))

    this.toastContainer = document.getElementById('toast_lijst')
    if (!this.toastContainer || !this.batchUuid || !this.taken.length || !this.verstuurUrl) {
      return
    }

    const existingToast = this.toastContainer.querySelector(
      `[data-pending-batch-toast="${this.batchUuid}"]`
    )
    if (existingToast) {
      this.element.style.display = 'none'
      return
    }

    this.renderToast()
    this.startCountdown()
    this.element.style.display = 'none'
  }

  disconnect() {
    // The source payload lives inside the modal, but the toast is appended outside it.
    // When the modal closes this controller disconnects; do not stop the active toast here.
  }

  renderToast() {
    const rawTitel = this.taken[0]?.titel || 'Taak'
    const taakTitel = rawTitel.length > 10 ? `${rawTitel.slice(0, 10)}...` : rawTitel
    const toast = document.createElement('div')
    toast.className = 'notification pending-batch-toast'
    toast.dataset.pendingBatchToast = this.batchUuid
    toast.setAttribute('data-controller', 'notificaties--toast-item')
    toast.setAttribute('data-notificaties--manager-target', 'toastItem')

    toast.innerHTML = `
      <div class="container__icon" aria-hidden="true">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path fill-rule="evenodd" clip-rule="evenodd" d="M21.9 12C21.9 6.5 17.5 2.1 12 2.1C6.5 2.1 2.1 6.5 2.1 12C2.1 17.5 6.5 21.9 12 21.9C17.5 21.9 21.9 17.5 21.9 12ZM0 12C0 5.4 5.4 0 12 0C18.6 0 24 5.4 24 12C24 18.6 18.6 24 12 24C5.4 24 0 18.6 0 12ZM16.6 7.1L18 8.5L10.5 16L7.10001 12.6L8.50001 11.2L10.5 13.2L16.6 7.1Z" fill="#00811F"/>
        </svg>
      </div>
      <div class="container__content">
        <div class="container__message">
          <p data-countdown-message>
            <span class="task-name">Taak <strong>${taakTitel}</strong></span>
            <span class="task-suffix">is aangemaakt</span>
          </p>
          <button type="button" class="btn btn-textlink" data-undo-button>Ongedaan maken</button>
        </div>
      </div>
      <button
        type="button"
        class="btn-close--small"
        aria-label="Sluit"
        data-close-button
      >
        <span aria-hidden="true">×</span>
      </button>
    `

    this.toastContainer.appendChild(toast)
    this.toastElement = toast
    this.undoButton = this.toastElement.querySelector('[data-undo-button]')
    this.closeButton = this.toastElement.querySelector('[data-close-button]')
    this.countdownMessage = this.toastElement.querySelector('[data-countdown-message]')

    this.undoClickHandler = () => this.annuleerAlles()
    this.closeClickHandler = (event) => this.verwerkEnSluit(event)
    this.mouseEnterHandler = () => this.pauseBatch()
    this.mouseLeaveHandler = () => this.resumeBatch()

    this.undoButton?.addEventListener('click', this.undoClickHandler)
    this.closeButton?.addEventListener('click', this.closeClickHandler)
    this.toastElement.addEventListener('mouseenter', this.mouseEnterHandler)
    this.toastElement.addEventListener('mouseleave', this.mouseLeaveHandler)
  }

  removeHoverHandlers() {
    this.undoButton?.removeEventListener('click', this.undoClickHandler)
    this.closeButton?.removeEventListener('click', this.closeClickHandler)
    this.toastElement?.removeEventListener('mouseenter', this.mouseEnterHandler)
    this.toastElement?.removeEventListener('mouseleave', this.mouseLeaveHandler)
  }

  verwerkEnSluit(event) {
    event?.preventDefault()
    event?.stopPropagation()
    this.verstuurNu()
  }

  startCountdown() {
    this.updateCountdownUI()
    this.intervalId = window.setInterval(() => {
      if (this.isPaused || this.isFinalized) return
      if (this.remaining <= 0) {
        this.verstuurNu()
        return
      }
      this.remaining -= 1
      this.updateCountdownUI()
    }, 1000)
  }

  stopCountdown() {
    if (this.intervalId) {
      window.clearInterval(this.intervalId)
      this.intervalId = null
    }
  }

  disableActions() {
    if (this.undoButton) this.undoButton.disabled = true
  }

  disableUndo() {
    if (this.undoButton) {
      this.undoButton.disabled = true
      this.undoButton.textContent = 'Ongedaan maken (verlopen)'
    }
    if (this.countdownMessage) {
      this.countdownMessage.textContent = 'Taken worden nu verwerkt.'
    }
  }

  updateCountdownUI() {
    if (this.undoButton) {
      this.undoButton.textContent = 'Ongedaan maken'
    }
  }

  async pauseBatch() {
    if (this.isPaused || this.isFinalized) return
    this.isPaused = true
    await Promise.all(
      this.taken
        .filter((taak) => Boolean(taak.pauseUrl))
        .map((taak) => this.request(taak.pauseUrl, 'PATCH').catch(() => null))
    )
  }

  async resumeBatch() {
    if (!this.isPaused || this.isFinalized) return
    this.isPaused = false
    await Promise.all(
      this.taken
        .filter((taak) => Boolean(taak.resumeUrl))
        .map((taak) => this.request(taak.resumeUrl, 'PATCH').catch(() => null))
    )
  }

  async verstuurNu() {
    if (this.isFinalized) return
    this.isFinalized = true
    this.disableActions()
    this.stopCountdown()

    try {
      await this.request(this.verstuurUrl, 'POST')
      this.hideToast()
    } catch (error) {
      console.error('[pending-batch] send failed', {
        batchUuid: this.batchUuid,
        method: 'POST',
        url: this.verstuurUrl,
        error: error?.message || error,
      })
      this.isFinalized = false
      this.updateCountdownUI()
      if (this.undoButton) this.undoButton.disabled = false
    }
  }

  async annuleerAlles() {
    if (this.isFinalized) return
    this.isFinalized = true
    this.disableActions()
    this.stopCountdown()

    try {
      await Promise.all(
        this.taken
          .filter((taak) => Boolean(taak.annuleerUrl))
          .map((taak) => this.request(taak.annuleerUrl, 'POST'))
      )
      this.hideToast()
    } catch (error) {
      console.error('[pending-batch] cancel failed', {
        batchUuid: this.batchUuid,
        method: 'POST',
        urls: annuleerUrls,
        error: error?.message || error,
      })
      this.isFinalized = false
      this.updateCountdownUI()
      if (this.undoButton) this.undoButton.disabled = false
    }
  }

  hideToast() {
    this.stopCountdown()
    this.removeHoverHandlers()
    this.toastElement?.classList.add('hide')
    window.setTimeout(() => {
      this.toastElement?.remove()
    }, 400)
  }

  async request(url, method) {
    const response = await fetch(url, {
      method,
      headers: {
        'X-CSRFToken': this.csrfToken,
        'X-Requested-With': 'XMLHttpRequest',
      },
      credentials: 'same-origin',
    })

    if (!response.ok) {
      throw new Error(`Request failed for ${url}`)
    }

    const contentType = response.headers.get('content-type') || ''
    if (contentType.includes('application/json')) {
      return response.json()
    }
    return response.text()
  }

  getCsrfToken() {
    const cookie = document.cookie
      .split('; ')
      .find((row) => row.startsWith('__Host-csrftoken=') || row.startsWith('csrftoken='))
    return cookie ? decodeURIComponent(cookie.split('=')[1]) : ''
  }
}

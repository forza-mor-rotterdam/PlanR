import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  connect() {
    this.batchUuid = this.element.dataset.batchUuid
    this.countdown = Number.parseInt(this.element.dataset.countdown || '0', 10)
    if (!Number.isFinite(this.remaining)) {
      this.remaining = Number.isFinite(this.countdown) ? this.countdown : 0
    }
    this.verstuurUrl = this.element.dataset.verstuurUrl
    const csrfInput = this.element.querySelector('input[name="csrfmiddlewaretoken"]')
    this.csrfToken = csrfInput?.value || this.element.dataset.csrfToken || this.getCsrfToken()
    if (typeof this.isPaused !== 'boolean') this.isPaused = false
    if (typeof this.isFinalized !== 'boolean') this.isFinalized = false
    if (!Number.isInteger(this.intervalId)) this.intervalId = null

    this.taken = Array.from(this.element.querySelectorAll('[data-taak-uuid]')).map((item) => ({
      uuid: item.dataset.taakUuid,
      titel: item.textContent?.trim() || 'Taak',
      annuleerUrl: item.dataset.annuleerUrl,
      pauseUrl: item.dataset.pauseUrl,
      resumeUrl: item.dataset.resumeUrl,
    }))

    this.toastContainer = document.getElementById('toast_lijst') || this.element.parentElement
    if (!this.batchUuid || !this.verstuurUrl) {
      return
    }

    const existingToast = this.toastContainer.querySelector(
      `[data-pending-batch-toast="${this.batchUuid}"]`
    )
    if (existingToast && existingToast !== this.element) {
      this.element.remove()
      return
    }

    this.element.dataset.pendingBatchToast = this.batchUuid
    if (this.taken.length) {
      const rawTitel = this.taken[0]?.titel || 'Taak'
      const taakTitel = rawTitel.length > 10 ? `${rawTitel.slice(0, 10)}...` : rawTitel
      const titleElement = this.element.querySelector('[data-task-title]')
      if (titleElement) titleElement.textContent = taakTitel
    }

    if (this.toastContainer && !this.toastContainer.contains(this.element)) {
      this.toastContainer.appendChild(this.element)
    }

    this.toastElement = this.element
    this.undoButton = this.toastElement.querySelector('[data-undo-button]')
    this.closeButton = this.toastElement.querySelector('[data-close-button]')
    this.countdownMessage = this.toastElement.querySelector('[data-countdown-message]')

    this.removeHoverHandlers()

    this.undoClickHandler = () => this.annuleerAlles()
    this.closeClickHandler = (event) => this.verwerkEnSluit(event)
    this.mouseEnterHandler = () => this.pauseBatch()
    this.mouseLeaveHandler = () => this.resumeBatch()

    this.undoButton?.addEventListener('click', this.undoClickHandler)
    this.closeButton?.addEventListener('click', this.closeClickHandler)
    this.toastElement.addEventListener('mouseenter', this.mouseEnterHandler)
    this.toastElement.addEventListener('mouseleave', this.mouseLeaveHandler)

    if (!this.intervalId) {
      this.startCountdown()
    }
  }

  disconnect() {
    // This element may briefly disconnect/reconnect when moved into #toast_lijst.
    // Keep timer and handlers intact unless toast is explicitly hidden.
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
      const result = await this.request(this.verstuurUrl, 'POST')
      if (result.status === 200) {
        console.info('[pending-batch] verstuur acknowledged (200)', {
          batchUuid: this.batchUuid,
          url: this.verstuurUrl,
          status: result.status,
        })
      }
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
      const results = await Promise.all(
        this.taken
          .filter((taak) => Boolean(taak.annuleerUrl))
          .map((taak) => this.request(taak.annuleerUrl, 'POST'))
      )
      const successCount = results.filter((result) => result.status === 200).length
      if (successCount > 0) {
        console.info('[pending-batch] annuleer acknowledged (200)', {
          batchUuid: this.batchUuid,
          successfulCancels: successCount,
          requestedCancels: results.length,
        })
      }
      this.hideToast()
    } catch (error) {
      console.error('[pending-batch] cancel failed', {
        batchUuid: this.batchUuid,
        method: 'POST',
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
    const status = response.status
    if (contentType.includes('application/json')) {
      return {
        status,
        body: await response.json(),
      }
    }
    return {
      status,
      body: await response.text(),
    }
  }

  getCsrfToken() {
    const cookie = document.cookie
      .split('; ')
      .find((row) => row.startsWith('__Host-csrftoken=') || row.startsWith('csrftoken='))
    return cookie ? decodeURIComponent(cookie.split('=')[1]) : ''
  }
}

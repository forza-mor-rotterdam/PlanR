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

    this.placeholderContainer = document.querySelector('[data-testid="detailTaken"] .container__taken')
    this.placeholderSection = this.placeholderContainer?.closest('.section--separated')
    this.ensurePlaceholders()
    this.streamRenderHandler = (event) => {
      const streamTarget = event.target?.getAttribute?.('target')
      if (streamTarget === 'melding_detail_taken') {
        this.removePlaceholders()
      }
    }
    document.addEventListener('turbo:before-stream-render', this.streamRenderHandler)

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
    document.removeEventListener('turbo:before-stream-render', this.streamRenderHandler)
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
        this.refreshTakenBlock()
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
      this.removePlaceholders()
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

  ensurePlaceholders() {
    if (!this.placeholderContainer || !this.batchUuid) {
      return
    }

    const headerRow = this.placeholderContainer.querySelector('.taken--header')
    const hasOptionsColumn = Array.from(
      this.placeholderContainer.querySelectorAll('.taken--header > div')
    ).some((node) => node.textContent?.trim() === 'Opties')

    this.taken.forEach((taak) => {
      const existing = this.placeholderContainer.querySelector(
        `[data-pending-taak-placeholder="${taak.uuid}"]`
      )
      if (existing) {
        return
      }

      const row = document.createElement('details')
      row.className = 'container__taak container__taak--placeholder'
      row.dataset.pendingBatchUuid = this.batchUuid
      row.dataset.pendingTaakPlaceholder = taak.uuid
      row.dataset.pendingTaakTitel = (taak.titel || '').toLowerCase().trim()

      const summary = document.createElement('summary')
      if (!hasOptionsColumn) {
        summary.classList.add('hide-last-column')
      }

      summary.innerHTML = `
        <div class="description">
          <div class="wrapper">
            <p style="color: black;">${this.escapeHtml(taak.titel || 'Taak')}</p>
          </div>
          <small></small>
        </div>
        <div><span class="help-text">${this.formatDateTime(new Date())}</span></div>
        <div><span class="help-text"></span></div>
        <div><span class="help-text"></span></div>
        <div><span class="help-text"></span></div>
        ${
          hasOptionsColumn
            ? `<div style="display: flex; align-items: center; justify-content: flex-end;">
                <span class="pending-task-placeholder__spinner" aria-hidden="true">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M22.125 12C22.125 14.6853 21.0583 17.2607 19.1595 19.1595C17.2607 21.0583 14.6853 22.125 12 22.125C9.31468 22.125 6.73935 21.0583 4.84054 19.1595C2.94174 17.2607 1.875 14.6853 1.875 12C1.875 8.01375 4.19344 4.37437 7.78125 2.72812C7.91606 2.6624 8.06266 2.62429 8.21242 2.61605C8.36217 2.60781 8.51206 2.62959 8.65328 2.68012C8.79449 2.73065 8.92417 2.80891 9.0347 2.91029C9.14523 3.01167 9.23437 3.13413 9.29688 3.27047C9.35939 3.4068 9.39401 3.55426 9.3987 3.70417C9.40339 3.85408 9.37806 4.00341 9.32419 4.14339C9.27033 4.28336 9.18902 4.41116 9.08504 4.51925C8.98107 4.62734 8.85653 4.71355 8.71875 4.77281C5.92875 6.05344 4.125 8.89031 4.125 12C4.125 14.0886 4.95468 16.0916 6.43153 17.5685C7.90838 19.0453 9.91142 19.875 12 19.875C14.0886 19.875 16.0916 19.0453 17.5685 17.5685C19.0453 16.0916 19.875 14.0886 19.875 12C19.875 8.89031 18.0713 6.05344 15.2812 4.77281C15.1435 4.71355 15.0189 4.62734 14.915 4.51925C14.811 4.41116 14.7297 4.28336 14.6758 4.14339C14.6219 4.00341 14.5966 3.85408 14.6013 3.70417C14.606 3.55426 14.6406 3.4068 14.7031 3.27047C14.7656 3.13413 14.8548 3.01167 14.9653 2.91029C15.0758 2.80891 15.2055 2.73065 15.3467 2.68012C15.4879 2.62959 15.6378 2.60781 15.7876 2.61605C15.9373 2.62429 16.0839 2.6624 16.2188 2.72812C19.8066 4.37437 22.125 8.01375 22.125 12Z" fill="black"/>
                  </svg>
                </span>
              </div>`
            : ''
        }
      `

      row.appendChild(summary)
      if (headerRow) {
        headerRow.insertAdjacentElement('afterend', row)
      } else {
        this.placeholderContainer.insertAdjacentElement('afterbegin', row)
      }
    })

    this.placeholderSection?.classList.add('has-taken')
  }

  removePlaceholders() {
    if (!this.batchUuid) {
      return
    }

    document
      .querySelectorAll(`[data-pending-batch-uuid="${this.batchUuid}"]`)
      .forEach((placeholder) => placeholder.remove())

    if (!document.querySelector('[data-pending-batch-uuid]')) {
      this.placeholderSection?.classList.remove('has-taken')
    }
  }

  formatDateTime(date) {
    const pad = (n) => `${n}`.padStart(2, '0')
    return `${pad(date.getDate())}-${pad(date.getMonth() + 1)}-${date.getFullYear()}, ${pad(date.getHours())}:${pad(date.getMinutes())}`
  }

  escapeHtml(value) {
    return `${value}`
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#39;')
  }

  async refreshTakenBlock() {
    window.Turbo?.visit(window.location.href)
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

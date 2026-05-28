import { Controller } from '@hotwired/stimulus'


export default class extends Controller {
  connect() {
    this.maxPauseMs = 60 * 1000
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
    if (!Number.isInteger(this.pauseTimeoutId)) this.pauseTimeoutId = null
    if (!Array.isArray(this.additionalToastEntries)) this.additionalToastEntries = []

    this.taken = Array.from(this.element.querySelectorAll('[data-taak-uuid]')).map((item) => ({
      uuid: item.dataset.taakUuid,
      titel: item.textContent?.trim() || 'Taak',
      annuleerUrl: item.dataset.annuleerUrl,
      pauseUrl: item.dataset.pauseUrl,
      resumeUrl: item.dataset.resumeUrl,
    }))
    this.takenByUuid = new Map(this.taken.map((taak) => [taak.uuid, taak]))
    this.primaryTaakUuid = this.taken[0]?.uuid || null

    this.placeholderContainer = document.querySelector('[data-testid="detailTaken"] .container__taken')
    this.placeholderSection = this.placeholderContainer?.closest('.section--separated')
    this.realTaskCountAtConnect = this.getRealTaskCount(document)
    this.ensurePlaceholders()

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
    this.element.dataset.pendingBatchGroup = this.batchUuid
    if (this.primaryTaakUuid) {
      this.element.dataset.pendingBatchTaskUuid = this.primaryTaakUuid
      this.element.dataset.pendingBatchAnnuleerUrl =
        this.takenByUuid.get(this.primaryTaakUuid)?.annuleerUrl || ''
    }
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
    this.ensureToastItemController(this.toastElement)
    this.undoButton = this.toastElement.querySelector('[data-undo-button]')
    this.closeButton = this.toastElement.querySelector('[data-close-button]')

    this.removeHoverHandlers()

    this.undoClickHandler = () =>
      this.annuleerTaak(
        this.primaryTaakUuid,
        this.element.dataset.pendingBatchAnnuleerUrl || null
      )
    this.closeClickHandler = (event) => this.verwerkEnSluit(event)
    this.mouseEnterHandler = () => this.pauseBatch()
    this.mouseLeaveHandler = () => this.resumeBatch()

    this.undoButton?.addEventListener('click', this.undoClickHandler)
    this.closeButton?.addEventListener('click', this.closeClickHandler)
    this.toastElement.addEventListener('mouseenter', this.mouseEnterHandler)
    this.toastElement.addEventListener('mouseleave', this.mouseLeaveHandler)

    this.bindAdditionalTaskToasts()
    this.updatePendingToastStackState()

    if (!this.intervalId) {
      this.startCountdown()
    }
  }

  disconnect() {
    // This element may briefly disconnect/reconnect when moved into #toast_lijst.
    // Keep timer and handlers intact unless toast is explicitly hidden.
    this.clearPauseTimeout()
  }

  removeHoverHandlers() {
    this.undoButton?.removeEventListener('click', this.undoClickHandler)
    this.closeButton?.removeEventListener('click', this.closeClickHandler)
    this.toastElement?.removeEventListener('mouseenter', this.mouseEnterHandler)
    this.toastElement?.removeEventListener('mouseleave', this.mouseLeaveHandler)

    this.additionalToastEntries.forEach((entry) => {
      entry.undoButton?.removeEventListener('click', entry.undoHandler)
      entry.closeButton?.removeEventListener('click', entry.closeHandler)
      entry.toast?.removeEventListener('mouseenter', entry.mouseEnterHandler)
      entry.toast?.removeEventListener('mouseleave', entry.mouseLeaveHandler)
    })
  }

  verwerkEnSluit(event) {
    event?.preventDefault()
    event?.stopPropagation()
    this.verstuurNu()
  }

  startCountdown() {
    this.intervalId = window.setInterval(() => {
      if (this.isPaused || this.isFinalized) return
      if (this.remaining <= 0) {
        this.verstuurNu()
        return
      }
      this.remaining -= 1
    }, 1000)
  }

  stopCountdown() {
    if (this.intervalId) {
      window.clearInterval(this.intervalId)
      this.intervalId = null
    }
  }

  startPauseTimeout() {
    this.clearPauseTimeout()

    this.pauseTimeoutId = window.setTimeout(() => {
      if (this.isFinalized || !this.isPaused) return
      this.isPaused = false
      this.verstuurNu()
    }, this.maxPauseMs)
  }

  clearPauseTimeout() {
    if (this.pauseTimeoutId) {
      window.clearTimeout(this.pauseTimeoutId)
      this.pauseTimeoutId = null
    }
  }

  disableActions() {
    this.getBatchUndoButtons().forEach((button) => {
      button.disabled = true
    })
  }

  async pauseBatch() {
    if (this.isPaused || this.isFinalized) return
    this.isPaused = true
    this.startPauseTimeout()
    const activeTaken = this.getActiveTaken()
    await Promise.all(
      activeTaken
        .filter((taak) => Boolean(taak.pauseUrl))
        .map((taak) => this.request(taak.pauseUrl, 'PATCH').catch(() => null))
    )
  }

  async resumeBatch() {
    if (!this.isPaused || this.isFinalized) return
    this.isPaused = false
    this.clearPauseTimeout()
    const activeTaken = this.getActiveTaken()
    await Promise.all(
      activeTaken
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
        await Promise.race([
          this.refreshTakenBlock(),
          this.sleep(4000),
        ])
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
      this.getBatchUndoButtons().forEach((button) => {
        button.disabled = false
      })
    }
  }

  async annuleerTaak(taakUuid, annuleerUrl = null) {
    if (this.isFinalized || !taakUuid) return

    const taak = this.takenByUuid.get(taakUuid)
    const cancelUrl = annuleerUrl || taak?.annuleerUrl || null
    if (!cancelUrl) {
      console.error('[pending-batch] cancel skipped - missing annuleerUrl', {
        batchUuid: this.batchUuid,
        taakUuid,
      })
      return
    }

    const clickedUndoButtons = Array.from(
      this.toastContainer?.querySelectorAll(
        `[data-pending-batch-task-uuid="${taakUuid}"] [data-undo-button]`
      ) || []
    )
    clickedUndoButtons.forEach((button) => {
      button.disabled = true
    })

    try {
      const result = await this.request(cancelUrl, 'POST')
      const geannuleerdeUuids = result.body?.geannuleerde_uuids || [taakUuid]
      const allesGeannuleerd = Boolean(result.body?.alles_geannuleerd)

      console.info('[pending-batch] annuleer acknowledged (200)', {
        batchUuid: this.batchUuid,
        requestedCancel: taakUuid,
        cancelled: geannuleerdeUuids,
      })

      this.removePlaceholdersForUuids(geannuleerdeUuids)
      this.removeToastsForUuids(geannuleerdeUuids)

      if (allesGeannuleerd || this.getRemainingTaskUuids().length === 0) {
        this.hideToast()
      }
    } catch (error) {
      console.error('[pending-batch] cancel failed', {
        batchUuid: this.batchUuid,
        method: 'POST',
        taakUuid,
        error: error?.message || error,
      })
      clickedUndoButtons.forEach((button) => {
        button.disabled = false
      })
    }
  }

  hideToast() {
    this.stopCountdown()
    this.clearPauseTimeout()
    this.removeHoverHandlers()

    this.additionalToastEntries.forEach((entry) => {
      this.hideToastElement(entry.toast)
    })
    this.hideToastElement(this.toastElement)

    window.setTimeout(() => {
      this.clearAdditionalTaskToasts()
      this.toastElement?.remove()
      this.updatePendingToastStackState()
    }, 550)
  }

  bindAdditionalTaskToasts() {
    if (!this.toastContainer || this.taken.length <= 1) return

    this.clearAdditionalTaskToasts()

    Array.from(
      this.toastContainer.querySelectorAll(
        `[data-pending-batch-group="${this.batchUuid}"][data-pending-batch-ghost]`
      )
    ).forEach((toast) => {
      const taakUuid = toast.dataset.pendingBatchTaskUuid
      if (!taakUuid) {
        return
      }

      const undoButton = toast.querySelector('[data-undo-button]')
      const closeButton = toast.querySelector('[data-close-button]')
      const undoHandler = () =>
        this.annuleerTaak(taakUuid, toast.dataset.pendingBatchAnnuleerUrl || null)
      const closeHandler = (event) => this.verwerkEnSluit(event)
      const mouseEnterHandler = () => this.pauseBatch()
      const mouseLeaveHandler = () => this.resumeBatch()

      undoButton?.addEventListener('click', undoHandler)
      closeButton?.addEventListener('click', closeHandler)
      toast.addEventListener('mouseenter', mouseEnterHandler)
      toast.addEventListener('mouseleave', mouseLeaveHandler)

      this.additionalToastEntries.push({
        taakUuid,
        toast,
        undoButton,
        closeButton,
        undoHandler,
        closeHandler,
        mouseEnterHandler,
        mouseLeaveHandler,
      })
    })
  }

  clearAdditionalTaskToasts() {
    if (!this.toastContainer) return
    this.additionalToastEntries.forEach((entry) => {
      entry.undoButton?.removeEventListener('click', entry.undoHandler)
      entry.closeButton?.removeEventListener('click', entry.closeHandler)
      entry.toast?.removeEventListener('mouseenter', entry.mouseEnterHandler)
      entry.toast?.removeEventListener('mouseleave', entry.mouseLeaveHandler)
      entry.toast?.remove()
    })
    this.additionalToastEntries = []
  }

  getBatchUndoButtons() {
    if (!this.toastContainer) return []
    return Array.from(
      this.toastContainer.querySelectorAll(
        `[data-pending-batch-group="${this.batchUuid}"] [data-undo-button]`
      )
    )
  }

  getRemainingTaskUuids() {
    const uuids = this.additionalToastEntries.map((entry) => entry.taakUuid)
    if (this.primaryTaakUuid) uuids.unshift(this.primaryTaakUuid)
    return uuids
  }

  getActiveTaken() {
    return Array.from(this.takenByUuid.values())
  }

  removePlaceholdersForUuids(uuids) {
    uuids.forEach((uuid) => {
      document
        .querySelectorAll(`[data-pending-taak-placeholder="${uuid}"]`)
        .forEach((placeholder) => placeholder.remove())
    })

    if (!document.querySelector('[data-pending-batch-uuid]')) {
      this.placeholderSection?.classList.remove('has-taken')
    }
  }

  removeToastsForUuids(uuids) {
    this.taken = this.taken.filter((taak) => !uuids.includes(taak.uuid))
    uuids.forEach((uuid) => {
      this.takenByUuid.delete(uuid)
    })

    this.additionalToastEntries = this.additionalToastEntries.filter((entry) => {
      if (!uuids.includes(entry.taakUuid)) {
        return true
      }

      entry.undoButton?.removeEventListener('click', entry.undoHandler)
      entry.closeButton?.removeEventListener('click', entry.closeHandler)
      entry.toast?.removeEventListener('mouseenter', entry.mouseEnterHandler)
      entry.toast?.removeEventListener('mouseleave', entry.mouseLeaveHandler)
      entry.toast?.remove()
      return false
    })

    if (this.primaryTaakUuid && uuids.includes(this.primaryTaakUuid)) {
      const replacement = this.additionalToastEntries.shift()
      if (replacement) {
        this.primaryTaakUuid = replacement.taakUuid
        this.toastElement.dataset.pendingBatchTaskUuid = replacement.taakUuid
        this.toastElement.dataset.pendingBatchAnnuleerUrl =
          this.takenByUuid.get(replacement.taakUuid)?.annuleerUrl || ''
        const replacementTitle = this.takenByUuid.get(replacement.taakUuid)?.titel || 'Taak'
        const titleElement = this.toastElement?.querySelector('[data-task-title]')
        if (titleElement) {
          titleElement.textContent =
            replacementTitle.length > 10
              ? `${replacementTitle.slice(0, 10)}...`
              : replacementTitle
        }

        replacement.undoButton?.removeEventListener('click', replacement.undoHandler)
        replacement.closeButton?.removeEventListener('click', replacement.closeHandler)
        replacement.toast?.removeEventListener('mouseenter', replacement.mouseEnterHandler)
        replacement.toast?.removeEventListener('mouseleave', replacement.mouseLeaveHandler)
        replacement.toast?.remove()
      } else {
        this.primaryTaakUuid = null
        delete this.toastElement.dataset.pendingBatchTaskUuid
        delete this.toastElement.dataset.pendingBatchAnnuleerUrl
      }
    }

    this.updatePendingToastStackState()
  }

  updatePendingToastStackState() {
    if (!this.toastContainer) return

    const hasPendingToasts = this.toastContainer.querySelectorAll('.pending-batch-toast').length > 0
    this.toastContainer.classList.toggle('has-pending-batch-toasts', hasPendingToasts)
  }

  ensureToastItemController(element) {
    if (!element) return

    const controllerAttr = element.getAttribute('data-controller') || ''
    const controllerNames = controllerAttr
      .split(/\s+/)
      .map((name) => name.trim())
      .filter(Boolean)

    if (!controllerNames.includes('notificaties--toast-item')) {
      controllerNames.push('notificaties--toast-item')
      element.setAttribute('data-controller', controllerNames.join(' '))
    }
  }

  hideToastElement(element) {
    if (!element) return

    const toastController = this.application.getControllerForElementAndIdentifier(
      element,
      'notificaties--toast-item'
    )
    if (toastController && typeof toastController.hideNotification === 'function') {
      toastController.hideNotification()
      return
    }

    if (element.classList.contains('notification')) {
      element.classList.add('hide')
      window.setTimeout(() => {
        element.remove()
      }, 500)
    }
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
    const pollIntervalMs = 500
    const maxAttempts = 60

    for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
      try {
        const refreshUrl = new URL(window.location.href)
        refreshUrl.searchParams.set('_taken_refresh', `${Date.now()}`)

        const response = await fetch(refreshUrl.toString(), {
          method: 'GET',
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
          },
          credentials: 'same-origin',
          cache: 'no-store',
        })

        if (!response.ok) {
          throw new Error('Failed to refresh taken block')
        }

        const html = await response.text()
        const parser = new DOMParser()
        const nextDocument = parser.parseFromString(html, 'text/html')
        const nextTakenBlock = nextDocument.querySelector('#melding_detail_taken')
        const currentTakenBlock = document.querySelector('#melding_detail_taken')

        if (!nextTakenBlock || !currentTakenBlock) {
          throw new Error('Taken block not found in refresh response')
        }

        const nextRealTaskCount = this.getRealTaskCount(nextDocument)

        if (nextRealTaskCount > this.realTaskCountAtConnect) {
          currentTakenBlock.replaceWith(nextTakenBlock)
          this.realTaskCountAtConnect = nextRealTaskCount
          return
        }
      } catch (error) {
        console.error('[pending-batch] refresh taken block failed', {
          batchUuid: this.batchUuid,
          error: error?.message || error,
        })
      }

      if (attempt < maxAttempts - 1) {
        await this.sleep(pollIntervalMs)
      }
    }
  }

  getRealTaskCount(root) {
    return root.querySelectorAll('[data-testid="detailTaken"] .container__taken .container__taak:not(.container__taak--placeholder)').length
  }

  sleep(ms) {
    return new Promise((resolve) => {
      window.setTimeout(resolve, ms)
    })
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

import { Controller } from '@hotwired/stimulus'
import { renderStreamMessage } from '@hotwired/turbo'

export default class extends Controller {
  static targets = [
    'modal',
    'modalSluiten',
    'template',
    'dialog',
    'content',
    'header',
    'body',
    'footer',
    'kaartLarge',
    'toplevelContainer',
  ]

  connect() {
    this.observer = new MutationObserver((mutationList) => {
      mutationList.forEach((mutation) => {
        if (mutation.type == 'childList') {
          mutation.addedNodes.forEach((node) => {
            if (node instanceof Element) {
              console.log('MutationObserver')
              console.log(node)
              // this.dialogTarget.classList.add('show')
              // console.log(this.elementContentHeight(this.contentTarget))
              // this.contentTarget.style.height = `${this.elementContentHeight(this.contentTarget)}px`
              // this.contentTarget.style.opacity = 1
            }
          })
        }
      })
    })
    this.params = null
    requestAnimationFrame(() => {
      this.detailController = this.application.getControllerForElementAndIdentifier(
        document.querySelector('[data-controller~="detail"]'),
        'detail'
      )
    })
  }

  openModal(e) {
    e.preventDefault()
    this.abortController = new AbortController()
    this.params = e.params
    if (!this.hasTemplateTarget || !this.hasModalTarget) {
      return
    }
    const templateClone = this.getCloneModalTemplate()
    this.modalTarget.appendChild(templateClone)

    if (this.params.showMap) {
      this.showMapLarge()
    }
  }
  fetchModalContent(action) {
    fetch(action, { signal: this.abortController.signal })
      .then((response) => response.text())
      .then((text) => renderStreamMessage(text))
      .catch(function (err) {
        console.error(` Err: ${err}`)
      })
  }
  contentTargetConnected() {
    document.body.classList.add('show-modal')
    if (this.params.action) {
      this.fetchModalContent(this.params.action)
      // this.observer.observe(this.dialogTarget, { childList: true })
    } else if (this.params.content) {
      this.contentTarget.innerHTML = ''
      this.contentTarget.insertAdjacentHTML('beforeend', this.params.content)
    }

    this.dialogTarget.showModal()
    if (this.params.showMap) {
      document.querySelector('#modal_close_button').blur()
    }

    this.dialogTarget.addEventListener('cancel', (e) => {
      e.preventDefault()
      this.closeModal()
    })
    requestAnimationFrame(() => {
      if (this.params.cssClass) {
        this.dialogTarget.classList.add(...this.params.cssClass.split(' '))
      }
      this.dialogTarget.classList.add('fade-in')
    })

    this.dialogTarget.addEventListener('click', (event) => {
      var rect = this.dialogTarget.getBoundingClientRect()
      var isInDialog =
        rect.top <= event.clientY &&
        event.clientY <= rect.top + rect.height &&
        rect.left <= event.clientX &&
        event.clientX <= rect.left + rect.width

      if (event.screenX != 0 && event.screenY != 0 && !isInDialog) {
        this.closeModal()
      }
    })
  }
  getCloneModalTemplate() {
    return this.templateTarget.content.cloneNode(true)
  }

  turboActionModalTargetConnected(target) {
    this.turboActionModalTargetClone = target.cloneNode(true)
  }
  closeModal() {
    this.abortController.abort()
    this.dialogTarget.classList.remove('fade-in')
    if (this.params.showMap) {
      this.hideMapLarge()
    }
    setTimeout(() => {
      document.body.classList.remove('show-modal')
      if (this.hasDialogTarget) {
        this.dialogTarget.remove()
      }
    }, 300)
  }
  modalSluitenTargetConnected() {
    this.closeModal()
  }
  disconnect() {
    this.observer.disconnect()
  }

  showMapLarge() {
    setTimeout(() => {
      this.mapElement = this.detailController.getMapElement()
      this.originalMapContainer = this.mapElement.closest('.container__map')
      this.mapControlsElement = document.querySelector('.map__layer-controls')
      this.egdLegendElement = document.querySelector('[data-detail-target="egdLegendPanel"]')
      this.egdInfoBtnElement = document.querySelector('[data-detail-target="egdInfoBtn"]')
      this.kaartLargeTarget.appendChild(this.mapElement)
      if (this.mapControlsElement) {
        this.kaartLargeTarget.appendChild(this.mapControlsElement)
        this.bindMapControls()
      }
      if (this.egdLegendElement) {
        this.kaartLargeTarget.appendChild(this.egdLegendElement)
      }
      if (this.egdInfoBtnElement) {
        this.kaartLargeTarget.appendChild(this.egdInfoBtnElement)
      }
      this.syncMovedEgdControls()
    }, 100)
    setTimeout(() => {
      this.detailController.getMapInstance().invalidateSize()
      document.querySelector('#modal_close_button').focus()
    }, 200)
  }

  hideMapLarge() {
    document.querySelector('[data-detail-target="kaartDefault"]').appendChild(this.mapElement)
    if (this.mapControlsElement) {
      this.unbindMapControls()
      this.originalMapContainer?.appendChild(this.mapControlsElement)
    }
    if (this.egdLegendElement) {
      this.originalMapContainer?.appendChild(this.egdLegendElement)
    }
    if (this.egdInfoBtnElement) {
      this.originalMapContainer?.appendChild(this.egdInfoBtnElement)
    }
    document.removeEventListener('click', this._modalEgdLegendOutsideClick)
    setTimeout(() => {
      this.detailController.getMapInstance().invalidateSize()
    }, 100)
  }

  bindMapControls() {
    if (!this.mapControlsElement || this.mapControlsElement.dataset.modalBound === 'true') {
      return
    }

    this.mapControlsClickHandler = (event) => {
      const button = event.target.closest('.map__layer-btn, .map__layer-sub-btn, .btn-on-map--egd-info')
      if (!button || !this.kaartLargeTarget.contains(button)) {
        return
      }

      event.preventDefault()
      if (button.classList.contains('btn-on-map--egd-info')) {
        this.toggleMovedEgdLegend()
        return
      }

      this.toggleMovedMapControls(button)
    }

    this.mapControlsChangeHandler = (event) => {
      const input = event.target.closest('.map__layer-panel input')
      if (!input || !this.mapControlsElement.contains(input)) {
        return
      }

      this.detailController.onMapLayerChange({
        params: {
          mapLayerTypes: JSON.parse(input.dataset.detailMapLayerTypesParam || '[]'),
        },
        target: input,
      })

      this.syncMovedEgdControls()
    }

    this.kaartLargeTarget.addEventListener('click', this.mapControlsClickHandler)
    this.mapControlsElement.addEventListener('change', this.mapControlsChangeHandler)
    this.mapControlsElement.dataset.modalBound = 'true'
  }

  unbindMapControls() {
    if (!this.mapControlsElement || this.mapControlsElement.dataset.modalBound !== 'true') {
      return
    }

    this.kaartLargeTarget.removeEventListener('click', this.mapControlsClickHandler)
    this.mapControlsElement.removeEventListener('change', this.mapControlsChangeHandler)
    delete this.mapControlsElement.dataset.modalBound
  }

  toggleMovedMapControls(button) {
    const menu = this.mapControlsElement.querySelector('.map__layer-menu')
    const toggle = this.mapControlsElement.querySelector('.map__layer-btn')
    if (!menu || !toggle) {
      return
    }

    const panels = menu.querySelectorAll('.map__layer-panel')
    const setToggleState = (isOpen) => {
      toggle.querySelector('.map__layer-btn-icon--default').hidden = isOpen
      toggle.querySelector('.map__layer-btn-icon--active').hidden = !isOpen
    }
    const hideAllPanels = () => {
      panels.forEach((panel) => {
        panel.hidden = true
      })
    }

    if (button.classList.contains('map__layer-btn')) {
      if (menu.hidden) {
        menu.hidden = false
        setToggleState(true)
        return
      }

      menu.hidden = true
      hideAllPanels()
      setToggleState(false)
      return
    }

    if (menu.hidden) {
      menu.hidden = false
      setToggleState(true)
    }

    const panelName = button.dataset.detailPanelNameParam
    const panel = menu.querySelector(`[data-map-layer-panel="${panelName}"]`)
    if (!panel) {
      return
    }

    if (!panel.hidden) {
      menu.hidden = true
      hideAllPanels()
      setToggleState(false)
      return
    }

    hideAllPanels()
    panel.hidden = false
  }

  isEgdLayerChecked() {
    if (!this.mapControlsElement) {
      return false
    }

    const layerInputs = this.mapControlsElement.querySelectorAll('.map__layer-panel input[type="checkbox"]')
    return Array.from(layerInputs).some((input) => {
      const types = JSON.parse(input.dataset.detailMapLayerTypesParam || '[]')
      return types.includes('EGD') && input.checked
    })
  }

  syncMovedEgdControls() {
    if (!this.egdInfoBtnElement) {
      return
    }

    const shouldShowButton = this.isEgdLayerChecked()
    this.egdInfoBtnElement.hidden = !shouldShowButton

    if (!shouldShowButton && this.egdLegendElement) {
      this.egdLegendElement.hidden = true
      document.removeEventListener('click', this._modalEgdLegendOutsideClick)
    }
  }

  toggleMovedEgdLegend() {
    if (!this.egdLegendElement || !this.egdInfoBtnElement || this.egdInfoBtnElement.hidden) {
      return
    }

    const isOpen = !this.egdLegendElement.hidden
    this.egdLegendElement.hidden = isOpen

    if (!isOpen) {
      this._modalEgdLegendOutsideClick = (e) => {
        if (!this.egdLegendElement.contains(e.target) && e.target !== this.egdInfoBtnElement) {
          this.egdLegendElement.hidden = true
          document.removeEventListener('click', this._modalEgdLegendOutsideClick)
        }
      }
      setTimeout(() => document.addEventListener('click', this._modalEgdLegendOutsideClick), 0)
    } else {
      document.removeEventListener('click', this._modalEgdLegendOutsideClick)
    }
  }

  elementContentHeight(elem) {
    return Array.from(elem.children).reduce((total, elem) => {
      const style = window.getComputedStyle(elem)
      const height = ['top', 'bottom']
        .map(function (side) {
          return parseInt(style['margin-' + side], 10)
        })
        .reduce(function (t, side) {
          return t + side
        }, elem.getBoundingClientRect().height)

      return (total += height)
    }, 0)
  }
}

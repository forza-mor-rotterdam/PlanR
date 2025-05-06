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
    const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth
    document.body.classList.add('show-modal')
    this.toplevelContainerTarget.style.paddingRight = `${scrollbarWidth}px`
    console.log('CLONE')
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
      this.toplevelContainerTarget.style.paddingRight = ``
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
      this.kaartLargeTarget.appendChild(this.mapElement)
    }, 100)
    setTimeout(() => {
      this.detailController.getMapInstance().invalidateSize()
      document.querySelector('#modal_close_button').focus()
    }, 200)
  }

  hideMapLarge() {
    document.querySelector('[data-detail-target="kaartDefault"]').appendChild(this.mapElement)
    setTimeout(() => {
      this.detailController.getMapInstance().invalidateSize()
    }, 100)
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

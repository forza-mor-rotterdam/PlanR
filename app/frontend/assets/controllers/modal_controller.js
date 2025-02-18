import { Controller } from '@hotwired/stimulus'
import { renderStreamMessage } from '@hotwired/turbo'

export default class extends Controller {
  static targets = ['modal', 'modalSluiten', 'template', 'templateButton', 'dialog']

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
  }
  openModal(e) {
    e.preventDefault()
    this.abortController = new AbortController()
    this.params = e.params
    if (!this.hasTemplateTarget || !this.hasModalTarget || !this.hasTemplateButtonTarget) {
      return
    }
    const templateClone = this.getCloneModalTemplate()
    this.modalTarget.appendChild(templateClone)
  }
  fetchModalContent(action) {
    fetch(action, { signal: this.abortController.signal })
      .then((response) => response.text())
      .then((text) => renderStreamMessage(text))
      .catch(function (err) {
        console.error(` Err: ${err}`)
      })
  }
  dialogTargetConnected() {
    document.body.classList.add('show-modal')
    console.log('CLONE')
    if (this.params.action) {
      this.fetchModalContent(this.params.action)
      // this.observer.observe(this.dialogTarget, { childList: true })
    } else if (this.params.content) {
      this.dialogTarget.innerHTML = ''
      this.dialogTarget.insertAdjacentHTML('beforeend', this.params.content)
      this.dialogTarget.appendChild(this.templateButtonTarget.content.cloneNode(true))
    }

    this.dialogTarget.showModal()

    if (this.params.cssClass) {
      this.dialogTarget.classList.add(...this.params.cssClass.split(' '))
    }
    this.dialogTarget.addEventListener('close', () => {
      this.closeModal()
    })
    this.dialogTarget.addEventListener('click', (event) => {
      var rect = this.dialogTarget.getBoundingClientRect()
      var isInDialog =
        rect.top <= event.clientY &&
        event.clientY <= rect.top + rect.height &&
        rect.left <= event.clientX &&
        event.clientX <= rect.left + rect.width
      if (!isInDialog) {
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
    this.dialogTarget.close()
    document.body.classList.remove('show-modal')

    // TODO: dialog transitioned wait and remove
    this.dialogTarget.addEventListener('transitionend', () => {
      this.hasdialogTarget && this.dialogTarget.remove()
    })
    this.dialogTarget.remove()
  }
  modalSluitenTargetConnected() {
    this.closeModal()
  }
  disconnect() {
    this.observer.disconnect()
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

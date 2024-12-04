import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  initialize() {}

  connect() {
    if ('ontouchstart' in document.documentElement) {
      document.body.classList.add('hasTouch')
    }
    window.addEventListener('click', (e) => {
      if (
        !(e.target.closest('.container__uitklapper') || e.target.hasAttribute('data-action')) || // data-action conflicts with window.evenlistener
        e.target.classList.contains('btn-close--small')
      ) {
        this.noHover()
        document.querySelector('.container__uitklapper').classList.remove('show')
      }
    })
  }

  goToUrl(e) {
    window.location.href = e.params.url
  }

  show() {
    if ('ontouchstart' in document.documentElement) {
      this.element.classList.add('show')
    }
  }

  noHover(e) {
    // used to close popup with close-button while hovering
    const targetContainer = e?.params?.targetcontainer ?? 'container__uitklapper'
    this.element.closest(`.${targetContainer}`)?.classList.remove('show')
    this.element.closest(`.${targetContainer}`)?.classList.add('no-hover')
    this.element.blur()
    setTimeout(() => {
      this.element.closest(`.${targetContainer}`)?.classList.remove('no-hover')
    }, 500)
  }
}

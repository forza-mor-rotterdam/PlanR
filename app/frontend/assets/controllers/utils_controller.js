import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  goToUrl(e) {
    window.location.href = e.params.url
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

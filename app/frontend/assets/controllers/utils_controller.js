import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  initialize() {}

  connect() {}

  goToUrl(e) {
    window.location.href = e.params.url
  }

  noHover(e) {
    const targetContainer = e.params.targetcontainer ?? 'container__uitklapper'
    this.element.closest(`.${targetContainer}`).classList.add('no-hover')

    setTimeout(() => {
      this.element.blur()
      this.element.closest(`.${targetContainer}`).classList.remove('no-hover')
    }, 500)
  }
}

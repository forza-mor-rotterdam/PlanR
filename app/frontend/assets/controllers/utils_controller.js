import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  goToUrl(e) {
    window.location.href = e.params.url
  }
}

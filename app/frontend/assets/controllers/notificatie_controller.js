import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  connect() {}

  hideNotification(e) {
    e.target.closest('.notification').classList.add('hide')
  }
}

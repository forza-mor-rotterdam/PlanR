import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  connect() {
    const container = this.element
    const content = container.querySelector('.content__overflow')
    if (content) console.log('content', content)

    if (content?.scrollHeight > container?.clientHeight) {
      this.element.classList.add('has-overflow')

      this.element.addEventListener('click', function () {
        this.classList.toggle('show')
      })
    }
  }
}

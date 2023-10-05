import { Controller } from '@hotwired/stimulus'
export default class extends Controller {
  connect() {
    window.addEventListener('popstate', (event) => {
      const overviewElement = document.querySelector('#overview')
      if (overviewElement) {
        const overviewSrcAttr = overviewElement.getAttribute('src')
        if (overviewSrcAttr) {
          const urlPath = overviewSrcAttr.split('?')[0] + window.location.search
          Turbo.visit(urlPath, { frame: 'overview' })
        }
      }
    })
  }
}

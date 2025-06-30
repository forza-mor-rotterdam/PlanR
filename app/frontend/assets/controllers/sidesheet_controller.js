import { Controller } from '@hotwired/stimulus'
export default class extends Controller {
  static targets = ['sidesheet', 'turboframe']

  openSidesheet(e) {
    console.log('openSidesheet')
    if (this.hasSidesheetTarget && this.hasTurboframeTarget) {
      e.preventDefault()
      const sidesheet = this.sidesheetTarget
      this.turboframeTarget.setAttribute('src', e.params.action)
      sidesheet.classList.add('show')
    }
    document.body.classList.add('show-sidesheet')
  }

  closeSidesheet() {
    console.log('closeSidesheet')
    if (this.hasSidesheetTarget) {
      const sidesheet = this.sidesheetTarget
      sidesheet.classList.remove('show')
    }
    document.body.classList.remove('show-sidesheet')
  }
  toggleFilter() {
    document.body.classList.toggle('show-sidesheet-dashboardfilters')
  }
}

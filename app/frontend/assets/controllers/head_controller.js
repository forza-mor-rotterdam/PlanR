import { Controller } from '@hotwired/stimulus'
export default class extends Controller {
  static targets = ['mainScript']
  mainScriptTargetConnected() {
    if (this.mainScriptTargets.length > 1) {
      location.reload()
    }
  }
}

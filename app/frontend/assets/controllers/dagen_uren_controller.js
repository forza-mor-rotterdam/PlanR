import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  connect() {
    const seconden = this.element.dataset.value
    const urenSeconden = 60 * 60
    const dagenSeconden = 24 * urenSeconden
    const huidigeSeconden = Number(seconden)
    const huidigeDagenSeconden = huidigeSeconden - (huidigeSeconden % dagenSeconden)
    const huidigeUrenSeconden = huidigeSeconden - huidigeDagenSeconden
    const dagen = huidigeDagenSeconden / dagenSeconden
    const uren = (huidigeUrenSeconden - (huidigeUrenSeconden % urenSeconden)) / urenSeconden
    const dagString = dagen > 1 ? 'dagen' : 'dag'
    let result = ``
    if (dagen > 0) result += `${dagen} ${dagString}`
    if (dagen > 0 && uren > 0) result += ` en `
    if (uren > 0) result += `${uren} uur`
    this.element.textContent = result
  }
}

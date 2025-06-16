import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static values = {
    standaardExterneOmschrijvingLijst: String,
  }
  static targets = ['reden', 'specificatieOpties']

  connect() {
    console.log(this.identifier)
    this.standaardExterneOmschrijvingLijst = JSON.parse(this.standaardExterneOmschrijvingLijstValue)
    this.specificatieOptiesTargets
      .filter((elem) => elem.nodeName === 'INPUT')
      .map((elem) => {
        const standaardExterneOmschrijvingLijst = this.standaardExterneOmschrijvingLijst.filter(
          (externeOmschrijving) => externeOmschrijving.specificatie_opties.includes(elem.value)
        )
        const liBase = elem.closest('li')
        if (standaardExterneOmschrijvingLijst.length) {
          const div = document.createElement('DIV')
          const strong = document.createElement('SMALL')
          strong.textContent = `Externe omschrijvingen (${standaardExterneOmschrijvingLijst.length})`
          const ul = document.createElement('UL')
          standaardExterneOmschrijvingLijst.map((externeOmschrijving) => {
            const li = document.createElement('li')
            const a = document.createElement('a')
            a.href = externeOmschrijving.aanpassen_url
            a.textContent = '(aanpassen)'
            li.textContent = externeOmschrijving.titel
            li.appendChild(a)
            ul.appendChild(li)
          })
          // div.appendChild(strong)
          div.appendChild(ul)
          liBase.appendChild(div)
        }
      })
  }
}

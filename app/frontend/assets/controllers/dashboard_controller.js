import { Controller } from '@hotwired/stimulus'
export default class extends Controller {
  static targets = [
    'table',
    'alleMeldingenAantal',
    'nieuweMeldingenAantal',
    'nieuweMeldingenPercentage',
    'inBehandelingMeldingenAantal',
    'inBehandelingMeldingenPercentage',
    'controleMeldingenAantal',
    'controleMeldingenPercentage',
    'pauzeMeldingenAantal',
    'pauzeMeldingenPercentage',
    'lookbackAantal',
  ]
  static values = {
    data: String,
    type: String,
    stadsdeel: String,
    id: String,
    rowFilters: String,
  }

  connect() {
    this.tableData = JSON.parse(this.dataValue)
    this.rowFilters = JSON.parse(this.rowFiltersValue)
    this.periode = 24
    this.update()
  }
  setRowFilters(obj) {
    Object.entries(obj).map(([name, value]) => {
      if (value) {
        this.rowFilters[name] = value
      } else {
        delete this.rowFilters[name]
      }
    })
  }
  onWeergaveChangeHandler(e) {
    this.tableTargets.map((table) => {
      table.controllers.table.setRowFilters({ [e.target.name]: e.target.value })
    })
  }
  onStadsdeelChangeHandler(e) {
    this.setRowFilters({ [e.target.name]: e.target.value })
    this.tableTargets.map((table) => {
      table.controllers.table.setRowFilters({ [e.target.name]: e.target.value })
    })
    this.update()
    this.tableTargets.map((elem) => this.updateLookbackAantal(elem.controllers.table))
  }
  onPeriodeChangeHandler(e) {
    this.periode = parseInt(e.target.value)
    this.element.requestSubmit()
  }
  tableTargetConnected(table) {
    setTimeout(() => {
      this.updateLookbackAantal(table.controllers.table)
    }, 1)
  }
  updateLookbackAantal(tableController) {
    let lookbackAantal = 0
    const afgehandeld = tableController.totals.find((total) => total.key === 'afgehandeld')
    const aangemaakt = tableController.totals.find((total) => total.key === 'aangemaakt')
    if (aangemaakt && afgehandeld) {
      lookbackAantal = aangemaakt.value - afgehandeld.value
    }
    if (this.hasLookbackAantalTarget) {
      if (lookbackAantal != 0) {
        this.lookbackAantalTarget.textContent = `${Math.abs(lookbackAantal)} ${
          lookbackAantal < 0 ? 'minder' : 'meer'
        } meldingen dan ${this.periode} uur geleden'`
      } else {
        this.lookbackAantalTarget.textContent = `${this.periode} uur geleden was dit hetzelfde`
      }
    }
  }

  update() {
    const columnKeyAantalTargets = {
      alle_meldingen: 'alleMeldingen',
      nieuwe_meldingen: 'nieuweMeldingen',
      meldingen_in_behandeling: 'inBehandelingMeldingen',
      meldingen_controle: 'controleMeldingen',
      meldingen_pauze: 'pauzeMeldingen',
    }
    const rowFiltersEntries = Object.entries(this.rowFilters)
    const tableData = this.tableData.filter(
      (rowData) =>
        rowFiltersEntries.filter(([key, value]) => rowData.filters[key] === value).length >=
        rowFiltersEntries.length
    )
    const totals = tableData[0].columns
      .filter((columnData) => Number.isInteger(columnData.value))
      .map((columnData) => {
        return {
          value: 0,
          key: columnData.key,
        }
      })
    tableData.map((rowData) => {
      rowData.columns
        .filter((columnData) => Number.isInteger(columnData.value))
        .map((columnData, ii) => {
          totals[ii].value += columnData.value
        })
    })
    const alleMeldingenAantal = totals.find((v) => v.key === 'alle_meldingen').value
    totals.map((v) => {
      if (!columnKeyAantalTargets[v.key]) {
        return
      }
      const hasAantal =
        this[
          `has${columnKeyAantalTargets[v.key].charAt(0).toUpperCase()}${columnKeyAantalTargets[
            v.key
          ].slice(1)}AantalTarget`
        ]
      const hasPercentage =
        this[
          `has${columnKeyAantalTargets[v.key].charAt(0).toUpperCase()}${columnKeyAantalTargets[
            v.key
          ].slice(1)}PercentageTarget`
        ]
      if (hasAantal) {
        this[`${columnKeyAantalTargets[v.key]}AantalTarget`].textContent = v.value
      }
      if (alleMeldingenAantal && hasPercentage) {
        this[`${columnKeyAantalTargets[v.key]}PercentageTarget`].textContent = `${Math.round(
          (v.value / alleMeldingenAantal) * 100
        )}%`
      }
    })
  }
}

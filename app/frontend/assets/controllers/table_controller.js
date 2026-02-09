import { Controller } from '@hotwired/stimulus'
export default class extends Controller {
  static values = {
    data: String,
    id: String,
    rowFilters: String,
    sortKey: String,
  }
  initialize() {}
  connect() {
    if (!this.element.controllers) {
      this.element.controllers = {}
    }
    this.element.controllers[this.identifier] = this
    this.tableData = JSON.parse(this.dataValue)
    this.tableDataFilteredSorted = []
    this.id = this.idValue
    this.sortKey = this.sortKeyValue
    this.sortDirection = 'asc'
    this.rowFilters = JSON.parse(this.rowFiltersValue)
    this.render()
  }
  download(data) {
    const blob = new Blob([data], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `download_${this.id}.csv`
    a.click()
  }
  csvmaker(data) {
    let csvRows = []
    const headers = data[0].columns.map((columnData) => columnData.column)
    csvRows.push(headers.join(','))
    this.tableDataFilteredSorted.map((rowData) => {
      csvRows.push(rowData.columns.map((column) => column.value).join(','))
    })
    return csvRows.join('\n')
  }

  setRowFilters(obj) {
    Object.entries(obj).map(([name, value]) => {
      if (value) {
        this.rowFilters[name] = value
      } else {
        delete this.rowFilters[name]
      }
    })
    this.render()
  }
  sorterClickHandler(e) {
    if (this.sortKey === e.params.columnHeadId) {
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc'
    } else {
      this.sortDirection = 'asc'
      this.sortKey = e.params.columnHeadId
    }
    this.render()
  }
  onExportClickHandler() {
    const csvdata = this.csvmaker(this.tableDataFilteredSorted)
    console.log(csvdata)
    this.download(csvdata)
  }
  render() {
    const rowTemplate = document.getElementById(`${this.id}_table_row`)
    const headCellTemplate = document.getElementById(`${this.id}_table_head_cell`)
    const bodyCellTemplate = document.getElementById(`${this.id}_table_body_cell`)
    const footCellTemplate = document.getElementById(`${this.id}_table_foot_cell`)

    const thead = this.element.querySelector('thead')
    const tbody = this.element.querySelector('tbody')
    const tfoot = this.element.querySelector('tfoot')
    thead.innerHTML = ''
    tbody.innerHTML = ''
    tfoot.innerHTML = ''
    const footRowClone = rowTemplate.content.cloneNode(true)
    const footRow = footRowClone.querySelector('[data-table-row]')

    const rowFiltersEntries = Object.entries(this.rowFilters)

    // filter & sort data
    this.tableDataFilteredSorted = this.tableData
      .filter(
        (rowData) =>
          rowFiltersEntries.filter(([key, value]) => rowData.filters[key] === value).length >=
          rowFiltersEntries.length
      )
      .sort((a, b) => {
        const columnA = a.columns.find((column) => column.key == this.sortKey)
        const columnB = b.columns.find((column) => column.key == this.sortKey)
        if (columnA && columnB && typeof columnB.value === 'string') {
          const a = columnA.value.toUpperCase()
          const b = columnB.value.toUpperCase()
          const dir = this.sortDirection === 'asc' ? 1 : -1
          return a < b ? -1 * dir : a > b ? 1 * dir : 0
        } else {
          return this.sortDirection === 'asc'
            ? columnB.value - columnA.value
            : columnA.value - columnB.value
        }
      })

    // exit when no data
    if (!this.tableDataFilteredSorted.length) {
      return
    }

    // redraw table
    const headRowClone = rowTemplate.content.cloneNode(true)
    const headRow = headRowClone.querySelector('[data-table-row]')
    thead.appendChild(headRow)

    // redraw table head
    this.tableDataFilteredSorted[0].columns.map((columnData) => {
      const headCellClone = headCellTemplate.content.cloneNode(true)
      const cell = headCellClone.querySelector('[data-table-head-cell]')
      const title = cell.querySelector('[data-table-head-label]')
      const sorter = cell.querySelector('[data-table-head-sorter]')

      title.textContent = columnData.column
      sorter.setAttribute('data-table-column-head-id-param', columnData.key)
      if (columnData.key === this.sortKey) {
        cell.classList.add('table-sort-active', `tabel-sort-direction-${this.sortDirection}`)
      } else {
        cell.classList.remove(
          'table-sort-active',
          'table-sort-direction-asc',
          'table-sort-direction-desc'
        )
      }
      cell.setAttribute('data-table-column-head-id-param', columnData.key)
      cell.setAttribute('data-column-head-id', columnData.key)
      cell.setAttribute('data-sort-direction', 'desc')
      cell.setAttribute('data-sort-order', '0')
      headRow.appendChild(cell)
    })
    // redraw table body
    this.tableDataFilteredSorted.map((rowData) => {
      const rowClone = rowTemplate.content.cloneNode(true)
      const row = rowClone.querySelector('[data-table-row]')
      rowData.columns.map((columnData) => {
        const bodyCellClone = bodyCellTemplate.content.cloneNode(true)
        const cell = bodyCellClone.querySelector('[data-table-body-cell]')
        cell.textContent = columnData.value
        cell.dataset.columnRowId = columnData.key
        row.appendChild(cell)
      })

      tbody.appendChild(rowClone)
    })

    // redraw table footer
    this.totals = this.tableDataFilteredSorted[0].columns.map((columnData) => {
      return {
        value: Number.isInteger(columnData.value) ? 0 : 'Totaal',
        key: columnData.key,
      }
    })
    this.tableDataFilteredSorted.map((rowData) => {
      rowData.columns.map((columnData, ii) => {
        if (Number.isInteger(columnData.value)) {
          this.totals[ii].value += columnData.value
        }
      })
    })
    this.tableDataFilteredSorted.push({
      columns: this.totals,
    })
    this.totals.map((v) => {
      const footCellClone = footCellTemplate.content.cloneNode(true)
      const cell = footCellClone.querySelector('[data-table-foot-cell]')
      cell.textContent = v.value
      // this.tableDataFilteredSorted[this.tableDataFilteredSorted.length-1]
      footRow.appendChild(cell)
    })
    tfoot.appendChild(footRow)
  }
}

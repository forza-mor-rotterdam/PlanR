import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['columnHead', 'row']

  connect() {}
  removeSortOrderHandler(e) {
    const columnHeadElement = this.getColumnHeadElement(e.params.columnHeadId)
    const incommingSortOrder = parseInt(columnHeadElement.dataset.sortOrder)
    if (incommingSortOrder === 0) {
      return
    }
    columnHeadElement.dataset.sortOrder = 0
    const currentSortingElements = this.columnHeadTargets.filter(
      (elem) => parseInt(elem.dataset.sortOrder) > incommingSortOrder
    )
    currentSortingElements.map((elem) => {
      elem.dataset.sortOrder--
    })
    this.sortTable()
  }
  getColumnHeadElement(columnHeadId) {
    return this.columnHeadTargets.find((elem) => elem.dataset.columnHeadId === columnHeadId)
  }
  thClickHandler(e) {
    const columnHeadElement = this.getColumnHeadElement(e.params.columnHeadId)
    const incommingSortOrder = parseInt(columnHeadElement.dataset.sortOrder)

    const currentSortingElements = this.columnHeadTargets.filter(
      (elem) => parseInt(elem.dataset.sortOrder) > 0
    )
    if (incommingSortOrder === 0) {
      currentSortingElements.map((elem) => {
        elem.dataset.sortOrder++
      })
    } else if (incommingSortOrder != 1) {
      currentSortingElements
        .filter((elem) => parseInt(elem.dataset.sortOrder) <= incommingSortOrder)
        .map((elem) => {
          elem.dataset.sortOrder++
        })
    }
    columnHeadElement.dataset.sortOrder = 1
    columnHeadElement.dataset.sortDirection =
      columnHeadElement.dataset.sortDirection === 'desc' ? 'asc' : 'desc'
    this.sortTable()
  }
  sortTable() {
    this.columnHeadTargets.filter((elem) => {
      const indicator = elem.querySelector('[data-sort-order-indicator]')
      if (elem.dataset.sortOrder != '0') {
        indicator.style.display = 'inline'
        indicator.textContent = elem.dataset.sortOrder
      } else {
        indicator.style.display = 'none'
        indicator.textContent = ''
      }
    })
    const columnIdList = this.columnHeadTargets
      .filter((elem) => parseInt(elem.dataset.sortOrder) > 0)
      .map((elem) => [
        parseInt(elem.dataset.sortOrder),
        elem.dataset.columnHeadId,
        elem.dataset.sortDirection,
      ])
      .sort((a, b) => a[0] - b[0])
      .map((c) => [c[1], c[2]])
    console.log(columnIdList.map((sortData) => sortData[0]))
    this.rowTargets
      .map((row) => {
        const sortIntegers = columnIdList.map((sortData) => {
          const sortElem = row.querySelector(`td[data-column-row-id="${sortData[0]}"]`)
          if (!sortElem) {
            return 0
          }
          return sortElem.dataset[sortData[1]]
        })
        row.dataset.order = parseInt(sortIntegers.join(''))
        return row
      })
      .sort((a, b) => parseInt(a.dataset.order) - parseInt(b.dataset.order))
      .map((row, i) => {
        row.style.order = i
      })
  }
}

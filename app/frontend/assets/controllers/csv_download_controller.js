import { Controller } from '@hotwired/stimulus'
export default class extends Controller {
  static values = {
    data: String,
    title: String,
  }
  initialize() {
    this.json_data = JSON.parse(this.dataValue)
    const title = this.titleValue ? this.titleValue : 'csv_bestand'
    const csv = this.toCSV()
    this.element.setAttribute('download', title)
    this.element.setAttribute('href', 'data:text/csv;charset=utf-8,' + this.escapeString(csv))
  }
  escapeString(str) {
    const allowed = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@*_+-./,'
    str = str.toString()
    let len = str.length,
      R = '',
      k = 0,
      S,
      chr,
      ord
    while (k < len) {
      chr = str[k]
      if (allowed.indexOf(chr) != -1) {
        S = chr
      } else {
        ord = str.charCodeAt(k)
        if (ord < 256) {
          S = '%' + ('00' + ord.toString(16)).toUpperCase().slice(-2)
        } else {
          S = '%u' + ('0000' + ord.toString(16)).toUpperCase().slice(-4)
        }
      }
      R += S
      k++
    }
    return R
  }
  toCSV() {
    const arr = this.json_data
    if (Array.isArray(arr) && arr.length > 0) {
      const fArr = arr.map((o) => {
        // eslint-disable-next-line no-unused-vars
        return (({ bar, ...rest }) => rest)(o)
      })
      return [Object.keys(fArr[0])]
        .concat(fArr)
        .map((row) => {
          return Object.values(row)
            .map((value) => {
              return typeof value === 'string' ? JSON.stringify(value) : value
            })
            .join(';')
        })
        .join('\n')
    }
    console.warn('No valid csv input data')
    return ''
  }
}

import { Application as StimulusApplication } from '@hotwired/stimulus'
import { start as TurboStart } from '@hotwired/turbo'
import { definitionsFromContext } from '@hotwired/stimulus-webpack-helpers'
import Chart from '@stimulus-components/chartjs'

if (typeof document.App === 'undefined') {
  document.App = StimulusApplication.start()
  document.App.register('chart', Chart)
  const context = require.context('./controllers', true, /\.js$/)
  document.App.load(definitionsFromContext(context))
  window.Stimulus = document.App
  TurboStart()
}

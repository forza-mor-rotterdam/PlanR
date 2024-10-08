import { Application as StimulusApplication } from '@hotwired/stimulus'
import { start as TurboStart } from '@hotwired/turbo'
import { definitionsFromContext } from '@hotwired/stimulus-webpack-helpers'
import Chart from '@stimulus-components/chartjs'

const application = StimulusApplication.start()
application.register('chart', Chart)
const context = require.context('./controllers', true, /\.js$/)
application.load(definitionsFromContext(context))
window.Stimulus = application

TurboStart()

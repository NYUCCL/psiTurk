#  Filename: ContentView.coffee
define [
    'inspiritas'
  ], (Inspiritas) ->
    class ContentView extends Backbone.View

      initialize: ->
        @render()

      render: ->
        loadCharts()

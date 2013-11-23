#  Filename: ChartView.coffee
define [
  'jquery'
  'backbone'
  'models/ChartModel'],
  ($,
  Backbone
  ChartModel) ->
    #class ChartView extends Backbone.View
    ChartView = Backbone.View.extend({
      el: '#mainChart'

      data: []
      chart: () ->
        $('#mainChart').highcharts({
           chart:
             type: 'column'
           legend: {enabled: false}
           title:
             text: 'Participant Status'
           showInLegend: false
           xAxis:
             categories: @categories
           yAxis:
             title:
               text: '# of participants'
           plotOptions:
             column:
               cursor: 'pointer'
               dataLabels:
                 enabled: true
                 color: @color
                 style:
                   fontWeight: 'bold'
                 formatter: ->
                   "#{@y}"
           tooltip:
             formatter: ->
               s = "#{@x} :<b> #{@y} </b><br/>"
               return s
           series: [{
             data : @data
             color: 'white'
           }]
           exporting:
             enabled: false
         }).highcharts() # return chart

      initialize: ->
        @model= new ChartModel
        @colors =  Highcharts.getOptions().colors
        @categories = ['Allocated', 'Started', 'Completed',
                       'Debriefed', 'Credited', 'Quit Early']
        proms = @getData()
        proms.done(=>@setChart())

      getData: ->
        promise = @model.fetch()
        promise.done(=>
          @data = [
            {
              y: @model.get("debriefed")
              color: "#EF643E"
            }, {
              y: @model.get("started")
              color: "#EF643E"
            }, {
              y: @model.get("completed")
              color: "#ef643e"
            }, {
              y: @model.get("credited")
              color: "#ef643e"
            }, {
              y: @model.get("allocated")
              color: "#ef643e"
            }, {
              y: @model.get("quit_early")
              color: "#ef643e"
            }
          ])

      setChart: () ->
        chart = @chart()
        chart.xAxis[0].setCategories(@categories, false)
        chart.series[0].remove(false)
        chart.addSeries(
          name: @name
          data: @data
          color: @color or 'white'
          false)
        chart.redraw()

      refresh: ->
        @getData()
        @setChart()
    })

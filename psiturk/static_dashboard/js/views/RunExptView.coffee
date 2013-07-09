#  Filename: RunExptView.coffee
define [
    'jquery'
    'backbone'
    'text!templates/run-expt-modal.html'
  ],
  (
    $
    Backbone
    RunExptTemplate
  ) ->

    class RunExptView extends Backbone.View

      initialize: ->
        @render()

      render: ->
        runExptTemplate = _.template RunExptTemplate,
          n_assignments: @options.config.get("HIT Configuration").max_assignments
          reward: @options.config.get("HIT Configuration").reward
          duration: @options.config.get("HIT Configuration").duration
          title: @options.config.get("HIT Configuration").title
        $('#run-expt-body').html(runExptTemplate)


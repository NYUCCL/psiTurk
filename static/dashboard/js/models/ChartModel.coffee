#  Filename: models/ConfigModel.coffee
define [
    'underscore'
    'backbone'
  ], (_, Backbone) ->

    class ChartModel extends Backbone.Model

      url: '/participant_status'

      defaults:
        debriefed: 0
        started: 0
        completed: 0
        total: 0
        credited: 0
        allocated: 0
        quit_early: 0

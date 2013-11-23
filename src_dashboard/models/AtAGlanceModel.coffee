#  Filename: models/ConfigModel.coffee
define [
    'underscore'
    'backbone'
  ], (_, Backbone) ->

    class AtAGlanceModel extends Backbone.Model

      url: '/at_a_glance_model'

      defaults:
        balance: "-"

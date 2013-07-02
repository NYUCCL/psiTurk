#  Filename: HITModel.coffee
define [
        "backbone"
      ],
      (
        Backbone
      ) ->

        class HIT extends Backbone.Model
          defaults:
            status: ""
            number_assignments_available: ""
            number_assignments_completed: ""
            hitid: ""
            max_assignments: 0
            title: ""
            number_assignments_pending: 0
            creation_time: ""
            number_assignments_completed: 0
            expiration: ""

#  Filename: HITModel.coffee
define [
        "backbone"
      ],
      (
        Backbone
      ) ->

        class Worker extends Backbone.Model
          defaults:
            "assignmentId": ""
            "workerId": ""
            "accept_time": ""
            "hitid": ""
            "submit_time": ""

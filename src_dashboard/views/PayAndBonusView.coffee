#  Filename: HITView.coffee
define [
        "backbone"
        "views/TableView"
      ],
      (
        Backbone
      ) ->

        class PayAndBonusView extends Backbone.TableView

          title: " "

          columns:
            title:
              header: "Worker Id"
              draw: (model) ->
                model.get "workerId"
            hitid:
              header: "HIT Id"
              draw: (model) ->
                model.get "hitId"
            # accept_time:
            #   header: "Accept Time"
            #   draw: (model) ->
            #     new Date(model.get "accept_time")
            submit_time:
              header: "Submit Time"
              draw: (model) ->
                new Date(model.get "submit_time")
            expire:
              header: " "
              draw: (model) ->
                id = model.get "assignmentId"
                button = "<button id=#{id} class='btn btn-small approve btn-success'>Approve</button>"
                return(button)
            extend:
              header: " "
              draw: (model) ->
                id = model.get "assignmentId"
                button = "<button id=#{id} class='btn btn-small reject btn-danger'>Reject</button>"
                return(button)

          pagination: true
          size: 25

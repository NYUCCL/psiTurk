#  Filename: HITView.coffee
define [
        "backbone"
      ],
      (
        Backbone
      ) ->

        class HITTableView extends Backbone.TableView
          title: ""
          columns:
            title:
              header: "Title"
            hitid:
              header: "HIT Id"
            number_assignments_available:
              header: "Left"
            max_assignments:
              header: "Max"
            number_assignments_completed:
              header: "Done"
            expiration:
              header: "Expires"
              draw: (model) ->
                new Date(model.get "expiration").toISOString()
          pagination: false
          size: 5

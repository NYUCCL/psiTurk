##  Filename: WorkerCollection.coffee
define [
        "backbone"
        "models/WorkerModel"
      ],
      (
        Backbone
        WorkerModel
      ) ->

        class Workers extends Backbone.Collection
          model: WorkerModel
          url: "/get_workers"
          parse: (resp) ->
            @allModels = resp.workers
          initialize: ->
            @reset @allModels
          count: =>
            @filteredModels.length
          fetch: (options) =>  # TODO(): Avoid overwriting fetch, but allows for easier communication with tableview
            fetchPromise = $.ajax
              url: @url
              type: "GET"
              success: (data) =>
                @allModels = data.workers
            fetchPromise.done =>
              @filteredModels = _.chain(@allModels)
                .filter((m) -> not options.data.type? or options.data.type == "" or
                               m.type == options.data.type)
                .filter((m) -> not options.data.name? or
                               m.name.toLowerCase().indexOf(options.data.name.toLowerCase()) >= 0)
                .sortBy(options.data.sort_col)
                .tap((o) -> options.data.sort_dir == "desc" and o.reverse())
                .value()
              page = options.data.page
              # size = options.data.size
              size = 25
              offset = (page - 1) * size
              @reset(_.first(_.rest(@filteredModels, offset), size))


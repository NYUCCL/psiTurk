#  Filename: app.coffee
define [
      'jquery'
      'underscore'
      'backbone'
      'router'
      'models/ConfigModel'
      'models/AtAGlanceModel'
      'views/SidebarView'
      'views/ContentView'
      'text!templates/overview.html'
      'text!templates/sidebar.html'
      'views/HITView'
      'models/HITModel'
      'collections/HITCollection'
      # 'views/ChartView'
      # 'models/ChartModel'
      # 'highcharts'
    ],
    (
      $
      _
      Backbone
      Router
      ConfigModel
      AtAGlanceModel
      SidebarView
      ContentView
      OverviewTemplate
      SideBarTemplate
      HITView
      HIT
      HITs
      # ChartView
      # ChartModel
      # Highcharts
    ) ->

      # Prevent links from reloading the page
      events:
        'click a' : 'pushstateClick'
        'click li' : 'pushstateClick'

      pushstateClick: (event) ->
        event.preventDefault()

      initialize: ->
        #  Pass in our router module and call it's initialize function
        Router.initialize()

        $('#server_on').on "click", ->
          $('#server_status').css "color": "yellow"

        # Listen for server status via socket.io
        $ ->
          socket = io.connect '/server_status'
          socket.on "connect", ->
            $.ajax
              url: "/monitor_server"
          socket.on 'status', (data) ->
            if parseInt(data) is 0
              $('#server_status').css "color": "green"
              $('#server_on')
                .css "color": "grey"
              $('#server_off').css "color": "orange"
            else
              $('#server_status').css({"color": "red"})
              $('#server_off')
                .css "color": "grey"
              $('#server_on').css "color": "orange"

        # Load at-a-glance model and data
        @ataglance = new AtAGlanceModel
        atAGlancePromise = @ataglance.fetch()
        atAGlancePromise.done(=>
          # Load configuration model
          @config = new ConfigModel
          configPromise = @config.fetch()
          configPromise.done(=>
            overview = _.template(OverviewTemplate,
              input:
                balance: @ataglance.get("balance")
                debug: if @config.get("Server Parameters").debug is "True" then "checked" else ""
                using_sandbox: if @config.get("HIT Configuration").using_sandbox is "True" then "checked" else "")
            $('#content').html(overview)
            # chrtView = new ChartView()
            # chrtView.initialize()
            # chrtView.setChart()
            # Load and add side bar html
            sideBarHTML = _.template(SideBarTemplate)
            $('#sidebar').html(sideBarHTML)
            sidebarView = new SidebarView(
              config: @config
              ataglance: @ataglance)
              # chart: chrtView)
          ))

        # Load content view after html; req's ids to be present
        contentView = new ContentView()
        contentView.initialize()

        # Have run button listen for clicks and tell server to create HITS
        # TODO(Jay): Combine and abstract the following functions-DRY principle.
        $('#run').on "click", ->
          $('#run-expt-modal').modal('show')
          $('#run-expt-btn').on "click", ->
            $.ajax
              contentType: "application/json; charset=utf-8"
              url: '/mturk_services'
              type: "POST"
              dataType: 'json'
              data: JSON.stringify mturk_request : "create_hit"
              success: ->
                $('#expire').css "color": "orange"
                $('#extend').css "color": "orange"
              complete: ->
                # reload HIT table
                $('#run-expt-modal').modal('hide')
                hit_view = new HITView collection: new HITs
                $("#tables").html hit_view.render().el
              error: (error) ->
                console.log(error)
                $('#expire-modal').modal('hide')

        $('#expire').on "click", ->
          # $('#expire-expt-modal').modal('show')
          # $('#expire-expt-btn').on "click", ->
          $.ajax
            contentType: "application/json; charset=utf-8"
            url: '/mturk_services'
            type: "POST"
            dataType: 'json'
            data: JSON.stringify
              mturk_request: "get_active_hits"

        # Shutdown button
        $("#server_off").on "click", ->
          $('#server-off-modal').modal('show')
          $('#shutdownServerBtn').on "click", ->
            $('#server_status').css "color": "yellow"
            $.ajax
              url: '/shutdown'
              type: "GET"
              success: $('#server-off-modal').modal('hide')

        # Run button
        $("#server_on").on "click", ->
          $.ajax
            url: '/launch'
            type: "GET"
            success:  # Get new socket for monitoring
              $ ->
                socket = io.connect '/server_status'
                socket.on "connect", ->
                  $.ajax
                    url: "/monitor_server"
                socket.on 'status', (data) ->
                  if parseInt(data) is 0
                    $('#server_status').css "color": "green"
                    $('#server_on')
                      .css "color": "grey"
                    $('#server_off').css "color": "orange"
                  else
                    $('#server_status').css({"color": "red"})
                    $('#server_off')
                      .css "color": "grey"
                    $('#server_on').css "color": "orange"

        # Expire button
        getExperimentStatus = ->
          $.ajax
            contentType: "application/json; charset=utf-8"
            url: '/mturk_services'
            type: "POST"
            dataType: 'json'
            data: JSON.stringify
              mturk_request: "get_active_hits"
            success: (data) ->
              if data.hits.length > 0
                $('#experiment_status').css "color": "green"
                $('#run').css({"color": "grey"})
                $('#expire').css({"color": "orange"})
                $('#extend').css({"color": "orange"})
                $('#extend').css({"color": "orange"})
              else
                $('#experiment_status').css "color": "green"
                $('#run').css({"color": "orange"})
                $('#expire').css({"color": "grey"})
                $('#extend').css({"color": "grey"})

        getExperimentStatus()

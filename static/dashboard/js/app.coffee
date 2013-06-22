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
      'views/chartView'
      'models/ChartModel'
      'highcharts'
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
      ChartView
      ChartModel
      Highcharts
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
              $('#run').css "color": "orange"
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
            chrtView = new ChartView()
            chrtView.initialize()
            chrtView.setChart()
            # Load and add side bar html
            sideBarHTML = _.template(SideBarTemplate)
            $('#sidebar').html(sideBarHTML)
            sidebarView = new SidebarView(
              config: @config
              ataglance: @ataglance
              chart: chrtView)
            sidebarView.initialize()
          ))

        # Load content view after html; req's ids to be present
        contentView = new ContentView()
        contentView.initialize()

        # Have run button listen for clicks and tell server to create HITS
        $('#run').on "click", ->
          $('#run-expt-modal').modal('show')
          $('#crate-hit-btn').on "click", ->
            $.ajax url: "/create_hit"

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
                    $('#run').css "color": "orange"
                  else
                    $('#server_status').css({"color": "red"})
                    $('#server_off')
                      .css "color": "grey"
                    $('#server_on').css "color": "orange"



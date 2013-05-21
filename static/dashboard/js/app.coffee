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
    ) ->

      # Prevent links from reloading the page
      events:
        'click a' : 'pushstateClick'
        'click li' : 'pushstateClick'

      pushstateClick: (event) ->
        event.preventDefault()

      initialize: ->
        #  Pass in our Router module and call it's initialize function
        Router.initialize()

        # Listen for server status via socket.io
        $ ->
          socket = io.connect '/server_status'
          socket.on "connect", ->
            $.ajax
              url: "/monitor_server"
              async: false
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
        ataglance = new AtAGlanceModel
        ataglance.fetch async: false

        # Load configuration model
        config = new ConfigModel
        config.fetch async: false

        # Load and add content html
        overviewContentHTML = _.template(OverviewTemplate,
          input:
            balance: ataglance.get("balance")
            debug: if config.get("Server Parameters").debug is "True" then "checked" else ""
            using_sandbox: if config.get("HIT Configuration").using_sandbox is "True" then "checked" else "")
        $('#content').html(overviewContentHTML)

        # Load and add side bar html
        sideBarHTML = _.template(SideBarTemplate)
        $('#sidebar').html(sideBarHTML)
        sidebarView = new SidebarView(
          config: config
          ataglance: ataglance)
        sidebarView.initialize()

        # Load content view after html; req's ids to be present
        contentView = new ContentView()
        contentView.initialize()

        # Have run button listen for clicks and tell server to create HITS
        $('#run').on "click", ->
          $.ajax url: "/create_hit"

        # Shutdown button
        $("#server_off").on "click", ->
          url = config.get("HIT Configuration").question_url + '/shutdown'
          url_pattern =  /^https?\:\/\/([^\/:?#]+)(?:[\/:?#]|$)/i
          domain = url.match(url_pattern)[0] + config.get("Server Parameters").port + '/shutdown'
          $.ajax
            url: domain
            type: "GET"
            data: {hash: config.get("Server Parameters").hash}

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
                    # async: false
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

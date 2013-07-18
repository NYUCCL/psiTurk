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
      'views/RunExptView'
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
      RunExptView
    ) ->

      # Prevent links from reloading the page
      events:
        'click a' : 'pushstateClick'
        'click li' : 'pushstateClick'

      pushstateClick: (event) ->
        event.preventDefault()

      getCredentials: ->
        $('#aws-info-modal').modal('show')
        $('.save').click (event) =>
          event.preventDefault()
          @save(event)
          $('#aws-info-modal').modal('hide')

      verifyAWSLogin: ->
        config = new ConfigModel
        configPromise = config.fetch()
        configPromise.done(=>
          key_id = config.get("AWS Access").aws_access_key_id
          secret_key = config.get("AWS Access").aws_secret_access_key
          inputData = {}
          inputData["aws_access_key_id"] = key_id
          inputData["aws_secret_access_key"] = secret_key
          $.ajax
            url: "/verify_aws_login"
            type: "POST"
            dataType: "json"
            contentType: "application/json; charset=utf-8"
            data: JSON.stringify inputData
            success: (response) =>
              if response.aws_accnt is 0
                @getCredentials()
                $('#aws-indicator').css("color", "red")
                  .attr("class", "icon-lock")
              else
                $('#aws-indicator').css("color", "white")
                  .attr("class", "icon-unlock")

            error: ->
              console.log("aws verification failed"))

      getExperimentStatus: ->
        $.ajax
          url: '/get_hits'
          type: "GET"
          success: (data) ->
            if data.hits.length > 0
              $('#experiment_status').css "color": "green"
              $('#run').css({"color": "grey"})
            else
              $('#experiment_status').css "color": "grey"
              $('#run').css({"color": "orange"})

      save: (event) ->
        # Prevent clicks from reloading page
        event.preventDefault()

        section = $(event.target).data 'section'
        inputData = {}
        configData = {}
        $.each($('#myform').serializeArray(), (i, field) ->
          inputData[field.name] = field.value)
        configData[section] = inputData
        @config = new ConfigModel
        configPromise = @config.fetch()
        configPromise.done(=>
          @config.save configData,
            complete: => @verifyAWSLogin())

      initialize: ->
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
        atAGlancePromise = @ataglance.fetch() #{error: => @ataglance.set("balance", "-") })
        atAGlancePromise.done(=>
          # Load configuration moder
          @config = new ConfigModel
          configPromise = @config.fetch()
          configPromise.done =>
            overview = _.template(OverviewTemplate,
              input:
                balance: if @ataglance.get("balance") is "unable to access aws" then "-" else @ataglance.get("balance")
                debug: if @config.get("Server Parameters").debug is "True" then "checked" else ""
                using_sandbox: if @config.get("HIT Configuration").using_sandbox is "True" then "checked" else "")
            $('#content').html(overview)
            sideBarHTML = _.template(SideBarTemplate)
            $('#sidebar').html(sideBarHTML)
            sidebarView = new SidebarView
              config: @config
              ataglance: @ataglance)

        # Load content view after html; req's ids to be present
        contentView = new ContentView()
        contentView.initialize()
        @verifyAWSLogin()

        # Have run button listen for clicks and tell server to create HITS
        # Before running expt, get latest config and verify
        # TODO(Jay): Combine and abstract the following functions-DRY principle.
        # There's a general pattern of loading ajax data and updating GUI which
        # can easily be abstracted
        updateExperimentStatus = _.bind(@getExperimentStatus, @)  # bind "this" to current namespace, before it's buried by callbacks
        $('#run').on "click", ->
          @config = new ConfigModel
          configPromise = @config.fetch()
          configPromise.done(=>
            runExptView = new RunExptView config: @config
            $('#run-expt-modal').modal('show')
            $('.run-expt').on "keyup", (event) =>
              inputData = {}
              configData = {}
              $.each($('#expt-form').serializeArray(), (i, field) ->
                inputData[field.name] = field.value
              )
              # Update amounts in GUI
              $('#total').html (inputData["reward"]*inputData["max_assignments"]*1.10).toFixed(2)
              $('#fee input').val (inputData["reward"]*inputData["max_assignments"]*.10).toFixed(2)

              configData["HIT Configuration"] = inputData
              @config.save configData

            $('#run-expt-btn').on "click", ->
              $.ajax
                contentType: "application/json; charset=utf-8"
                url: '/mturk_services'
                type: "POST"
                dataType: 'json'
                data: JSON.stringify mturk_request : "create_hit"
                complete: ->
                  # reload HIT table
                  $('#run-expt-modal').modal('hide')
                  hit_view = new HITView collection: new HITs
                  $("#tables").html hit_view.render().el
                  updateExperimentStatus()
                error: (error) ->
                  console.log(error)
                  $('#expire-modal').modal('hide'))

        # Shutdown button
        $("#server_off").on "click", ->
          $('#server-off-modal').modal('show')
          $('#shutdownServerBtn').on "click", ->
            $('#server_status').css "color": "yellow"
            $.ajax
              url: '/shutdown_psiturk'
              type: "GET"
              success: $('#server-off-modal').modal('hide')

        # Server status
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

        @getExperimentStatus()

#  Filename: SidebarView.coffee
define [
        "backbone"
        'text!templates/aws-info.html'
        'text!templates/overview.html'
        'text!templates/hit-config.html'
        'text!templates/database.html'
        'text!templates/server-params.html'
        'text!templates/expt-info.html'
        'views/validators'
        'views/HITView'
        'models/HITModel'
        'collections/HITCollection'
      ],
      (
        Backbone
        AWSInfoTemplate
        OverviewTemplate
        HITConfigTemplate
        DatabaseTemplate
        ServerParamsTemplate
        ExptInfoTemplate
        Validators
        HITView
        HIT
        HITs
      ) ->

        # TODO(Jay): This module is getting heavy.
        # Refactor into separate, lighter modules, esp non-essential sidebar code
        # and repeated table refresh code
        class SideBarView extends Backbone.View

          verifyAWSLogin: ->
            $.when @options.config.fetch()
              .then =>
                key_id = @options.config.get("AWS Access").aws_access_key_id
                secret_key = @options.config.get("AWS Access").aws_secret_access_key
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
                  error: ->
                    console.log("aws verification failed")

          save: (event) ->
            # Prevent clicks from reloading page
            event.preventDefault()

            section = $(event.target).data 'section'
            inputData = {}
            configData = {}
            $.each($('#myform').serializeArray(), (i, field) ->
              inputData[field.name] = field.value)
            configData[section] = inputData
            @options.config.save configData

            # Load overview and change sidebar link
            $('li').removeClass 'selected'
            $('#overview').addClass 'selected'
            $.when @options.config.fetch(), @options.ataglance.fetch()
              .then(=>
                overview = _.template(OverviewTemplate,
                  input:
                    balance: @options.ataglance.get("balance")
                    debug: if @options.config.get("Server Parameters").debug is "True" then "checked" else ""
                    using_sandbox: if @options.config.get("HIT Configuration").using_sandbox is "True" then "checked" else "")
                $('#content').html(overview)
                # Load HIT table
                hit_view = new HITView collection: new HITs
                $("#tables").html hit_view.render().el
                saveSandbox = _.bind(@saveUsingSandboxState, @)
                $('input#using_sandbox').on "click", ->
                  saveSandbox()
                $('input#debug').on "click",  =>
                  @saveDebugState())
            $.ajax
              url: "/monitor_server"

            @render()

          pushstateClick: (event) ->
            event.preventDefault()

          events:
            'click a': 'pushstateClick'
            'click .save_data': 'save'
            'click #aws-info-save': 'save'
            'click #server-parms-save': 'serverParamsSave'
            'click input#debug': 'saveDebugState'
            'click input#using_sandbox': 'saveUsingSandboxState'

          serverParamsSave: ->
            @save()
            # Update server on save
            configResetPromise = @options.config.fetch()
            configResetPromise.done(->
              url = @options.config.get("HIT Configuration").question_url + '/shutdown'
              url_pattern =  /^https?\:\/\/([^\/:?#]+)(?:[\/:?#]|$)/i
              domain = url.match(url_pattern)[0] + @options.config.get("Server Parameters").port + '/shutdown'
              $.ajax
                url: domain
                type: "GET"
                data: {hash: @options.config.get("Server Parameters").hash})

          saveDebugState: ->
            debug = $("input#debug").is(':checked')
            @options.config.save 
              "Server Parameters":
                debug: debug

          saveUsingSandboxState: ->
            using_sandbox = $("input#using_sandbox").is(':checked')
            @options.config.save(
              "HIT Configuration":
                using_sandbox: using_sandbox,
              {
                complete: =>
                  $.when @options.config.fetch(), @options.ataglance.fetch()
                    .done(=>
                      overview = _.template(OverviewTemplate,
                        input:
                          balance: @options.ataglance.get("balance")
                          debug: if @options.config.get("Server Parameters").debug is "True" then "checked" else ""
                          using_sandbox: if @options.config.get("HIT Configuration").using_sandbox is "True" then "checked" else "")
                      $('#content').html(overview)
                      # Load HIT table
                      hit_view = new HITView collection: new HITs
                      $("#tables").html hit_view.render().el
                      saveSandbox = _.bind(@saveUsingSandboxState, @)
                      $('input#using_sandbox').on "click", ->
                        saveSandbox())
              }, {
                error: (error) => console.log "error"
              })

          initialize: ->
            @render()
            @verifyAWSLogin()

          getCredentials: ->
            $('#aws-info-modal').modal('show')
            $('.save').click (event) =>
              event.preventDefault()
              @save(event)
              $('#aws-info-modal').modal('hide')

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

          loadOverview: ->
            #configOverviewPromise = @options.config.fetch()
            $.when @options.config.fetch(), @options.ataglance.fetch()
              .then(=>
                overview = _.template(OverviewTemplate,
                  input:
                    balance: @options.ataglance.get("balance")
                    debug: if @options.config.get("Server Parameters").debug is "True" then "checked" else ""
                    using_sandbox: if @options.config.get("HIT Configuration").using_sandbox is "True" then "checked" else "")
                $('#content').html(overview)
                # Load HIT table
                hit_view = new HITView collection: new HITs
                $("#tables").html hit_view.render().el
                saveSandbox = _.bind(@saveUsingSandboxState, @)
                $('input#using_sandbox').on "click", ->
                  saveSandbox()
                $('input#debug').on "click",  =>
                  @saveDebugState())


          render: =>
            # Highlight sidebar selections on click
            $('li').on 'click', ->
              $('li').removeClass 'selected'
              $(@).addClass 'selected'

            $('#shutdown-dashboard').on 'click', =>
              $.ajax
                url: '/shutdown'
                type: "GET"
                complete: ->
                  window.location.replace "http://nyuccl.github.io/psiTurk/"

            # Load content
            $.when @options.config.fetch(), @options.ataglance.fetch()
              .done =>

                # Load and add config content pages
                awsInfo = _.template(AWSInfoTemplate,
                  input:
                    aws_access_key_id: @options.config.get("AWS Access").aws_access_key_id
                    aws_secret_access_key: @options.config.get("AWS Access").aws_secret_access_key)
                hitConfig = _.template(HITConfigTemplate,
                  input:
                    title: @options.config.get("HIT Configuration").title
                    description: @options.config.get("HIT Configuration").description
                    keywords: @options.config.get("HIT Configuration").keywords
                    question_url: @options.config.get("HIT Configuration").question_url
                    max_assignments: @options.config.get("HIT Configuration").max_assignments
                    hit_lifetime: @options.config.get("HIT Configuration").hit_lifetime
                    reward: @options.config.get("HIT Configuration").reward
                    duration: @options.config.get("HIT Configuration").duration
                    us_only: @options.config.get("HIT Configuration").us_only
                    approve_requirement: @options.config.get("HIT Configuration").approve_requirement
                    using_sandbox: @options.config.get("HIT Configuration").using_sandbox)
                database = _.template(DatabaseTemplate,
                  input:
                    database_url: @options.config.get("Database Parameters").database_url
                    table_name: @options.config.get("Database Parameters").table_name)
                serverParams = _.template(ServerParamsTemplate,
                  input:
                    host: @options.config.get("Server Parameters").host
                    port: @options.config.get("Server Parameters").port
                    cutoff_time: @options.config.get("Server Parameters").cutoff_time
                    support_ie: @options.config.get("Server Parameters").support_ie)
                exptInfo = _.template(ExptInfoTemplate,
                  input:
                    code_version: @options.config.get("Task Parameters").code_version,
                    num_conds: @options.config.get("Task Parameters").num_conds,
                    num_counters: @options.config.get("Task Parameters").num_counters)

                # Have content area respond to sidebar link clicks
                validator = new Validators
                saveConfig = _.bind(@save, @)
                $('#overview').off('click').on 'click', =>
                  $('li').removeClass 'selected'
                  $('#overview').addClass 'selected'
                  @loadOverview()
                    # @options.chart.refresh())
                $('#aws-info').on 'click', ->
                  $('#content').html(awsInfo)
                  validator.loadValidators()
                  $('#myform').submit(false)
                  $('.save').on "click", (event) ->
                    event.preventDefault()
                    saveConfig(event)
                $('#hit-config').on 'click', ->
                  $('#content').html(hitConfig)
                  validator.loadValidators()
                  $('#myform').submit(false)
                  #$(document).on "click", '.save', (event) ->
                  $('.save').on "click", (event) ->
                    # event.preventDefault()
                    saveConfig(event)
                    # @save(event)
                $('#database').on 'click', ->
                  $('#content').html(database)
                  validator.loadValidators()
                  $('#myform').submit(false)
                  $('.save').on "click", (event) ->
                    event.preventDefault()
                    saveConfig(event)
                $('#server-params').on 'click', ->
                  $('#content').html(serverParams)
                  validator.loadValidators()
                  $('#myform').submit(false)
                  $('.save').on "click", (event) ->
                    event.preventDefault()
                    saveConfig(event)
                $('#expt-info').on 'click', ->
                  $('#content').html(exptInfo)
                  validator.loadValidators()
                  $('#myform').submit(false)
                  $('.save').on "click", (event) ->
                    event.preventDefault()
                    saveConfig(event)
                $('#contribute').on 'click', ->
                  window.open('https://github.com/NYUCCL/psiTurk')

            # Load and initialize HIT table
            hit_view = new HITView collection: new HITs
            $("#tables").html hit_view.render().el

            # TODO(): Figure out why backbone.events are not firing when triggered.
            # These are just a temporary hack around the issue.

            # $(document).on "click", '.save', (event) =>
            #   event.preventDefault()
            #   @save(event)

            saveSandbox = _.bind(@saveUsingSandboxState, @)
            saveConfig = _.bind(@save, @)
            #$('.save').on "click", (event) ->
            $(document).on "click", '.save', =>
              event.preventDefault()
              console.log('hi')
              saveConfig(event)
              $(document).on "click", '.save_data', (event) =>
                event.preventDefault()
                saveConfig(event)
            $('input#using_sandbox').on "click", ->
              saveSandbox()
            $('input#debug').on "click",  =>
              @saveDebugState()
            $(document).off("click").on "click", '#aws-info-save', =>
              @verifyAWSLogin()
            $(document).on "click", '#server-parms-save', =>
              @serverParamsSave()

            updateExperimentStatus = _.bind(@getExperimentStatus, @)
            updateOverview = _.bind(@loadOverview, @)

            # Bind table buttons
            $(document).on "click", '.expire', ->
              $('#expire-modal').modal('show')
              data = JSON.stringify
                mturk_request: "expire_hit"
                hitid: $(@).attr('id')
              $('#expire-btn').on 'click', ->
                $.ajax
                  contentType: "application/json; charset=utf-8"
                  url: '/mturk_services'
                  type: "POST"
                  dataType: 'json'
                  data: data
                  complete: ->
                    updateExperimentStatus()
                    updateOverview()
                  error: (error) ->
                    console.log("failed to expire HITJ")
                $('#expire-modal').modal('hide')

            $(document).on "click", '.extend', ->
              hitid = $(@).attr('id')
              $('#extend-modal').modal('show')
              $('#extend-btn').on 'click', ->
                data = JSON.stringify
                  mturk_request: "extend_hit"
                  hitid: hitid
                  assignments_increment: $('#extend-workers').val()
                  expiration_increment: $('#extend-time').val()
                $.ajax
                  contentType: "application/json; charset=utf-8"
                  url: '/mturk_services'
                  type: "POST"
                  dataType: 'json'
                  data: data
                  complete: ->
                    $('#extend-modal').modal('hide')
                    updateExperimentStatus()
                    updateOverview()
                  error: (error) ->
                    console.log("failed to extend HIT")

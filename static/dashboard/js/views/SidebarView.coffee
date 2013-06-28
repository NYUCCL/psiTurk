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
                $("#tables").html hit_view.render().el)

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
                      $("#tables").html hit_view.render().el)
              }, {
                error: (error) => console.log "error"
              })

          initialize: ->
            @render()

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
                $("#tables").html hit_view.render().el)

          render: =>
            # Highlight sidebar selections on click
            $('li').on 'click', ->
              $('li').removeClass 'selected'
              $(@).addClass 'selected'

            # Load content
            $.when @options.config.fetch(), @options.ataglance.fetch()
              .done(=>
                if @options.config.get("AWS Access").aws_access_key_id is "YourAccessKeyId" or @options.config.get("AWS Access").aws_secret_access_key is "YourSecretAccessKey"
                  @getCredentials()

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
              $('#overview').off('click').on 'click', =>
                $('li').removeClass 'selected'
                $('#overview').addClass 'selected'
                @loadOverview()
                  # @options.chart.refresh())
              $('#aws-info').on 'click', ->
                $('#content').html(awsInfo)
                validator.loadValidators()
              $('#hit-config').on 'click', ->
                $('#content').html(hitConfig)
                validator.loadValidators()
              $('#database').on 'click', ->
                $('#content').html(database)
                validator.loadValidators()
              $('#server-params').on 'click', ->
                $('#content').html(serverParams)
                validator.loadValidators()
              $('#expt-info').on 'click', ->
                $('#content').html(exptInfo)
                validator.loadValidators()
            )


            # Load HIT table
            hit_view = new HITView collection: new HITs
            $("#tables").html hit_view.render().el

            # TODO(): Figure out why backbone.events are not firing when triggered.
            # These are just a temporary hack around the issue.

            # $(document).on "click", '.save', (event) =>
            #   # event.preventDefault()
            #   @save(event)
            $(document).on "click", '.save_data', (event) =>
              event.preventDefault()
              @save(event)
            $(document).on "click", 'input#using_sandbox', =>
              @saveUsingSandboxState()
            $(document).on "click", 'input#debug', =>
              @saveDebugState()
            $(document).on "click", '#aws-info-save', =>
              @save()
            $(document).on "click", '#server-parms-save', =>
              @serverParamsSave()

            updateExperimentStatus = _.bind(@getExperimentStatus, @)
            updateOverview = _.bind(@loadOverview, @)

            # Bind table buttons
            $(document).on "click", '.extend', ->
              "blah"
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
                    console.log("failed to update status")
                $('#expire-modal').modal('hide')

            $(document).on "click", '.extend', ->
              $('#extend-modal').modal('show')
              data = JSON.stringify
                mturk_request: "extend_hit"
                hitid: $(@).attr('id')
                # Get time + worker data via text fields
              $('#expire-btn').on 'click', ->
                $('#expire-modal').modal('hide')

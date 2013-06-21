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
      ) ->
        class SideBarView extends Backbone.View

          # el: $('#content')

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
            configPromise = @options.config.fetch
            configPromise.done(->
              overview = _.template(OverviewTemplate,
                input:
                  balance: @options.ataglance.get("balance")
                  debug: if @options.config.get("Server Parameters").debug is "True" then "checked" else ""
                  using_sandbox: if @options.config.get("HIT Configuration").using_sandbox is "True" then "checked" else "")
              $('#content').html(overview))

              # @options.chart.getData()

            $.ajax
              url: "/monitor_server"

            @render()

          pushstateClick: (event) ->
            event.preventDefault()

          events:
            'click a': 'pushstateClick'
            'click .save_data': 'save'
            'click #server-parms-save': 'serverParamsSave'
            'click input#debug': 'saveDebugState'
            'click input#using_sandbox': 'saveUsingSandboxState'
  
          serverParamsSave: ->
            @save()
            # Reset server on save
            configResetPromise = @options.config.fetch()
            configResetPromise.done(->
              url = @options.config.get("HIT Configuration").question_url + '/shutdown'
              url_pattern =  /^https?\:\/\/([^\/:?#]+)(?:[\/:?#]|$)/i
              console.log(@options.config.get("Server Parameters").port)
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
            @options.config.save
              "HIT Configuration":
                using_sandbox: using_sandbox

          initialize: ->
            @render()

          render: ->
            # Highlight sidebar selections on click
            $('li').on 'click', ->
              $('li').removeClass 'selected'
              $(@).addClass 'selected'

            $.when(@options.config.fetch(), @options.ataglance.fetch()).done(=>
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

              validator = new Validators
              # Have content area respond to sidebar link clicks
              $('#overview').on 'click', =>
                configOverviewPromise = @options.config.fetch()
                configOverviewPromise.done(=>
                  overview = _.template(OverviewTemplate,
                    input:
                      balance: @options.ataglance.get("balance")
                      debug: if @options.config.get("Server Parameters").debug is "True" then "checked" else ""
                      using_sandbox: if @options.config.get("HIT Configuration").using_sandbox is "True" then "checked" else "")
                  $('#content').html(overview)
                  @options.chart.refresh())
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



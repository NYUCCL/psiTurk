#  Filename: SidebarView.coffee
define [
        "backbone"
        'inspiritas'
        'text!templates/aws-info.html'
        'text!templates/overview.html'
        'text!templates/hit-config.html'
        'text!templates/database.html'
        'text!templates/server-params.html'
        'text!templates/expt-info.html'
      ],
      (
        Backbone
        Inspiritas
        AWSInfoTemplate
        OverviewTemplate
        HITConfigTemplate
        DatabaseTemplate
        HitConfigTemplate
        ExptInfoTemplate
      ) ->
        class SideBarView extends Backbone.View

          el: $('#content')

          save: (event) ->
            event.preventDefault()
            # Get section name of form posted
            section = $(event.target).data 'section'
            inputData = {}
            configData = {}
            $.each($('#myform').serializeArray(), (i, field) ->
              inputData[field.name] = field.value)
            configData[section] = inputData
            @options.config.save configData
            @render()

          pushstateClick: (event) ->
            event.preventDefault()

          events:
            'click a': 'pushstateClick'
            'click #save_data': 'save'

          initialize: ->
            @render()

          render: ->
            # Highlight sidebar selections on click
            $('li').on 'click', ->
              $('li').removeClass 'selected'
              $(@).addClass 'selected'

            # Load and add config content pages
            overview = _.template(OverviewTemplate)
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
            serverParams = _.template(HitConfigTemplate,
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

            # Have options respond to clicks
            $('#overview').on 'click', ->
              $('#content').html(overview)
              loadCharts()
            $('#aws-info').on 'click', ->
              $('#content').html(awsInfo)
            $('#hit-config').on 'click', ->
              $('#content').html(hitConfig)
            $('#database').on 'click', ->
              $('#content').html(database)
            $('#server-params').on 'click', ->
              $('#content').html(serverParams)
            $('#expt-info').on 'click', ->
              $('#content').html(exptInfo)


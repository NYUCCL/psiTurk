#  Filename: SidebarView.coffee
define [
        "backbone"
        'text!templates/aws-info.html'
        'text!templates/hit-config.html'
        'text!templates/database.html'
        'text!templates/server-params.html'
        'text!templates/expt-info.html'
        'views/validators'
        'views/RunExptView'
      ],
      (
        Backbone
        AWSInfoTemplate
        HITConfigTemplate
        DatabaseTemplate
        ServerParamsTemplate
        ExptInfoTemplate
        Validators
        RunExptView
      ) ->

        class SideBarView extends Backbone.View


          initialize: ->
            @render()


          saveAndRender: (id, generateTemplate) =>
            validator = new Validators  # Validates form fields
            $(id).on 'click', =>
              $('#content').html generateTemplate()
              validator.loadValidators()
              $('#myform').submit(false)
              $('.save').on "click", (event) =>
                @options.pubsub.trigger "save", event


          redirect: (id, url) =>
            $(id).on 'click', =>
              $('li').removeClass 'selected'
              $('#overview').addClass 'selected'
              @options.pubsub.trigger "loadOverview"
              window.open(url)


          render: =>
            # Highlight sidebar selections on click
            $('li').on 'click', ->
              $('li').removeClass 'selected'
              $(@).addClass 'selected'

            # Generate dynamic content from AMT data
            $.when @options.config.fetch(), @options.ataglance.fetch()
              .done =>
                # Load and add config content pages via dynamic templates
                awsInfo = =>
                  _.template(AWSInfoTemplate,
                    input:
                      aws_access_key_id: @options.config.get("AWS Access").aws_access_key_id
                      aws_secret_access_key: @options.config.get("AWS Access").aws_secret_access_key)
                hitConfig = =>
                  _.template(HITConfigTemplate,
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
                database = =>
                  _.template(DatabaseTemplate,
                    input:
                      database_url: @options.config.get("Database Parameters").database_url
                      table_name: @options.config.get("Database Parameters").table_name)
                serverParams = =>
                  _.template(ServerParamsTemplate,
                    input:
                      host: @options.config.get("Server Parameters").host
                      port: @options.config.get("Server Parameters").port
                      cutoff_time: @options.config.get("Server Parameters").cutoff_time
                      support_ie: @options.config.get("Server Parameters").support_ie)
                exptInfo = =>
                  _.template(ExptInfoTemplate,
                    input:
                      code_version: @options.config.get("Task Parameters").code_version,
                      num_conds: @options.config.get("Task Parameters").num_conds,
                      num_counters: @options.config.get("Task Parameters").num_counters)

                # Have content area respond to sidebar clicks
                $('#overview').off('click').on 'click', =>
                  $('li').removeClass 'selected'
                  $('#overview').addClass 'selected'
                  @options.pubsub.trigger "loadOverview"
                @saveAndRender('#aws-info', awsInfo)
                @saveAndRender('#hit-config', hitConfig)
                @saveAndRender('#database', database)
                @saveAndRender('#server-params', serverParams)
                @saveAndRender('#expt-info', exptInfo)
                @redirect('#documentation', 'https://github.com/NYUCCL/psiTurk/wiki')
                @redirect('#contribute', 'https://github.com/NYUCCL/psiTurk')

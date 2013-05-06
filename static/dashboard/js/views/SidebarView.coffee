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
          events:
            'click a' : 'pushstateClick'
            'click li' : 'pushstateClick'

          pushstateClick: (event) ->
            event.preventDefault()

          initialize: ->
            @render()

          render: ->
            # Highlight sidebar selections on click
            $('li').on 'click', ->
              $('li').removeClass 'selected'
              $(@).addClass 'selected'

            # Load and add options bar html
            awsInfo = _.template(AWSInfoTemplate)
            overview = _.template(OverviewTemplate)
            hitConfig = _.template(HITConfigTemplate)
            database = _.template(DatabaseTemplate)
            serverParams = _.template(HitConfigTemplate)
            exptInfo = _.template(ExptInfoTemplate)

            # Have options respond to clicks
            $('#overview').on 'click', ->
              $('#content').html(overview)
              loadCharts()
            $('#aws-info').on 'click', -> $('#content').html(awsInfo)
            $('#hit-config').on 'click', -> $('#content').html(hitConfig)
            $('#database').on 'click', -> $('#content').html(database)
            $('#server-params').on 'click', -> $('#content').html(serverParams)
            $('#expt-info').on 'click', -> $('#content').html(exptInfo)

        side_bar_view = new SideBarView

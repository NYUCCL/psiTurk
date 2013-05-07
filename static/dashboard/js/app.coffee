#  Filename: app.coffee
define [
      'jquery'
      'underscore'
      'backbone'
      'router'
      'models/ConfigModel'
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


        # Load and add content html
        overviewContentHTML = _.template(OverviewTemplate)
        $('#content').html(overviewContentHTML)

        # Load configuration file
        config = new ConfigModel

        # Load and add side bar html
        sideBarHTML = _.template(SideBarTemplate)
        $('#sidebar').html(sideBarHTML)
        sidebarView = new SidebarView({config: config})
        sidebarView.initialize()

        # Load content view after html; req's ids to be present
        contentView = new ContentView()
        contentView.initialize()

#  Filename: app.coffee
define [
      'jquery'
      'underscore'
      'backbone'
      'router'
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
      SidebarView
      ContentView
      OverviewTemplate
      SideBarTemplate
    ) ->
      initialize: ->
        #  Pass in our Router module and call it's initialize function
        Router.initialize()
        
        # Prevent links from reloading the page
        events:
          'click a' : 'pushstateClick'
          'click li' : 'pushstateClick'

        pushstateClick: (event) ->
          event.preventDefault()

        # Load and add content html
        overviewContent = _.template(OverviewTemplate)
        $('#content').html(overviewContent)

        # Load and add side bar html
        sideBar = _.template(SideBarTemplate)
        $('#sidebar').html(sideBar)
        SidebarView.initialize()

        # Load content view after html; req's ids to be present
        ContentView.initialize()

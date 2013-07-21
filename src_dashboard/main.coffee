# Filename: main.coffee

# Require.js allows us to configure shortcut alias
require.config
  paths:
    jquery: "libs/jquery"
    underscore: "libs/underscore"
    backbone: "libs/backbone"
    text: "libs/text"
    cs: "libs/cs"
    bootstrap: "libs/bootstrap"
    dropdown: "libs/bootstrap-dropdown"
    collapse: "libs/bootstrap-collapse"
    tab: "libs/bootstrap-tab"
    nod: "libs/nod"
    dotimeout: "libs/jquery.dotimeout.min"


  # Shim sets the configuration for third party scripts that are not AMD compatible
  shim:
    # Twitter Bootstrap jQuery plugins
    bootstrap: ["jquery"]
    dropdown: ["bootstrap"]
    collapse: ["bootstrap"]
    tab: ["bootstrap"]
    nod: ["jquery"]
    dotimeout: ["jquery"]
    backbone:
      deps: ["underscore", "jquery"]
      exports: "Backbone" #attaches "Backbone" to the window object

    underscore:
      exports: "_"

# end shim
require [
  "jquery"
  "app"
  "bootstrap"
  "dropdown"
  "collapse"
  "tab"
  "dotimeout",
  "nod"],
  (
    $
    App
    Bootstrap
    dropdown
    tab
  ) ->
    App.initialize()

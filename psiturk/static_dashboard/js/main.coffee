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
    highcharts: "libs/highcharts"
    exporting: "libs/exporting"
    dropdown: "libs/bootstrap-dropdown"
    collapse: "libs/bootstrap-collapse"
    nod: "libs/nod"
    dotimeout: "libs/jquery.dotimeout.min"


  # Shim sets the configuration for third party scripts that are not AMD compatible
  shim:

    # Twitter Bootstrap jQuery plugins
    bootstrap: ["jquery"]
    dropdown: ["bootstrap"]
    collapse: ["bootstrap"]
    highcharts:
      deps: ["jquery"]
      exports: "Highcharts" #attaches "Backbone" to the window object
    exporting:
      deps: ["highcharts"]
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
  "highcharts"
  "exporting"
  "bootstrap"
  "dropdown"
  "collapse"
  "dotimeout",
  "nod"],
  (
    $
    App
    Highcharts
    Exporting
  ) ->
    App.initialize()

// Filename: main.js

// Require.js allows us to configure shortcut alias
require.config({
  waitseconds: 10,
  paths: {
    jquery: 'dashboard/libs/jquery',
    underscore: 'dashboard/libs/underscore',
    backbone: 'dashboard/libs/backbone',
    text: 'dashboard/libs/text',
    cs: 'dashboard/libs/cs',
    bootstrap: 'dashboard/libs/bootstrap'
  },

  // Shim sets the configuration for third party scripts that are not AMD compatible
  shim: {
    // Twitter Bootstrap jQuery plugins
    "bootstrap": ["jquery"],
    "backbone": {
      "deps": ["underscore", "jquery"],
      "exports": "Backbone"  //attaches "Backbone" to the window object
    },
  } // end shim
});

require([
  // Load our app module and pass it to our definition function
  'app',
], function(App){
  // The "app" dependency is passed in as "App"
  App.initialize();
});


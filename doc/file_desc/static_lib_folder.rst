The `static/lib/` directory
===========================

This folder should contain all the external
Javascript libraries that are needed by your
project.  It is a good idea to actually include
copies of those libraries here instead of linking
to a CDN or other URL.  This was, far into the
future, someone can re-run your experiment without
have to hunt down an older version of the libraries
you used.  By default, the Stroop example
includes libraries for
`Backbone <http://backbonejs.org/>`__, `JQuery <http://jquery.com/>`__, `d3.js <http://d3js.org/>`__, and
`underscore.js <http://underscorejs.org/>`__.
These four are required for **psiTurk** to work
properly but you can add other lirbaries for customization
purposes.

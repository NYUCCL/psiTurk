.. _migrating:

Migrating from psiturk 2 to 3
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*Draft*

* psiTurk 3 only supports > python3.6
* starting with psiTurk 3, no Secure Ad Server is provided.

  See the documentation for using a cloud-hosted service such as Heroku,
  and for setting your own ad url in the config
* A new default tablename is used -- `assignments` instead of `turkdemo`
* a jinja "layout" is used for many of the bundled experiment pages
* A few of the config settings have been moved to new sections.
* `def regularpage` in experiment.py no longer calls render_template -- instead, it sends the file as-is.
  If you need a custom template to be rendered, then create a route for your template in `custom.py`, and
  call `render_template()` on it yourself.

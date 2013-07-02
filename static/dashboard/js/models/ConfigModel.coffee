#  Filename: models/ConfigModel.coffee
define [
    'underscore'
    'backbone'
  ], (_, Backbone) ->

    class ConfigModel extends Backbone.Model

      url: '/dashboard_model'

      defaults:
        "AWS Access":
          aws_access_key_id: "YourAccessKeyId"
          aws_secret_access_key: "YourSecreteAccessKey"
        "HIT Configuration":
          title: "Perceptual Reaction Time"
          description: "Make a series of perceptual judgments."
          keywords: "Perception, Psychology"
          question_url: "http://localhost:5001/mturk"
          max_assignments: 10
          hit_lifetime: 24
          reward: 1
          duration: 2
          us_only: true
          approve_requirement: 95
          using_sandbox: true
        "Database Parameters":
          database_url:  "sqlite:///participants.db"
          table_name: "turkdemo"
        "Server Parameters":
          host: "localhost"
          port: 5001
          cutoff_time: 30
          support_ie: true
          logfile: "server.log"
          loglevel: 2
          debug: true
          login_username: "examplename"
          login_pw: "examplepassword"
        "Task Parameters":
          code_version: 1.0
          num_conds: 1
          num_counters: 1

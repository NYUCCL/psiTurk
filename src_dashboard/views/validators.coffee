#  Filename: validators.coffee
define [
        "backbone"
      ],
      (
        Backbone
      ) ->
        class SideBarView extends Backbone.View
          loadValidators: ->
            metrics = [
              # AWS Info
              ['#aws_access_key_id', 'presence', 'Cannot be empty']
              ['#aws_secret_access_key', 'presence', 'Cannot be empty']
              # Database info
              ['#table_name', 'presence', 'Cannot be empty']
              ['#database_url', 'presence', 'Cannot be empty']
              # Server Config
              ['#host', 'presence', 'Cannot be empty']
              ['#port', 'presence', 'Cannot be empty']
              ['#port', ((port) ->
                    is_available= null
                    $.ajax
                      async: false
                      url: '/is_port_available'
                      type: "POST"
                      data: JSON.stringify port: port
                      contentType: "application/json; charset=utf-8"
                      dataType: "json"
                      success: (data) ->
                        if data.is_available is 1
                          is_available = true
                        else
                          is_available = false
                    return(is_available)),
                'Port unavailable']
              ['#port', 'between-num:1024:65535', 'Must be between 1024 and 65535']
              ['#port', 'presence', 'Cannot be empty']
              ['#cutoff_time', 'presence', 'Cannot be empty']
              ['#cutoff_time', ((x) -> x > 0), 'Must be positive']
              # HitConfig
              ['#title', 'presence', 'Cannot be empty']
              ['#description', 'presence', 'Cannot be empty']
              ['#keywords', 'presence', 'Cannot be empty']
              ['#question_url', 'presence', 'Cannot be empty']
              ['#max_assignments', 'presence', 'Cannot be empty']
              ['#max_assignments', 'integer', 'Must be a whole number']
              ['#max_assignments', ((x) -> x > 0), 'Must be non-negative']
              ['#hit_lifetime', ((x) -> x > 0) , 'Must be positive']
              ['#hit_lifetime', 'presence', 'Cannot be empty']
              ['#hit_lifetime', 'presence', 'Cannot be empty']
              ['#reward', 'presence', 'Cannot be empty']
              ['#reward', ((x) -> x >= 0) , 'Must be non-negative']
              ['#duration', 'presence', 'Cannot be empty']
              ['#duration', ((x) -> x > 0) , 'Must be positive']
              ['#approve_requirement', 'between-num:0:100', 'Must be between 0 and 100']
              ['#approve_requirement', 'presence', 'Cannot be empty']
            ]
            $("#myform").nod metrics

import { DatabaseView } from './dbview.js';
import { DatabaseFilters } from './dbfilter.js';

// The fields to be parsed from the returned HIT response
var ASSIGNMENT_FIELDS = {
    'workerId': {'title': 'Worker ID', 'type': 'string', 'style': {'width': '200px'}},
    'assignmentId': {'title': 'Assignment ID', 'type': 'string', 'style': {'width': '320px'}},
    'status': {'title': 'Status', 'type': 'string', 'style': {'width': '100px'}},
    'accept_time': {'title': 'Accepted On', 'type': 'date', 'style': {'width': '300px'}},
    'submit_time': {'title': 'Submitted On', 'type': 'date', 'style': {'width': '300px'}},
};

if (HIT_LOCAL) {
    ASSIGNMENT_FIELDS = {
        'workerId': {'title': 'Worker ID', 'type': 'string', 'style': {'width': '200px'}},
        'assignmentId': {'title': 'Assignment ID', 'type': 'string', 'style': {'width': '320px'}},
        'status': {'title': 'Status', 'type': 'string', 'style': {'width': '100px'}},
        'bonus': {'title': 'Bonus', 'type': 'dollar', 'style': {'width': '100px'}},
        'codeversion': {'title': 'Code#', 'type': 'string', 'style': {'width': '100px'}},
        'accept_time': {'title': 'Accepted On', 'type': 'date', 'style': {'width': '300px'}},
        'submit_time': {'title': 'Submitted On', 'type': 'date', 'style': {'width': '300px'}},
    };
}

class AssignmentsDBDisplay {

    // Create the assignments display with references to the HTML elements it will
    // use as a basis for controls and in which it will fill in the database.
    constructor(domelements) {
        this.DOM$ = domelements;
        this.db = undefined;  // Main assignment database handler
        this.assignmentSelected = false; // Is an assignment selected currently?
    }

    // Build the database views into their respective elmeents. There is one
    // for the main database and another for the sub-assignments view
    init() {
        this.dbfilters = new DatabaseFilters(this.DOM$, 
            ASSIGNMENT_FIELDS, this._filterChangeHandler.bind(this));
        this.db = new DatabaseView(this.DOM$, {
                'onSelect': this._assignmentSelectedHandler.bind(this)
            }, 'assignments', this.dbfilters);
        
        // Load the data
        this._loadAssignments(HIT_ID);
    }

    // Pulls the assignment data from the backend and loads it into the main database
    _loadAssignments(hitId) {
        $.ajax({
            type: 'POST',
            url: '/dashboard/api/assignments',
            data: JSON.stringify({
                hit_ids: [hitId],
                local: HIT_LOCAL
            }),
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            success: (data) => {
                if (data.success && data.data.length > 0) {
                    this.db.updateData(data.data, ASSIGNMENT_FIELDS);
                }
            },
            error: function(errorMsg) {
                alert(errorMsg);
                console.log(errorMsg);
            }
        });
    }

    _filterChangeHandler() {
        this.db.renderTable();
    }

    // Handler for assignment select
    _assignmentSelectedHandler(data) {
        $('#assignmentInfo_hitid').text(data['hitId']);
        $('#assignmentInfo_workerid').text(data['workerId']);
        $('#assignmentInfo_assignmentid').text(data['assignmentId']);
        $('#assignmentInfo_status').text(data['status']);
        $('#assignmentInfo_accepted').text(data['accept_time']);
        $('#assignmentInfo_submitted').text(data['submit_time']);

        if (HIT_LOCAL) {
            $('#assignmentInfo_bonus').text('$' + data['bonus'].toFixed(2));
        }
    }
}

// Populates the table view with HITs
$(window).on('load', function() {

     // Initialize the HIT display
     var disp = new AssignmentsDBDisplay({
        filters: $('#DBFilters'),
        display: $('#DBDisplay'),
    });
    disp.init();

    // Render material icons
    $('.material-icons').css('opacity','1');
});
import { DatabaseView } from './dbview.js';
import { DatabaseFilters } from './dbfilter.js';

// The fields to be parsed from the returned HIT response
var ASSIGNMENT_FIELDS = {
    'workerId': {'title': 'Worker ID', 'type': 'string', 'style': {'width': '200px'}},
    'assignmentId': {'title': 'Assignment ID', 'type': 'string', 'style': {'max-width': '150px'}},
    'status': {'title': 'Status', 'type': 'string', 'style': {'width': '100px'}},
    'accept_time': {'title': 'Accepted On', 'type': 'date', 'style': {'width': '300px'}},
    'submit_time': {'title': 'Submitted On', 'type': 'date', 'style': {'width': '300px'}},
};

// For a local hit, add code version and bonus, as well as data fields
if (HIT_LOCAL) {
    ASSIGNMENT_FIELDS = {
        'workerId': {'title': 'Worker ID', 'type': 'string', 'style': {'width': '200px'}},
        'assignmentId': {'title': 'Assignment ID', 'type': 'string', 'style': {'max-width': '150px'}},
        'status': {'title': 'Status', 'type': 'string', 'style': {'width': '100px'}},
        'bonus': {'title': 'Bonus', 'type': 'dollar', 'style': {'width': '100px'}},
        'codeversion': {'title': 'Code#', 'type': 'string', 'style': {'width': '100px'}},
        'accept_time': {'title': 'Accepted On', 'type': 'date', 'style': {'width': '300px'}},
        'submit_time': {'title': 'Submitted On', 'type': 'date', 'style': {'width': '300px'}},
    };

    var DATA_FIELDS = {
        'event_data': {
            'eventtype': {'title': 'Event Type', 'type': 'string', 'style': {'width': '200px'}},
            'value': {'title': 'Value', 'type': 'json', 'style': {'width': '200px'}},
            'interval': {'title': 'Interval', 'type': 'num', 'style': {'width': '100px'}}
        },
        'question_data': {
            'questionname': {'title': 'Question Name', 'type': 'string', 'style': {'width': '200px'}},
            'response': {'title': 'Response', 'type': 'json', 'style': {'width': '200px', 'max-width': '600px'}}
        },
        'trial_data': {
            'current_trial': {'title': 'Trial', 'type': 'num', 'style': {'width': '100px'}},
            'trialdata': {'title': 'Data', 'type': 'json', 'style': {'width': '200px', 'max-width': '600px'}},
            'dateTime': {'title': 'Time', 'type': 'date', 'style': {'width': '200px'}}
        }
    }
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

    // Reloads specific assignment data
    _reloadAssignments(assignment_ids) {
        $.ajax({
            type: 'POST',
            url: '/api/assignments',
            data: JSON.stringify({
                'assignments': assignment_ids,
                'local': HIT_LOCAL
            }),
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            success: (data) => {
                if (data.success) {
                    let updatedData = this.db.data;
                    data.data.forEach((el, _) => {
                        let i = updatedData.findIndex(o => o['assignment_id'] == el['assignment_id'])
                        updatedData[i] = el;
                    });
                    this.db.updateData(updatedData, ASSIGNMENT_FIELDS);
                }
            },
            error: function(errorMsg) {
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

        // Update approval / rejection buttons
        $('#approveOne').prop('disabled', !['Submitted', 'Rejected'].includes(data['status']));
        $('#rejectOne').prop('disabled', data['status'] != 'Submitted');
        $('#bonusOne').prop('disabled', !(data['bonus'] && data['bonus'] > 0 && ['Credited', 'Approved'].includes(data['status'])));

        if (HIT_LOCAL) {
            $('#assignmentInfo_bonus').text('$' + data['bonus'].toFixed(2));
            $('#downloadOneData').prop('disabled', !['Credited', 'Approved', 'Submitted', 'Rejected', 'Bonused'].includes(data['status']));
            $('#viewOneData').prop('disabled', !['Credited', 'Approved', 'Submitted', 'Rejected', 'Bonused'].includes(data['status']));
        } else {
            $('#assignmentInfo_bonus').text('No bonus data.');
        }
    }
}

class AssignmentWorkerDataDBDisplay {

    // Create the assignments worker data display
    constructor(domelements) {
        this.DOM$ = domelements;
        this.db = undefined;  // Main assignment database handler
        this.dataCache = {}; // { id: { questions, events, trials } }
    }

    // Build the database view, do not load with data yet.
    init() {
        this.db = new DatabaseView(this.DOM$, {
                'onSelect': function() {}
            }, 'workerdata');
    }

    // Loads a worker's data from the database into the cache
    _loadWorkerData(assignment_id, callback) {
        if (!(assignment_id in this.dataCache)) {
            $.ajax({
                type: 'POST',
                url: '/dashboard/api/assignments/data',
                data: JSON.stringify({
                    'assignments': [assignment_id]
                }),
                contentType: 'application/json; charset=utf-8',
                dataType: 'json',
                success: (data) => {
                    if (data.success) {
                        this.dataCache[assignment_id] = data.data[assignment_id];
                        callback();
                    }
                },
                error: function(errorMsg) {
                    console.log(errorMsg);
                }
            });
        } else {
            callback();
        }
    }

    // Loads the worker data from the cache into the database
    async displayWorkerData(assignment_id) {
        this._loadWorkerData(assignment_id, () => {
            let type = $('input[name="dataRadioOptions"]:checked').val();
            this.db.updateData(this.dataCache[assignment_id][type], DATA_FIELDS[type], true);
        });
    }
}

// Approves a single individual in the database
function approveIndividualHandler() {
    let assignment_id = $('#assignmentInfo_assignmentid').text();
    $.ajax({
        type: 'POST',
        url: '/dashboard/api/assignments/approve',
        data: JSON.stringify({
            'assignments': [assignment_id],
            'all_studies': !HIT_LOCAL
        }),
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        success: function(data) {
            if (data.success && data.data[0].success) {
                mainDisp._reloadAssignments([assignment_id]);
            } else {
                console.log(data);
            }
        },
        error: function(errorMsg) {
            console.log(errorMsg);
        }
    });
}

// Rejects a single individual in the database
function rejectIndividualHandler() {
    let assignment_id = $('#assignmentInfo_assignmentid').text();
    $.ajax({
        type: 'POST',
        url: '/dashboard/api/assignments/reject',
        data: JSON.stringify({
            'assignments': [assignment_id],
            'all_studies': !HIT_LOCAL
        }),
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        success: function(data) {
            if (data.success && data.data[0].success) {
                mainDisp._reloadAssignments([assignment_id]);
            } else {
                console.log(data);
            }
        },
        error: function(errorMsg) {
            console.log(errorMsg);
        }
    });
}

// Listens for modal showing and loads in worker data for an assignment
function viewWorkerDataHandler() {
    let assignment_id = $('#assignmentInfo_assignmentid').text();
    dataDisp.displayWorkerData(assignment_id);
}

// Populates the table view with assignments, loads handlers
var mainDisp;
var dataDisp;
$(window).on('load', function() {

    // Initialize the assignment display
    mainDisp = new AssignmentsDBDisplay({
        filters: $('#DBFilters'),
        display: $('#DBDisplay'),
    });
    mainDisp.init();

    // Initialize worker data display
    dataDisp = new AssignmentWorkerDataDBDisplay({
        display: $('#DataDBDisplay'),
    });
    dataDisp.init();

    // Listeners for moving with arrow keys
    $(document).keydown((e) => {
        if (e.which == 38) {
            mainDisp.db.selectPreviousRow();
        } else if (e.which == 40) {
            mainDisp.db.selectNextRow();
        }
    });

    // On view worker data request, load in the data
    $('#viewOneData').on('click', viewWorkerDataHandler);
    $('input[name="dataRadioOptions"]').on('change', viewWorkerDataHandler);

    // Approves/rejects/bonuses the currently selected assignment
    $('#approveOne').on('click', approveIndividualHandler);
    $('#rejectOne').on('click', rejectIndividualHandler);
});
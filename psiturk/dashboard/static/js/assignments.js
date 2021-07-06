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

// The fields to use in the approval HIT display
var APPROVE_FIELDS = {
    'workerId': {'title': 'Worker ID', 'type': 'string', 'style': {'width': '200px'}},
    'status': {'title': 'Status', 'type': 'string', 'style': {'width': '100px'}},
    'assignmentId': {'title': 'Assignment ID', 'type': 'string', 'style': {'width': '320px'}},
}

// The fields to use in the bonus HIT display
var BONUS_FIELDS = {
    'workerId': {'title': 'Worker ID', 'type': 'string', 'style': {'width': '200px'}},
    'bonus': {'title': 'Bonus', 'type': 'dollar', 'style': {'width': '100px'}},
    'status': {'title': 'Status', 'type': 'string', 'style': {'width': '100px'}},
    'assignmentId': {'title': 'Assignment ID', 'type': 'string', 'style': {'width': '320px'}},
}

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
            ASSIGNMENT_FIELDS, {
                onChange: this._filterChangeHandler.bind(this),
                onDownload: this._downloadTableHandler.bind(this)
            });
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
            url: '/api/assignments/',
            data: JSON.stringify({
                hit_ids: [hitId],
                local: HIT_LOCAL
            }),
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            success: (data) => {
                if (data.length > 0) {
                    this.db.updateData(data, ASSIGNMENT_FIELDS, {
                        'rerender': true,
                        'resetFilter': false,
                        'maintainSelected': false,
                        'index': 'assignmentId',
                        'callback': () => {
                            if (ASSIGNMENT_ID) {
                                $('#' + this.db.trPrefix + ASSIGNMENT_ID).click();
                            }
                        }
                    });
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
            url: '/api/assignments/',
            data: JSON.stringify({
                'assignment_ids': assignment_ids,
                'local': HIT_LOCAL
            }),
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            success: (data) => {
                let updatedData = this.db.data;
                data.forEach((el, _) => {
                    let i = updatedData.findIndex(o => o['assignmentId'] == el['assignmentId'])
                    updatedData[i] = el;
                });
                this.db.updateData(updatedData, ASSIGNMENT_FIELDS, {
                    'rerender': true,
                    'resetFilter': false,
                    'maintainSelected': true,
                    'index': 'assignmentId',
                    'callback': () => {}
                });
            },
            error: function(errorMsg) {
                console.log(errorMsg);
            }
        });
    }

    /**
     * HANDLER: Change in filters of main DB view
     */
    _filterChangeHandler() {
        this.db.renderTable();
    }

    /**
     * HANDLER: Download table
     */
    _downloadTableHandler() {
        this.db.downloadData('assignments_' + HIT_ID);
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
        $('#bonusOne').prop('disabled', !['Credited', 'Approved'].includes(data['status']));

        if (HIT_LOCAL) {
            $('#assignmentInfo_bonus').text('$' + data['bonus'].toFixed(2));
            $('#downloadOneData').prop('disabled', data['status'] == 'Allocated');
            $('#viewOneData').prop('disabled', data['status'] == 'Allocated');
            // Update the data download HREF
            if (data['status'] != 'Allocated') {
                $('#downloadOneDataHref').attr('href', '/api/assignments/action/datadownload?assignmentid=' + data['assignmentId']);
            } else {
                $('#downloadOneDataHref').removeAttr('href');
            }
        } else {
            $('#assignmentInfo_bonus').text('No bonus data.');
        }

        // Update the current HREF
        history.pushState({id: 'hitpage'}, '', window.location.origin + '/dashboard/hits/' + HIT_ID + '/assignments/' + data['assignmentId']);
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
                url: '/api/assignments/action/data',
                data: JSON.stringify({
                    'assignments': [assignment_id]
                }),
                contentType: 'application/json; charset=utf-8',
                dataType: 'json',
                success: (data) => {
                    this.dataCache[assignment_id] = data[assignment_id];
                    callback();
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
            this.db.updateData(this.dataCache[assignment_id][type], DATA_FIELDS[type], {
                'rerender': true,
                'resetFilter': false,
                'maintainSelected': false,
                'index': undefined,
                'callback': () => {}
            });
        });
    }
}

// Approves a list of assignment ids and then reloads them
function assignmentAPI(assignment_ids, endpoint, payload={}, callbacks={'success': () => {}, 'failure': () => {}}) {
    $.ajax({
        type: 'POST',
        url: '/api/assignments/action/' + endpoint,
        data: JSON.stringify({
            'assignments': assignment_ids,
            'all_studies': !HIT_LOCAL,
            ...payload
        }),
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        success: function(data) {
            if (data.every(el => !el.success)) {
                callbacks['failure']();
            } else {
                mainDisp._reloadAssignments(assignment_ids);
                callbacks['success']();
            }
        },
        error: function(errorMsg) {
            console.log(errorMsg);
            callbacks['failure']();
        }
    });
}

// Approves a single individual in the database
function approveIndividualHandler() {
    let assignment_id = $('#assignmentInfo_assignmentid').text();
    $('#approveOne').prop('disabled', true);
    $('#rejectOne').prop('disabled', true);
    assignmentAPI([assignment_id], 'approve', {}, {
        'success': () => {
            alert('Approval successful!');
        },
        'failure': () => {
            $('#approveOne').prop('disabled', false);
            $('#rejectOne').prop('disabled', false);
            alert('Approval unsuccessful');
        }
    });
}

// Approves all the individuals in the approval display
function approveAllHandler() {
    let assignment_ids = approvalDispView.getDisplayedData().map((el) => el['assignmentId']);
    $('#approval-submit').prop('disabled', true);
    assignmentAPI(assignment_ids, 'approve', {}, {
        'success': () => {
            $('#approveModal').modal('hide');
            $('#approval-submit').prop('disabled', false);
            alert('Approval successful!');
        },
        'failure': () => {
            $('#approval-submit').prop('disabled', false);
            alert('Approval unsuccessful.');
        }
    });
}

// Rejects a single individual in the database
function rejectIndividualHandler() {
    let assignment_id = $('#assignmentInfo_assignmentid').text();
    $('#approveOne').prop('disabled', true);
    $('#rejectOne').prop('disabled', true);
    assignmentAPI([assignment_id], 'reject', {}, {
        'success': () => {
            alert('Rejeection successful!');
        },
        'failure': () => {
            $('#approveOne').prop('disabled', false);
            $('#rejectOne').prop('disabled', false);
            alert('Rejection unsuccessful');
        }
    });
}

function bonusAllHandler() {
    let assignment_ids = bonusDispView.getDisplayedData().map((el) => el['assignmentId']);
    let amount = parseFloat($('#bonus-value').val());
    let reason = $('#bonus-reason').val();
    $('#bonus-submit').prop('disabled', true);
    assignmentAPI(assignment_ids, 'bonus', {
        'amount': amount,
        'reason': reason
    }, 
    {
        'success': () => {
            $('#bonusModal').modal('hide');
            $('#bonus-submit').prop('disabled', false);
            alert('Bonus successful!');
        },
        'failure': () => {
            $('#bonus-submit').prop('disabled', false);
            alert('Bonus unsuccessful');
        }
    })
}

// Opens the worker approval modal with the workers currently in the table
var approvalDispView;
function approveWorkersModal() {
    let assignments = mainDisp.db.getDisplayedData();
    assignments = assignments.filter(data => data['status'] == 'Submitted');
    if (!approvalDispView) {
        approvalDispView = new DatabaseView({display: $('#DBApprovalTable')});
    }
    approvalDispView.updateData(assignments, APPROVE_FIELDS);
    $('#numWorkersApproving').text(assignments.length);
    $('#approval-numWorkers').text(assignments.length);

    // MTurk fee is 20% for HITs with < 10 assignments, 40% for HITs with 10 or more
    let mturkfee = HIT_ASSIGNMENTS > 9 ? 0.4 : 0.2;
    let totalCost = HIT_REWARD * (1 + mturkfee) * assignments.length;
    $('#approval-mturkfee').text(100 * mturkfee);
    $('#approval-total').text(totalCost.toFixed(2));

    // If no workers, do not enable the approve
    if (assignments.length == 0) {
        $('#approval-submit').prop('disabled', true);
    } else {
        $('#approval-submit').prop('disabled', false);
    }
}

// Opens the worker bonus modal with the workers currently in the table
var bonusDispView;
function bonusWorkersModal() {
    let assignments = mainDisp.db.getDisplayedData();
    assignments = assignments.filter(data => ['Credited', 'Approved'].includes(data['status']));
    if (!bonusDispView) {
        bonusDispView = new DatabaseView({display: $('#DBBonusTable')});
    }
    bonusDispView.updateData(assignments, BONUS_FIELDS);
    $('#numWorkersBonusing').text(assignments.length);
    $('#bonus-numWorkers').text(assignments.length);

    // MTurk fee is 20% for HITs with < 10 assignments, 40% for HITs with 10 or more
    let mturkfee = HIT_ASSIGNMENTS > 9 ? 0.4 : 0.2;
    $('#bonus-mturkfee').text(100 * mturkfee);
    // $('#approval-total').text(totalCost.toFixed(2));
}
// Listens for modal showing and loads in worker data for an assignment
function viewWorkerDataHandler() {
    let assignment_id = $('#assignmentInfo_assignmentid').text();
    dataDisp.displayWorkerData(assignment_id);
    $('#workerDataAssignmentId').text(assignment_id);
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
    $('#downloadOneData').on('click', () => {
        // mainDisp._reloadAssignments(['3I3WADAZ9Q5QECKJM5NCXE9VS1X5OL']);
    });
    $('#viewOneData').on('click', viewWorkerDataHandler);
    $('input[name="dataRadioOptions"]').on('change', viewWorkerDataHandler);

    // Approves/rejects/bonuses the currently selected assignment
    $('#approveOne').on('click', approveIndividualHandler);
    $('#rejectOne').on('click', rejectIndividualHandler);
    $('#approval-submit').on('click', approveAllHandler);
    $('#bonus-submit').on('click', bonusAllHandler);

    // Approves/bonuses all the workers in the database showing
    $('#approveAll').on('click', approveWorkersModal);
    $('#bonusAll').on('click', bonusWorkersModal);
});
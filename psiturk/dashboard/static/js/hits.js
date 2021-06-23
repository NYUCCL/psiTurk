import { DatabaseView } from './dbview.js';
import { DatabaseFilters } from './dbfilter.js';

// The fields to be parsed from the returned HIT response
var HIT_FIELDS = {
    'local_hit': {'title': '<img src="' + BLUE_RIBBON_PATH + '" class="db-boolimg">', 'type': 'bool', 'style': {'width': '50px', 'max-width': '50px'}},
    'HITId': {'title': 'ID', 'type': 'string', 'style': {'width': '50px', 'max-width': '50px'}},
    'Title': {'title': 'Title', 'type': 'string', 'style': {'min-width': '100px', 'width': '20%', 'max-width': '200px'}},
    'HITStatus': {'title': 'Status', 'type': 'string', 'style': {'width': '100px'}},
    'Reward': {'title': 'Reward', 'type': 'string', 'style': {'width': '100px', 'max-width': '100px'}},
    'ToDoAssignments': {'title': 'TODO', 'type': 'num', 'style': {'width': '50px'}},
    'MaxAssignments': {'title': 'Max', 'type': 'num', 'style': {'width': '50px'}},
    'NumberOfAssignmentsAvailable': {'title': 'Available', 'type': 'num', 'style': {'width': '50px'}},
    'NumberOfAssignmentsCompleted': {'title': 'Completed', 'type': 'num', 'style': {'width': '50px'}},
    'NumberOfAssignmentsPending': {'title': 'Pending', 'type': 'num', 'style': {'width': '50px'}},
    'Description': {'title': 'Description', 'type': 'string', 'style': {'min-width': '100px', 'width': '20%', 'max-width': '200px'}},    
    'CreationTime': {'title': 'Created On', 'type': 'date', 'style': {'width': '300px'}},
    'Expiration': {'title': 'Expiration', 'type': 'date', 'style': {'width': '300px'}},
};

var HIT_STATUSES = ['Reviewable', 'Reviewing', 'Assignable', 'Unassignable'];

/**
 * Handles the database HIT views
 */
class HITDBDisplay {

    // Create the HIT display with references to the HTML elements it will
    // use as a basis for controls and in which it will fill in the database.
    constructor(domelements) {
        this.DOM$ = domelements;
        this.db = undefined;  // Main HIT database handler
    }

    // Build the database views into their respective elmeents. There is one
    // for the main database and another for the sub-assignments view
    init() {
        this.dbfilters = new DatabaseFilters(this.DOM$, 
            HIT_FIELDS, this._filterChangeHandler.bind(this));
        this.db = new DatabaseView(this.DOM$, {
                'onSelect': this._hitSelectedHandler.bind(this)
            }, 'hits', this.dbfilters);
        
        // Load the data
        this._loadHITs();
    }

    // Pulls the HIT data from the backend and loads it into the main database
    _loadHITs(statuses=HIT_STATUSES) {
        $.ajax({
            type: 'POST',
            url: '/dashboard/api/hits',
            data: JSON.stringify({'statuses': statuses}),
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            success: (data) => {
                if (data.success && data.data.length > 0) {
                    this.db.updateData(data.data, HIT_FIELDS, {
                        'rerender': true,
                        'resetFilter': false,
                        'maintainSelected': false,
                        'index': 'HITId',
                        'callback': () => {
                            if (HIT_ID) {
                                $('#' + this.db.trPrefix + HIT_ID).click();
                            }
                        }
                    });
                }
            },
            error: function(errorMsg) {
                console.log(errorMsg);
                // alert('Error loading HIT data.');
                // location.reload();
            }
        });
    }

    /**
     * HANDLER: New HIT is selected in the database view
     * @param {object} data - The data of the newly-selected HIT
     */
    _hitSelectedHandler(data) {
        // Enable the HIT assignment page
        $('#assignmentsPage').removeClass('disabled');

        // Update the HIT information column
        let hitId = data['HITId'];
        $('#hitInfo_id').text(hitId);
        $('#hitInfo_title').text(data['Title']);
        $('#hitInfo_desc').text(data['Description']);
        $('#hitInfo_status').text(data['HITStatus']);
        $('#hitInfo_reward').text('$' + data['Reward']);
        $('#hitInfo_created').text(data['CreationTime']);
        $('#hitInfo_expired').text(data['Expiration']);
        $('#hitInfo_todo').text(data['ToDoAssignments']);
        $('#hitInfo_max').text(data['MaxAssignments']);
        $('#hitInfo_available').text(data['NumberOfAssignmentsAvailable']);
        $('#hitInfo_completed').text(data['NumberOfAssignmentsCompleted']);
        $('#hitInfo_pending').text(data['NumberOfAssignmentsPending']);

        // Update the current HREF
        history.pushState({id: 'hitpage'}, '', window.location.origin + '/dashboard/hits/' + hitId + '/');
    }

    /**
     * HANDLER: Change in filters of main DB view
     */
    _filterChangeHandler() {
        this.db.renderTable();
    }
}


// Updates the HIT expenses based on the modal
function updateHITCreateExpense() {
    // Fee structure 07.22.15:
    // 20% for HITs with < 10 assignments
    // 40% for HITs with >= 10 assignments
    let assignments = parseInt($('#hitCreateInput-participants').val());
    let reward = parseFloat(parseFloat($('#hitCreateInput-reward').val()).toFixed(2));
    let work = assignments * reward;

    let commission = assignments >= 10 ? 0.4 : 0.2;
    let fee = work * commission;
    let total = fee + assignments * reward;

    // Update displays
    $('#hitCreate-mturkfee').html(fee.toFixed(2));
    $('#hitCreate-totalCost').html(total.toFixed(2));
}

// Creates an HIT. Dangerous to use this on live!
function createHIT() {
    let participants = parseInt($('#hitCreateInput-participants').val());
    let reward = parseFloat($('#hitCreateInput-reward').val());
    let duration = parseInt($('#hitCreateInput-duration').val());
    
    // Disables submitting the HIT twice
    $('#hitCreate-submit').prop('disabled', true);

    $.ajax({
        type: 'POST',
        url: '/dashboard/api/hits/create',
        data: JSON.stringify({
            "num_workers": participants,
            "reward": reward,
            "duration": duration
        }),
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        success: function() {
            alert('HIT was successfully created! If you don\'t see it in the database view, refresh.')
            $('#hitCreateModal').modal('hide');
            $('#hitCreate-submit').prop('disabled', false);

            // Reload the HIT data
            disp._loadHITs();
        },
        error: function() {
            alert('There was an error creating your HIT. Try again maybe? Also, check your qualifications.')
            $('#hitCreate-submit').prop('disabled', false);
        }
    })
}

// Generates a random 6-length ID for the debug link
function randomIdGenerator() {
    return Math.random().toString(36).substr(2, 6).toUpperCase();
 }

// Sets the hit debug URL link
function hitURLUpdate() {
    $('#hitDebug-URL').val(`${window.location.protocol}//${window.location.host}/pub?assignmentId=${$('#hitDebug-assignmentid').val()}&workerId=${$('#hitDebug-workerid').val()}&hitId=${$('#hitDebug-hitid').val()}&mode=debug`);
}

// Populates the table view with HITs
var disp;
$(window).on('load', function() {

    // Initialize the HIT display
    disp = new HITDBDisplay({
        filters: $('#DBFilters'),
        display: $('#DBDisplay'),
    });
    disp.init();

    // Listeners for moving with arrow keys
    $(document).keydown((e) => {
        if (e.which == 38) {
            disp.db.selectPreviousRow();
        } else if (e.which == 40) {
            disp.db.selectNextRow();
        }
    });

    // Add HIT creation expense calculation
    updateHITCreateExpense();
    $('#hitCreateInput-participants').on('change', updateHITCreateExpense);
    $('#hitCreateInput-reward').on('change', updateHITCreateExpense);

    // Add HIT creation function
    $('#hitCreate-submit').on('click', createHIT);

    // Handle debug link generation
    $('#hitDebug-hitidRandom').on('click', () => $('#hitDebug-hitid').val(randomIdGenerator()));
    $('#hitDebug-workeridRandom').on('click', () => $('#hitDebug-workerid').val('debug' + randomIdGenerator()));
    $('#hitDebug-assignmentidRandom').on('click', () => $('#hitDebug-assignmentid').val('debug' + randomIdGenerator()));
    $('#hitDebug-openURL').on('click', () => window.open($('#hitDebug-URL').val(), '_blank'));
    $('#hitDebug-copyURL').on('click', () => { $('#hitDebug-URL').select(); document.execCommand('copy'); });
    $('#hitDebug-hitid').val(randomIdGenerator());
    $('#hitDebug-workerid').val('debug' + randomIdGenerator());
    $('#hitDebug-assignmentid').val('debug' + randomIdGenerator());
    hitURLUpdate();
});
import { DatabaseView } from './dbview.js';
import { DatabaseFilters } from './dbfilter.js';

// The fields to be parsed from the returned HIT response
var HIT_FIELDS = {
    'local': {'title': '<img src="' + BLUE_RIBBON_PATH + '" class="db-boolimg">', 'type': 'bool', 'style': {'width': '50px', 'max-width': '50px'}},
    'HITId': {'title': 'ID', 'type': 'string', 'style': {'width': '50px', 'max-width': '50px'}},
    'Title': {'title': 'Title', 'type': 'string', 'style': {'min-width': '100px', 'width': '20%', 'max-width': '200px'}},
    'Description': {'title': 'Description', 'type': 'string', 'style': {'min-width': '100px', 'width': '20%', 'max-width': '200px'}},
    'HITStatus': {'title': 'Status', 'type': 'string', 'style': {'width': '100px'}},
    'MaxAssignments': {'title': 'Max', 'type': 'num', 'style': {'width': '50px'}},
    'NumberOfAssignmentsAvailable': {'title': 'Available', 'type': 'num', 'style': {'width': '50px'}},
    'NumberOfAssignmentsCompleted': {'title': 'Completed', 'type': 'num', 'style': {'width': '50px'}},
    'NumberOfAssignmentsPending': {'title': 'Pending', 'type': 'num', 'style': {'width': '50px'}},
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
        this.hitSelected = false; // Is an HIT selected currently?
    }

    // Build the database views into their respective elmeents. There is one
    // for the main database and another for the sub-assignments view
    init() {
        this.db = new DatabaseView(this.DOM$, {
                'onSelect': this._hitSelectedHandler.bind(this), 
                'onFilter': this._filterChangeHandler.bind(this)
            }, 'hits');
        this.dbfilters = new DatabaseFilters(this.DOM$, Object.values(HIT_FIELDS));
        
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
                    this.db.updateData(data.data, HIT_FIELDS).then(() => {
                        if (HIT_ID) {
                            let index = this.db.data.map(e => e['HITId']).indexOf(HIT_ID);
                            $('#row' + index).click();
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
        if (!this.hitSelected) {
            $('#hitSelected').css('display', 'flex');
            $('#noHITAlert').css('display', 'none');
            this.hitSelected = true;
        }

        // Update the HIT information column
        let hitId = data['HITId'];
        $('#hitInfo_id').text(hitId);
        $('#hitInfo_title').text(data['Title']);
        $('#hitInfo_desc').text(data['Description']);
        $('#hitInfo_status').text(data['HITStatus']);
        $('#hitInfo_created').text(data['CreationTime']);
        $('#hitInfo_expired').text(data['Expiration']);
        $('#hitInfo_max').text(data['MaxAssignments']);
        $('#hitInfo_available').text(data['NumberOfAssignmentsAvailable']);
        $('#hitInfo_completed').text(data['NumberOfAssignmentsCompleted']);

        // Update the current HREF
        history.pushState({id: 'hitpage'}, '', window.location.origin + '/dashboard/hits/' + hitId + '/');
    }

    /**
     * HANDLER: Change in filters of main DB view
     * @param {int} length - The number of rows showing post-filter
     */
    _filterChangeHandler(length) {
        $('#totalHITsFiltered').html(length.toString());
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
    
    $.ajax({
        type: 'POST',
        url: '/api/HITs/create',
        data: JSON.stringify({
            "num_workers": participants,
            "reward": reward,
            "duration": duration
        }),
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        success: function() {
            alert('HIT successfully created! You shall see it in the database if you refresh in a little bit.')
            $('#hitCreateModal').modal('hide');
        },
        error: function() {
            alert('There was an error creating your HIT. Try again maybe? Also, check your qualifications.')
        }
    })
}

// Populates the table view with HITs
$(window).on('load', function() {

    // Initialize the HIT display
    var disp = new HITDBDisplay({
        filters: $('#DBFilters'),
        display: $('#DBDisplay'),
    });
    disp.init();

    // Disable the navbar mode toggle until the HIT data is finished loading

    // // Add HIT creation expense calculation
    // updateHITCreateExpense();
    // $('#hitCreateInput-participants').on('change', updateHITCreateExpense);
    // $('#hitCreateInput-reward').on('change', updateHITCreateExpense);

    // // Add HIT creation function
    // $('#hitCreate-submit').on('click', createHIT);


    // TESTING

    // if (!($('.modal.in').length)) {
    //     $('.modal-dialog').css({
    //       top: 0,
    //       left: 0
    //     });
    // }
});
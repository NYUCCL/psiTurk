import { DatabaseView } from './dbview.js';
import { DatabaseFilters } from './dbfilter.js';

var WORKER_FIELDS = {
    'workerId': {'title': 'Worker ID', 'type': 'string', 'style': {'width': '200px'}},
    'assignmentId': {'title': 'Assignment ID', 'type': 'string', 'style': {'max-width': '150px'}},
    'status': {'title': 'Status', 'type': 'string', 'style': {'width': '100px'}},
    'bonus': {'title': 'Bonus', 'type': 'dollar', 'style': {'width': '100px'}},
    'codeversion': {'title': 'Code#', 'type': 'string', 'style': {'width': '100px'}},
    'accept_time': {'title': 'Accepted On', 'type': 'date', 'style': {'width': '300px'}},
    'submit_time': {'title': 'Submitted On', 'type': 'date', 'style': {'width': '300px'}},
};

class WorkerDBDisplay {

    // Create the worker display with references to the HTML elements it will
    // use as a basis for controls and in which it will fill in the database.
    constructor(domelements) {
        this.DOM$ = domelements;
        this.db = undefined;  // Main HIT database handler
    }

    // Build the database views into their respective elmeents. There is one
    // for the main database and another for the sub-assignments view
    init() {
        this.dbfilters = new DatabaseFilters(this.DOM$, 
            WORKER_FIELDS, this._filterChangeHandler.bind(this));
        this.db = new DatabaseView(this.DOM$, {
                'onSelect': this._workerSelectedHandler.bind(this)
            }, 'workers', this.dbfilters);
        
        // Load the data
        this._loadCampaigns();
    }

    // Pulls the campaign data from the backend and loads it into the main database
    _loadCampaigns() {
        $.ajax({
            type: 'POST',
            url: '/api/workers/',
            data: JSON.stringify({
                codeversion: 0
            }),
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            success: (data) => {
                this.db.updateData(data, WORKER_FIELDS, {
                    'rerender': true,
                    'resetFilter': false,
                    'maintainSelected': false,
                    'index': 'workerId',
                    'callback': () => {
                        if (WORKER_ID) {
                            $('#' + this.db.trPrefix + WORKER_ID).click();
                        }
                    }
                });
            },
            error: function(errorMsg) {
                console.log(errorMsg);
            }
        });
    }

    /**
     * HANDLER: New worker is selected in the database view
     * @param {object} data - The data of the newly-selected worker
     */
     _workerSelectedHandler(data) {

        let workerId = data['workerId'];
        $('#workerInfo_hitid').text(data['hitId']);
        $('#workerInfo_id').text(data['workerId']);
        $('#workerInfo_assignmentid').text(data['assignmentId']);
        $('#workerInfo_status').text(data['status']);
        $('#workerInfo_accepted').text(data['accept_time']);
        $('#workerInfo_submitted').text(data['submit_time']);
        $('#workerInfo_bonus').text('$' + parseFloat(data['bonus']).toFixed(2));
        $('#workerInfo_codeVersion').text(data['codeversion']);

        // Update the current HREF
        history.pushState({id: 'hitpage'}, '', window.location.origin + '/dashboard/workers/' + workerId + '/');
    }

    /**
     * HANDLER: Change in filters of main DB view
     */
     _filterChangeHandler() {
        this.db.renderTable();
    }
}

// Populates the table view with HITs
var disp;
$(window).on('load', function() {

    // Initialize the HIT display
    disp = new WorkerDBDisplay({
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
});
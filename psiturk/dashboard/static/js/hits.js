import { DatabaseView, DatabaseViewWithFilters } from './dbview.js';

// The fields to be parsed from the returned HIT response
var HIT_FIELDS = {
    'local': {'title': '<img src="' + BLUE_RIBBON_PATH + '" class="db-boolimg">', 'type': 'bool', 'style': {'width': '50px', 'max-width': '50px'}},
    'Title': {'title': 'Title', 'type': 'string', 'style': {'min-width': '100px', 'width': '20%', 'max-width': '300px'}},
    'Description': {'title': 'Description', 'type': 'string', 'style': {'min-width': '100px', 'width': '20%', 'max-width': '300px'}},
    'HITId': {'title': 'ID', 'type': 'string', 'style': {'width': '50px', 'max-width': '50px'}},
    'HITStatus': {'title': 'Status', 'type': 'string', 'style': {'width': '100px'}},
    'MaxAssignments': {'title': 'Max', 'type': 'num', 'style': {'width': '50px'}},
    'NumberOfAssignmentsAvailable': {'title': 'Available', 'type': 'num', 'style': {'width': '50px'}},
    'NumberOfAssignmentsCompleted': {'title': 'Completed', 'type': 'num', 'style': {'width': '50px'}},
    'NumberOfAssignmentsPending': {'title': 'Pending', 'type': 'num', 'style': {'width': '50px'}},
    'CreationTime': {'title': 'Created On', 'type': 'date', 'style': {'width': '300px'}},
    'Expiration': {'title': 'Expiration', 'type': 'date', 'style': {'width': '300px'}},
};

var ASSIGNMENT_FIELDS = {
    'WorkerId': {'title': 'Worker ID', 'type': 'string', 'style': {'width': '200px'}},
    'AssignmentId': {'title': 'Assignment ID', 'type': 'string', 'style': {'width': '320px'}},
    'AssignmentStatus': {'title': 'Status', 'type': 'string', 'style': {'width': '100px'}},
    'AcceptTime': {'title': 'Accepted On', 'type': 'date', 'style': {'width': '300px'}},
    'SubmitTime': {'title': 'Submitted On', 'type': 'date', 'style': {'width': '300px'}},
    'ApprovalTime': {'title': 'Approved On', 'type': 'date', 'style': {'width': '300px'}},
};

// Database view for rendering the HIT
var MainDBView = new DatabaseViewWithFilters('mainDisplay', {'onSelect': onHITSelectedChange, 'onFilter': onFilterChange}, 'hits');

// Sub-database view for rendering any HIT's assignments
var cachedAssignments = {}
var SubDBView = new DatabaseView('assignmentDisplay', {'onSelect': console.log}, 'assignments');

// Loads the HITs from the backend
function loadHITs(statuses=[]) {
    $.ajax({
        type: 'POST',
        url: '/dashboard/api/hits',
        data: JSON.stringify({'statuses': statuses}),
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        headers: {
            'Authorization': 'Basic ' + btoa(USERNAME + ':' + PASSWORD)
        },
        success: function(data) {
            if (data.success && data.data.length > 0) {
                MainDBView.updateData(data.data, HIT_FIELDS).then(() => {
                    if (HITId) {
                        let index = MainDBView.data.map(e => e['HITId']).indexOf(HITId);
                        $('#row' + index).click();
                    }
                });
            }
        },
        error: function(errorMsg) {
            alert(errorMsg);
        }
    });
}

// Updates the HIT display with the data of the currently-clicked element
var displayingHIT = false;
function onHITSelectedChange(data) {
    if (!displayingHIT) {
        $('#hitSelected').css('display', 'flex');
        $('#noHITAlert').css('display', 'none');
        displayingHIT = true;
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


    // Load in the assignment data for that HIT if not already cached
    if (hitId in cachedAssignments) {
        SubDBView.updateData(cachedAssignments[hitId], ASSIGNMENT_FIELDS);
    } else {
        SubDBView.clearData();
        $.ajax({
            type: 'POST',
            url: '/dashboard/api/hits/' + hitId + '/assignments',
            data: "{}",
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            success: function(data) {
                if (data.success && data.data.length > 0) {
                    cachedAssignments[hitId] = data.data;
                    SubDBView.updateData(data.data, ASSIGNMENT_FIELDS);
                }
            },
            error: function(errorMsg) {
                alert(errorMsg);
            }
        })
    }
}

// Updates the query-row display with the number of rows filtered
function onFilterChange(length) {
    $('#totalHITsFiltered').html(length.toString());
}

// Batch downloads all the completed csv files from the server for the
// currently selected HIT (uses the ID span, so directly reflected in DOM)
function batchDownload() {
    
}

// Calculates the HIT creation expense from the values in the HIT create menu
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
    loadHITs(['Reviewable', 'Reviewing', 'Assignable', 'Unassignable']);

    // Add HIT creation expense calculation
    updateHITCreateExpense();
    $('#hitCreateInput-participants').on('change', updateHITCreateExpense);
    $('#hitCreateInput-reward').on('change', updateHITCreateExpense);

    // Add HIT creation function
    $('#hitCreate-submit').on('click', createHIT);
});
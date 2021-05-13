import { DatabaseViewWithFilters } from './web_databaseview.js';

// The fields to be parsed from the returned HIT response
var HIT_FIELDS = {
    'WorkerId': {'title': 'Worker ID', 'type': 'string', 'style': {'width': '200px'}},
    'AssignmentId': {'title': 'Assignment ID', 'type': 'string', 'style': {'width': '320px'}},
    'AssignmentStatus': {'title': 'Status', 'type': 'string', 'style': {'width': '100px'}},
    'AcceptTime': {'title': 'Accepted On', 'type': 'date', 'style': {'width': '300px'}},
    'SubmitTime': {'title': 'Submitted On', 'type': 'date', 'style': {'width': '300px'}},
    'ApprovalTime': {'title': 'Approved On', 'type': 'date', 'style': {'width': '300px'}},
};

// Database view for rendering the HIT
var MainDBView = new DatabaseViewWithFilters('mainDisplay', {'onSelect': selectAssignment}, 'assignments');

// Loads the workers from the backend
function loadAssignments(hitId) {
    $.ajax({
        type: 'POST',
        url: '/api/HITs/' + hitId + '/assignments',
        data: "{}",
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        headers: {
            'Authorization': 'Basic ' + btoa('michael:correcthorsebatterystaple')
        },
        success: function(data) {
            if (data.success && data.data.length > 0) {
                MainDBView.updateData(data.data, HIT_FIELDS);
            }
        },
        error: function(errorMsg) {
            alert(errorMsg);
        }
    });
}

// Updates the assignments display
var displayingAssignment = false;
function selectAssignment(data) {
    console.log(data);
}

// Populates the table view with HITs
$(window).on('load', function() {
    // Render material icons
    $('.material-icons').css('opacity','1');
    loadAssignments(HITId);
});
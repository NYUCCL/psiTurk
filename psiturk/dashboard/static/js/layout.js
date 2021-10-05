function modeSwitchListener() {
    let mode = $('#toggleLiveMode').prop('checked') ? 'live' : 'sandbox';
    let prev_state = $('#toggleLiveMode').prop('checked') ? 'off' : 'on';
    $('#toggleLiveMode').bootstrapToggle('disable');
    $.ajax({
        type: 'POST',
        url: '/dashboard/mode',
        data: JSON.stringify({mode: mode}),
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        success: function() {
            location.reload();
        },
        error: function(errorMessage) {
            alert('Error switching mode!');
            console.log(errorMessage);
            // reset it
            $('#toggleLiveMode').bootstrapToggle('enable');
            $('#toggleLiveMode').bootstrapToggle(prev_state, true);
        }
    });
}

$(window).on('load', function() {
    $('#toggleLiveMode').on('change', modeSwitchListener);
});

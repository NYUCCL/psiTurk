function modeSwitchListener() {
    let mode = $('#toggleLiveMode').prop('checked') ? 'live' : 'sandbox';
    $('#toggleLiveMode').attr('disabled', true);
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
            $('#toggleLiveMode').attr('disabled', false);
        }
    });
}

// On load, add listener to mode switch
$(window).on('load', function() {
    $('#toggleLiveMode').on('change', modeSwitchListener);
});
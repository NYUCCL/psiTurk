function modeSwitchListener() {
    let mode = $('#toggleLiveMode').prop('checked') ? 'live' : 'sandbox';
    $('#toggleLiveMode').attr('disabled', true);
    $.ajax({
        type: 'POST',
        url: '/api/services_manager',
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

function reloadAMTBalance() {
    $.ajax({
        type: 'GET',
        url: '/api/services_manager',
        success: function(data) {
            if (data.amt_balance) {
                $('#layout-amtbalance').text(data.amt_balance);
            } else {
                console.log('Could not get AMT balance!', data);
            }
        },
        error: function(errorMessage) {
            console.log(errorMessage);
        }
    })
}

// On load, add listener to mode switch
$(window).on('load', function() {
    $('#toggleLiveMode').on('change', modeSwitchListener);
});

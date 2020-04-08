odoo.define('lafilm_website_calendar.fullCalendar', function (require) {
    "use strict";

    var ajax = require('web.ajax');
    var output_data = '';
    var delayInMilliseconds = 1000;
    // var urlParams = new URLSearchParams(window.location.search);
    console.log(window.location);
    // var search = urlParams.get('search')
    ajax.jsonRpc('/slot_ids', 'call').then(function (data) {
        output_data = data['slot_lists'];
        console.log("----->>>", output_data);
        });


    $(document).ready(function() {
        console.log("output_data--->>", output_data);
        setTimeout(function() {
            $('#calendar').fullCalendar({
                header: {
                    left: 'prev,next today',
                    center: 'title',
                    right: 'agendaDay,agendaWeek,month'
                },
                defaultView: 'agendaDay',
                navLinks: true,
                eventLimit: false,
                events: output_data,
            });
        },5000);
    });
});


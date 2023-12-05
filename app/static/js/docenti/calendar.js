const page = {};

$(()=>{
   initCalendar();
});

function initCalendar() {
    let calendarEl = document.getElementById('calendar');
    page.calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        editable: true,
        events: '/api/appelli/?calendar=true',
        themeSystem: 'bootstrap',
        displayEventTime: false,
        headerToolbar: {
            right: 'today prev,next'
        }
    });
    page.calendar.render();
}

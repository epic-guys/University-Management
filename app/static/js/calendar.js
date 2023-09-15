var calendar = undefined;

document.addEventListener('DOMContentLoaded', function() {
        let calendarEl = document.getElementById('calendar');
        calendar = new FullCalendar.Calendar(calendarEl, {
          initialView: 'dayGridMonth',
            editable: true,
            events: '/api/appelli'
        });
        calendar.render();
      });


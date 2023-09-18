const NAMESPACE = {};

document.addEventListener('DOMContentLoaded', function() {
        let calendarEl = document.getElementById('calendar');
        NAMESPACE.calendar = new FullCalendar.Calendar(calendarEl, {
          initialView: 'dayGridMonth',
            editable: true,
            events: '/api/appelli'
        });
        NAMESPACE.calendar.render();
      });


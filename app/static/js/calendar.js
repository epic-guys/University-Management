 document.addEventListener('DOMContentLoaded', function() {
        var calendarEl = document.getElementById('calendar');
        var calendar = new FullCalendar.Calendar(calendarEl, {
          initialView: 'dayGridMonth',
            events: [
                {
                    title: 'Evento',
                    start: '2023-09-03',
                    end: '2023-09-05'
                }

            ]
        });
        calendar.render();
      });
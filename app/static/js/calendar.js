document.addEventListener('DOMContentLoaded', function() {
        var calendarEl = document.getElementById('calendar');
        var calendar = new FullCalendar.Calendar(calendarEl, {
          initialView: 'dayGridMonth',
            editable: true,
            events: [
                {
                    id: 'e1',
                    title: 'Esame di Basi di Dati',
                    start: '2023-09-03'
                }

            ]
        });
        calendar.render();
      });

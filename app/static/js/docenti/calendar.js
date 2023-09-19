const page = {};

document.addEventListener('DOMContentLoaded', function() {
        let calendarEl = document.getElementById('calendar');
        page.calendar = new FullCalendar.Calendar(calendarEl, {
          initialView: 'dayGridMonth',
            editable: true,
            events: '/api/appelli',
            themeSystem: 'bootstrapFontAwesome',
            customButtons: {
              addEventButton: {
                  text: '+',
                  click: function(){
                      $('#add-modal').modal('show');
                  }
              }
            },
            headerToolbar: {
              right: 'addEventButton today prev,next'
            }
        });
        page.calendar.render();
      });

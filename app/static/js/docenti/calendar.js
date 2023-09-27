const page = {};

$(()=>{
   initAddAppelli();
});

document.addEventListener('DOMContentLoaded', function() {
        let calendarEl = document.getElementById('calendar');
        page.calendar = new FullCalendar.Calendar(calendarEl, {
          initialView: 'dayGridMonth',
            editable: true,
            events: '/api/appelli',
            themeSystem: 'bootstrap',
            displayEventTime: false,
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
            },
            eventClick: function(event){
                // TODO popover sugli eventi
                alert('Hai premuto ' + event.title);
            }
        });
        page.calendar.render();
      });


//TODO rendere accessibili gli esami solo al docente del corso
function initAddAppelli(){
    $.ajax({
       url: '/api/esami',
        success: (esami) => {
            let options = [];
            for (const e of esami) {
                let option = $("<option>");
                option.attr("value", e.cod_esame);
                option.html(e.nome_corso);
                options.push(option);
            }
            $('#cod_esame').html(options);
        },
        error: () => {
            // TODO cambiare ovviamente, è solo per debug
            alert("Richiesta a corsi di laurea fallita");
        }
    });
}


function createAppello(){
    $.ajax({
        url: "/api/appelli",
        method: "POST",
        data: $("#add-form").serialize(),
        success: (res) => {
            page.calendar.refetchEvents();
        }
    })
}
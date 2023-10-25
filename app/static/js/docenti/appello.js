const page = {};

$(() => {
    initTable();
});


function initTable() {
    let voti = {
        "assente": 0,
        "insufficiente": 1,
        "ritirato": 2,

        /*
        * Fa confusione ma ecco una spiegazione.
        * Crea una lambda che si limita a creare un oggetto
        * che associa ogni numero a sé stesso.
        * Viene chiamata la lambda.
        * Poi l'operatore ... "spacchetta" l'oggetto e lo
        * inserisce in quello attuale.
        */
        ...(() => {
            let dict = {};
            for (let i = 18; i <= 31; i++) {
                dict[i.toString()] = i;
            }
            return dict;
        })()
    };
    page.studentiTable = $("#studenti-table").DataTable({
        columns: [
            {
                data: "studente.cognome",
                render: $.fn.dataTable.render.text()
            },
            {
                data: "studente.nome",
                render: $.fn.dataTable.render.text()
            },
            {
                data: "matricola",
                render: (data, type, row) => {
                    return $("<input>")
                        .attr("name", "matricola[]")
                        .attr("value", data)
                        .attr("readonly", "true")
                        .addClass("form-control-plaintext")
                        .prop("outerHTML");
                }
            },
            {
                data: "data_iscrizione",
                render: $.fn.dataTable.render.date()
            },
            {
                render: (data, type, row) => {
                    let select = $('<select>')
                        .addClass("form-control")
                        // TODO aggiungere name per abilitare form
                        // aggiungere anche value sulle opzioni
                        .attr("name", "");

                    // Se l'appello è in data futura, disattivo l'input
                    let appello_datetime = Date.parse($("#appello-datetime").val());
                    if (appello_datetime > Date.now()) {
                        select.attr("disabled", "true");
                    }

                    // Creo le opzioni
                    let options = [];
                    Object.entries(voti).forEach(
                        ([key, value]) => {
                        let opt = $("<option>")
                            .html(key)
                            .attr("name", value);
                        options.push(opt);
                    });

                    // Aggiungo le opzioni
                    select.html(options);
                    return select.prop("outerHTML");
                }
            }
        ],
        ajax: {
            url: "/api/appelli/" + $("#cod_appello").val() + "/iscrizioni"
        }
    });
}

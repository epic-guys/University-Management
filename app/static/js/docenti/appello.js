const page = {};

$(() => {
    page.appello_datetime = Date.parse($("#appello-datetime").val());
    page.editsEnabled = page.appello_datetime < Date.now();
    $("#insert-voti-btn").click(insertVoti);
    initTable();
});


function initTable() {
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
                    if (row.voto_appello != null) {
                        return data;
                    }

                    return $("<input>")
                        .attr("name", "matricola")
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
                    if (row.voto_appello != null) {
                        return row.voto_appello.voto;
                    }

                    let select = $('<select>')
                        .addClass("form-control voto-select");

                    // Se l'appello è in data futura, disattivo l'input
                    if (!page.editsEnabled) {
                        select.attr("disabled", "true");
                    }

                    // Creo le opzioni
                    let options = [];
                    Object.entries(votoString).forEach(
                        ([key, value]) => {
                        let opt = $("<option>")
                            .html(value)
                            .val(key);
                        options.push(opt);
                    });

                    // Voto non inserito
                    options.push($("<option>")
                        .html("-- Voto non inserito --")
                        .attr("value", "-1")
                        .attr("selected", "true")
                        .attr("disabled", "true")
                    );

                    // Aggiungo le opzioni
                    select.append(options);
                    return select.prop("outerHTML");
                }
            }
        ],
        ajax: {
            url: "/api/appelli/" + $("#cod_appello").val() + "/iscrizioni"
        }
    });
}

function insertVoti(eventObject) {
    let voti = [];
    page.studentiTable.rows().every((rowIdx, tableLoop, rowLoop) => {
        let row = page.studentiTable.row(rowIdx);
        let data = row.data();
        let voto = row.nodes().to$().find(".voto-select").val();
        if (voto != null && voto !== -1) {
            voti.push({
                "matricola": data.matricola,
                "voto": voto
            });
        }
    });

    if (voti.length === 0) {
        new Noty({
            text: "Nessun voto inserito",
            type: "warning",
            timeout: 3000
        }).show();
        return;
    }

    $.ajax({
        url: "/api/appelli/" + $("#cod_appello").val() + "/voti",
        method: "POST",
        data: JSON.stringify(voti),
        contentType: "application/json",
        success: () => {
            new Noty({
                text: "Voti inseriti con successo",
                type: "success",
                timeout: 3000
            }).show();
            location.reload();
        },
        error: (xhr, status, error) => {
            new Noty({
                text: "Errore: " + xhr.responseText,
                type: "error",
                timeout: 3000
            }).show();
        }
    });
}

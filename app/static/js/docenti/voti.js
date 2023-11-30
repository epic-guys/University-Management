const page = {};

$(() => {
    page.votiTableElement = $("#voti-table");
    page.params = new URLSearchParams(window.location.search);

    $("#insert-voti-btn").click(insertVoti);

    initTable();
});


function initTable(){
    page.votiTable = page.votiTableElement.DataTable({
        columns: [
            {
                data: "nome",
                render: $.fn.dataTable.render.text()
            },
            {
                data: "cognome",
                render: $.fn.dataTable.render.text()
            },
            {
                data: "matricola",
                render: $.fn.dataTable.render.text()
            },
            {
                render: (data, type, row) => {
                    // TODO controllare che studente non abbia già un voto

                    let select = $('<select>')
                        .addClass("form-control voto-select");


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
            url: "/api/esami/" + $("#cod_esame").val() + "/anni/" + $("#cod_anno_accademico").val() + "/idonei"
        }
    });
}

function insertVoti(eventObject) {
    let voti = [];
    page.votiTable.rows().every((rowIdx, tableLoop, rowLoop) => {
        let row = page.votiTable.row(rowIdx);
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
        url: "/api/esami/" + $("#cod_esame").val() + "/anni/" + $("#cod_anno_accademico").val() + "/voti",
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
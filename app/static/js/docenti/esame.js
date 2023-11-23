const page = {};

$(() => {
    page.tableElement = $("#prove-table");
    initAddProva();
    initTable();
});


function initTable() {
    page.table = page.tableElement.DataTable({
        columns: [
            {
                data: "cod_prova",
                render: $.fn.dataTable.render.text()
            },
            {
                data: "descrizione_prova",
                render: $.fn.dataTable.render.text()
            },
            {
                data: "tipo_prova",
                render: $.fn.dataTable.render.text()
            },
            {
                data: "scadenza",
                render: $.fn.dataTable.render.date()
            },
            {
                data: "peso",
                render: $.fn.dataTable.render.number(".", ",", 2)
            },
            {
                data: "cod_esame",
                render: $.fn.dataTable.render.text()
            },
            {
                data: "docente",
                // render: $.fn.dataTable.render.text()
                render: function (data, type, row) {
                    // FIXME XSS
                    return data.nome + " " + data.cognome;
                }
            },
            {
                render: function (data, type, row) {
                    return $("<a>")
                        .attr("class", "btn btn-primary")
                        .html(
                            $("<i>")
                                .attr("class", "fa-solid fa-eye")
                        )
                        .attr("href", "/docenti/prove/" + row.cod_prova)
                        .prop("outerHTML");
                },
                orderable: false
            }
        ],
        ajax: {
            url: "/api/esami/" + $("#cod-esame").val() + "/prove"
        }
    });
}


function initAddProva() {
    $.ajax({
        url: "/api/tipi-prova",
        success: (tipo) => {
            let options = [];
            for (const t of tipo) {
                let option = $("<option>");
                option.attr("value", t.tipo_prova);
                option.html(t.tipo_prova);
                options.push(option);
            }
            $('#tipo_prova').html(options);
        },
        error: () => {
            new Noty({
                type: "error",
                text: "Errore nel caricamento dei tipi di prova",
                timeout: 3000
            }).show();
        }
    });
}

function createProva(){

    $.ajax({
        url: "/api/esami",
        method: "POST",
        dataType: "json",
        contentType: "application/json",
        data: serializeForm($("#add-form")),
        success: (res) => {
            new Noty({
                type: "success",
                text: "Prova creata con successo",
                timeout: 3000
            }).show();
            page.table.ajax.reload();
        },
        error: (res) => {
            new Noty({
                type: "error",
                text: "Errore nella creazione della prova",
                timeout: 3000
            }).show();
        }
    })
}
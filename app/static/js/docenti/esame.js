const page = {};

$(() => {
    page.tableElement = $("#prove-table");
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
                        // FIXME potenziale XSS
                        .attr("href", "/docenti/prove/" + row.cod_prova)
                        .prop("outerHTML");
                },
                orderable: false
            }
        ],
        ajax: {
            url: "/api/esami/" + $("#cod-esame").html() + "/prove",
            dataSrc: ""
        },
        rowGroup: {
            dataSrc: "anno_accademico.cod_anno_accademico"
        }
    });
}


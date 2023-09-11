$(() => {
    $("#prove-table").DataTable({
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
                data: "cod_docente",
                render: $.fn.dataTable.render.text()
            }
        ],
        ajax: {
            url: "/api/esami/" + $("#cod-esame").html() + "/prove",
            dataSrc: ""
        }
    });

});
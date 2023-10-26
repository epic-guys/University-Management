const page = {};

$(() => {
    initTable();
});

function initTable() {
    page.esamiDataTable = $("#esami-table").DataTable({
        columns: [
            {
                data: "cod_esame",
                render: $.fn.dataTable.render.text()
            },
            {
                data: "nome_corso",
                render: $.fn.dataTable.render.text()
            },
            {
                data: "descrizione_corso",
                render: $.fn.dataTable.render.text()
            },
            {
                data: "anno",
                render: $.fn.dataTable.render.number()
            },
            {
                data: "cfu",
                render: $.fn.dataTable.render.number()
            },
            {
                data: "cod_corso_laurea",
                render: $.fn.dataTable.render.text()
            }

        ],
        ajax: {
            url: "/api/studenti/libretto"
        }
    });
}

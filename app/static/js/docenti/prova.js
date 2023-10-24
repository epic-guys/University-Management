
const page = {};

$(() => {
    page.tableElement = $("#appelli-table");
    initTable();
});


function initTable() {
    page.table = page.tableElement.DataTable({
        columns: [
            {
                data: "data_appello",
                render: $.fn.dataTable.render.date()
            },
            {
                data: "cod_appello",
                render: $.fn.dataTable.render.text()
            },
            {
                data: "aula",
                render: $.fn.dataTable.render.text()
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
                        .attr("href", "/docenti/appelli/" + row.cod_appello)
                        .prop("outerHTML");
                },
                orderable: false
            }

        ],
        ajax: {
            url: "/api/prove/" + $("#cod-prova").val() + "/appelli",
            dataSrc: ""
        },
        rowGroup: {
            dataSrc: "anno_accademico.cod_anno_accademico"
        }
    });
}

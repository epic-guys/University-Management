const page = {};

$(() => {
    page.tableElement = $("#voti-table");
    initTable();
});


function initTable(){
    page.tableElement = page.tableElement.DataTable({
        columns: [
            {
                data: "cod_appello",
                render: $.fn.dataTable.render.text()
            },
            {
                data: "matricola",
                render: $.fn.dataTable.render.text()
            },
            {
                data: "voto",
                render: $.fn.dataTable.render.number()
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
                        .attr("href", "/docenti/esami/" + row.cod_esame)
                        .prop("outerHTML");
                },
                orderable: false
            }
        ],
        ajax: {
            url: "/api/voti",
            dataSrc: ""
        }
    });
}
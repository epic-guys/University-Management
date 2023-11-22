const page = {};

$(() => {
    page.tableElement = $('#appelli-table');
    initTable();
});

function iscriviti(cod_appello, element) {
    $.ajax({
        url: "/api/appelli/" + cod_appello + "/iscrizioni",
        method: "POST",
        success: (res) => {
            console.log("Iscrizione effettuata");
            // Facendo così gli tolgo la classe btn-iscriviti che lo rende cliccabile
            element.attr("class", "btn btn-success");
            element.empty();
            element.append($("<i>").attr("class", "fa-solid fa-check"));
        },
        error: (res) => {
            console.log("Errore iscrizione");
            element.attr("class", "btn btn-danger");
            element.empty();
            element.append($("<i>").attr("class", "fa-solid fa-times"));
        }
    })
}

function initTable() {
    page.tableElement = page.tableElement.DataTable({
        columns: [
            {
                data: "cod_appello",
                render: $.fn.dataTable.render.text()
            },
            {
                data: "data_appello",
                render: $.fn.dataTable.render.datetime()
            },
            {
                data: "cod_prova",
                render: $.fn.dataTable.render.text()
            },
            {
                data: "aula",
                render: $.fn.dataTable.render.text()
            },
            {
                render: function (data, type, row) {


                    let elem = $("<a>")
                        .attr("class", "btn btn-primary btn-iscriviti")
                        .attr("href", "#")
                        .html(
                            $("<i>")
                                .attr("class", "fa-solid fa-plus")
                        )
                        // FIXME potenziale XSS
                        .on("click", function (e) {
                            e.preventDefault(); // Per evitare il comportamento predefinito del link
                            iscriviti(row.cod_appello);
                        })
                        .prop("outerHTML")
                    return elem;
                },
                orderable: false
            }
        ],
        ajax: {
            url: "/api/appelli/info",
            dataSrc: ""
        }
    });
    page.tableElement.on('click', '.btn-iscriviti', function (eventObject) {
        eventObject.preventDefault();
        obj = $(eventObject.target);
        console.log(obj);
        obj.empty();
        obj.append($("<i>").attr("class", "fa-solid fa-spinner fa-spin"));
        let row = page.tableElement.row($(this).parents('tr')).data();
        iscriviti(row.cod_appello, obj);
    });
}

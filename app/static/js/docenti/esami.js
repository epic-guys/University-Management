const page = {};


$(() => {
    page.tableElement = $("#esami-table");
    initAddEsame();
    initTable();
});


function initAddEsame() {
    $.ajax({
        url: "/api/corsi_laurea",
        success: (corsi) => {
            $('#cod_corso_laurea').empty();
            let options = [];
            for (const c of corsi) {
                let option = $("<option>");
                option.attr("value", c.cod_corso_laurea);
                option.html(c.nome_corso_laurea);
                options.push(option);
            }
            $('#cod_corso_laurea').append(options);
        },
        error: () => {
            new Noty({
                text: "Errore nel caricamento dei corsi di laurea",
                type: "error",
                timeout: 3000
            }).show();
        }
    });
}


function initTable() {
    page.tableElement = page.tableElement.DataTable({
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
            },
            {
                render: function (data, type, row) {
                    return $("<a>")
                        .attr("class", "btn btn-primary")
                        .html(
                            $("<i>")
                                .attr("class", "fa-solid fa-eye")
                        )
                        .attr("href", "/docenti/esami/" + row.cod_esame)
                        .prop("outerHTML");
                },
                orderable: false
            }
        ],
        ajax: {
            url: "/api/esami"
        }
    });
}


function createEsame() {
    $.ajax({
        url: "/api/esami",
        method: "POST",
        data: $("#add-form").serialize(),
        success: (res) => {
            page.table.ajax.reload();
            new Noty({
                text: "Esame creato con successo",
                type: "success",
                timeout: 3000
            }).show();
        },
        error: (res) => {
            new Noty({
                text: "Errore nella creazione dell'esame",
                type: "error",
                timeout: 3000
            }).show();
        }
    })
}

function resetEsame() {
    $("#add-form").trigger("reset");
}

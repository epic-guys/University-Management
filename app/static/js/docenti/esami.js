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
            let options = [];
            for (const c of corsi) {
                let option = $("<option>");
                option.attr("value", c.cod_corso_laurea);
                option.html(c.nome_corso_laurea);
                options.push(option);
            }
            $('#cod_corso_laurea').html(options);
        },
        error: () => {
            // TODO cambiare ovviamente, è solo per debug
            alert("Richiesta a corsi di laurea fallita");
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
                        // FIXME potenziale XSS
                        .attr("href", "/docenti/esami/" + row.cod_esame)
                        .prop("outerHTML");
                },
                orderable: false
            }
        ],
        ajax: {
            url: "/api/esami",
            dataSrc: ""
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
        }
    })
}

function resetEsame() {
    $("#add-form").trigger("reset");
}

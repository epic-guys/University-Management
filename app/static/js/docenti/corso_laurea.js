const page = {};


$(() => {
    page.tableElement = $("#esami-table");
    initCreateEsame();
    initAddEsame();
    initTable();
});


function initCreateEsame() {
    $("#create-esame-btn").on("click", createEsame);
}

function initAddEsame() {

}

function initTable() {
    page.table = page.tableElement.DataTable({
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
            url: "/api/corso_laurea/" + $("#cod-corso-laurea").val() + "/esami",
        },
        rowGroup: {
            dataSrc: "anno_accademico.cod_anno_accademico"
        },
    });
}


function createEsame(eventObject) {
    eventObject.preventDefault();
    let form = $("#create-esame-form");
    $.ajax({
        url: "/api/esami",
        method: "POST",
        data: serializeForm(form),
        dataType: "json",
        contentType: "application/json",
        success: (res) => {
            page.table.ajax.reload();
            form.trigger("reset");
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

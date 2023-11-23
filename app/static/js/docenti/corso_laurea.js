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
        }
    });
    page.tableElement.on("click", "tr", function (eventObject) {
        let row = page.table.row(eventObject.target);
        console.log(row);
        if (row.child.isShown()) {
            row.child.hide();
            $(eventObject.target).removeClass("shown");
        } else {
            let esame = row.data();
            $.ajax({
                url: "/api/esami/" + esame.cod_esame + "/anni",
                success: (res) => {
                    row.child(formatEsami(res.data)).show();
                    $(eventObject.target).addClass("shown");
                }
            });
        }
    });
}


function formatEsami(esami) {
    let newTable = $("<table>")
        .attr("class", "table")
        .append(
            $("<thead>")
                .append(
                    $("<tr>")
                        .append(
                            $("<th>")
                                .text("Anno accademico")
                        )
                        .append(
                            $("<th>")
                                .text("Codice presidente")
                        )
                )
        );
    let tbody = $("<tbody>");
    for (let esame of esami) {
        tbody.append(
            $("<tr>")
                .append(
                    $("<td>")
                        .text(esame.anno_accademico.cod_anno_accademico)
                )
                .append(
                    $("<td>")
                        .text(esame.cod_presidente)
                )
        );
    }
    newTable.append(tbody);
    return newTable.prop("outerHTML");
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

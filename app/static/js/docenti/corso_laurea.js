const page = {};


$(() => {
    page.tableElement = $("#esami-table");
    initCreateEsame();
    initTable();
    initAddEsame();
});


function initCreateEsame() {
    $("#create-esame-btn").on("click", createEsame);
}

function initAddEsame() {
    let modal = $("#add-esame-anno-modal");
    modal.on("show.bs.modal", function (eventObject) {
        $.ajax({
            url: "/api/anni_accademici",
            success: (res) => {
                let select = modal.find("#cod-anno-accademico-add-anno");
                select.empty();
                for (let anno of res.data) {
                    select.append(
                        $("<option>")
                            .attr("value", anno.cod_anno_accademico)
                            .text(anno.cod_anno_accademico)
                    );
                }
            },
            error: (res) => {
                new Noty({
                    text: "Errore nel caricamento degli anni accademici",
                    type: "error",
                    timeout: 3000
                }).show();
            }
        });
    });

    $("#add-esame-anno-btn").on("click", createEsameAnno);
}

function initTable() {
    page.table = page.tableElement.DataTable({
        columns: [
            {
                render: function (data, type, row) {
                    return $("<button>")
                        .attr("class", "btn btn-secondary expand-btn")
                        .append(
                            $("<i>")
                                .attr("class", "fa-solid fa-caret-down")
                        )
                        .prop("outerHTML");
                },
                orderable: false
            },
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
                render: function () {
                    return $("<button>")
                        .attr("class", "btn btn-primary")
                        .attr("data-toggle", "modal")
                        .attr("data-target", "#add-esame-anno-modal")
                        .append(
                            $("<i>").attr("class", "fa-solid fa-plus")
                        )
                        .prop("outerHTML");
                }
            }
        ],
        ajax: {
            url: "/api/corso_laurea/" + $("#cod-corso-laurea").val() + "/esami",
        }
    });

    page.table.on("click", ".btn-add-esame-anno", function (eventObject) {
        let target = $(eventObject.target);
        let rowElem = target.parents("tr");
        let row = page.table.row(rowElem);
        let esame = row.data();
        let modal = $("#add-esame-anno-modal");
        modal.find("#cod-esame-add-anno").val(esame.cod_esame);
    });

    page.tableElement.on("click", ".expand-btn", function (eventObject) {
        let target = $(eventObject.target);
        let rowElem = target.parents("tr");
        let row = page.table.row(rowElem);

        // Hide if shown
        if (row.child.isShown()) {
            row.child.hide();
            target.removeClass("shown");
            rowElem.removeClass("table-active");
        }
        // Show if hidden
        else {
            let esame = row.data();
            // Fetch data
            $.ajax({
                url: "/api/esami/" + esame.cod_esame + "/anni",
                success: (res) => {
                    row.child(formatEsami(res.data)).show();
                    target.addClass("shown");
                    rowElem.addClass("table-active");
                },
                error: (res) => {
                    new Noty({
                        text: "Errore nel caricamento degli esami",
                        type: "error",
                        timeout: 3000
                    }).show();
                }
            });
        }
    });
}


function formatEsami(esami) {
    let newTable = $("<table>")
        .attr("class", "table table-sm table table-bordered")
        .append(
            $("<thead>").append(
                    $("<tr>").append(
                            $("<th>").text("Anno accademico")
                        )
                        .append(
                            $("<th>").text("Codice presidente")
                        )
            )
        );
    let tbody = $("<tbody>");
    for (let esame of esami) {
        tbody.append(
            $("<tr>").append(
                    $("<td>").text(esame.anno_accademico.cod_anno_accademico)
                )
                .append(
                    $("<td>").text(esame.cod_presidente)
                )
                .append(
                    $("<td>")
                        .attr("class", "col-1")
                        .append(
                        $("<a>")
                            .attr("class", "btn btn-primary")
                            .attr("href", "/docenti/esami/" + esame.cod_esame + "/anni/" + esame.anno_accademico.cod_anno_accademico)
                            .append(
                                $("<i>").attr("class", "fa-solid fa-eye")
                            )
                        )
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
    });
}

function createEsameAnno(eventObject) {
    eventObject.preventDefault();
    let form = $("#add-esame-anno-form");
    $.ajax({
        url: "/api/esami/" + $("#cod-esame-add-anno").val() + "/anni",
        method: "POST",
        data: serializeForm(form),
        dataType: "json",
        contentType: "application/json",
        success: (res) => {
            page.table.ajax.reload();
            form.trigger("reset");
            new Noty({
                text: "Esame aggiunto in anno accademico con successo",
                type: "success",
                timeout: 3000
            }).show();
        },
        error: (res) => {
            new Noty({
                text: "Errore nell'aggiunta dell'esame",
                type: "error",
                timeout: 3000
            }).show();
        }
    });
}
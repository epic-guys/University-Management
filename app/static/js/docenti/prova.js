
const page = {};

$(() => {
    page.tableElement = $("#appelli-table");
    page.addForm = $("#add-form");
    // page.addForm.on("submit", createAppello);
    page.addForm.on("reset", onResetForm);
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
                        .attr("href", "/docenti/appelli/" + row.cod_appello)
                        .prop("outerHTML");
                },
                orderable: false
            }

        ],
        ajax: {
            url: "/api/prove/" + $("#cod-prova").val() + "/appelli"
        }
    });
}

function createAppello(eventObject){
    console.log("Sesso");
    // eventObject.preventDefault();
    $.ajax({
        url: "/api/appelli",
        method: "POST",
        dataType: "json",
        contentType: "application/json",
        data: serializeForm(page.addForm),
        success: (res) => {
            new Noty({
                text: "Appello creato con successo",
                type: "success",
                timeout: 3000
            }).show();

            page.addForm.trigger("reset");
            page.table.ajax.reload();
        },
        error: (xhr, status, error) => {
            new Noty({
                text: "Creazione appello fallita",
                type: "error",
                timeout: 5000
            }).show();
        }
    });
}

function onResetForm() {
    console.log("reset");
    page.addForm.find("#cod-prova").val($("#cod-prova").val());
}

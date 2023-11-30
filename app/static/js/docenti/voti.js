const page = {};

$(() => {
    page.tableElement = $("#voti-table");
    initTable();
});


function initTable(){
    page.tableElement = page.tableElement.DataTable({
        columns: [
            {
                data: "nome",
                render: $.fn.dataTable.render.text()
            },
            {
                data: "cognome",
                render: $.fn.dataTable.render.text()
            },
            {
                data: "matricola",
                render: $.fn.dataTable.render.text()
            },
            {
                render: (data, type, row) => {
                    if (row.voto_appello != null) {
                        return row.voto_appello.voto;
                    }

                    let select = $('<select>')
                        .addClass("form-control voto-select");

                    // Se l'appello è in data futura, disattivo l'input
                    if (!page.editsEnabled) {
                        select.attr("disabled", "true");
                    }

                    // Creo le opzioni
                    let options = [];
                    Object.entries(votoString).forEach(
                        ([key, value]) => {
                        let opt = $("<option>")
                            .html(value)
                            .val(key);
                        options.push(opt);
                    });

                    // Voto non inserito
                    options.push($("<option>")
                        .html("-- Voto non inserito --")
                        .attr("value", "-1")
                        .attr("selected", "true")
                        .attr("disabled", "true")
                    );

                    // Aggiungo le opzioni
                    select.append(options);
                    return select.prop("outerHTML");
                }
            }
        ],
        ajax: {
            url: "/api/esami/" + $("#cod_esame").val() + "/anni/" + $("#cod_anno_accademico").val() + "/idonei"
        }
    });
}
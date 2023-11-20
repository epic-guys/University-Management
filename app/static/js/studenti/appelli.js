const page = {};

$(() => {
    page.tableElement = $('#appelli-table');
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
                        .attr("class", "btn btn-primary")
                        .html(
                            $("<i>")
                                .attr("class", "fa-solid fa-plus")
                        )
                        // FIXME potenziale XSS
                        .attr("href", "/studenti/appelli/" + row.cod_appello + "/iscrizione")
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
}

function iscriviti(cod_appello) {
    $.ajax({
        url: "/api/appelli/" + cod_appello + "/iscrizione",
        method: "POST",
        success: (res) => {
           console.log("inviato")
        }
    })
}

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
               render: $.fn.dataTable.render.text()
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
                                .attr("class", "fa-solid fa-eye")
                        )
                        // FIXME potenziale XSS
                        .attr("href", "/docenti/appelli/" + row.cod_appello)
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

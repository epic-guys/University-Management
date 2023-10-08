const page = {};

$(() => {
    page.tableElement = $('#profilo-table');
   initTable();
});


function initTable(){
    page.tableElement = page.tableElement.DataTable({
       columns: [
           {
               data: "ruolo",
               render: $.fn.dataTable.render.text()
           },
           {
               data: "cod_persona",
               render: $.fn.dataTable.render.text()
           },
           {
               data: "nome",
               render: $.fn.dataTable.render.text()
           },
           {
               data: "cognome",
               render: $.fn.dataTable.render.text()
           },
           {
               data: "data_nascita",
               render: $.fn.dataTable.render.text()
           },
           {
               data: "sesso",
               render: $.fn.dataTable.render.text()
           },
           {
               data: "email",
               render: $.fn.dataTable.render.text()
           }
       ],
         ajax: {
            url: "/api/persone",
            dataSrc: ""
        }
    });
}
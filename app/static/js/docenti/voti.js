const page = {};

$(() => {
    page.tableElement = $("#voti-table");
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
                data: "matricola",
                render: $.fn.dataTable.render.text()
            },
            {
                data: "voto",
                render: $.fn.dataTable.render.number()
            },
            {

            }
        ],
        ajax: {
            url: "/api/voti"
        }
    });
}
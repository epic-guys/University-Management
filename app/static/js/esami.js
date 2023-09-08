$(() => {
    $("#esami_t").DataTable({
        columns: [
            {data: "cod_esame"},
            {data: "nome_corso"},
            {data: "descrizione_corso"},
            {data: "anno"},
            {data: "cfu"},
            {data: "cod_corso_laurea"}
        ],
        ajax: {
            url: "/api/esami",
            dataSrc: ""
        }
    });
});

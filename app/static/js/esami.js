$(() => {
    $("#esami-table").DataTable({
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

    $.ajax({
        url: "/api/corsi_laurea",
        success: (res) => {
            let corsi = JSON.parse(res);
            let options = [];
            for (const c of corsi) {
                let option = $("<option>");
                option.attr("value", c.cod_corso_laurea);
                option.html(c.nome_corso_laurea);
                options.push(option);
            }
            $('#cod_corso_laurea').html(options);
        },
        error: () => {
            // TODO cambiare ovviamente, è solo per debug
            alert("Richiesta a corsi di laurea fallita");
        }
    });


});


function createEsame() {
    let obj = {};

    $.ajax({
        url: "/api/esami",
        method: "POST",
        data: $("#add-form").serialize(),
        success: (res) => {
            $("#esami-table").DataTable().ajax.reload();
        }
    })
}

function resetEsame() {
    $("#add-form").trigger("reset");
}

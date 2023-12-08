const page = {};

$("#form-iscriviti").submit(function (e) {
    e.preventDefault();
    submitForm();
});

function submitForm() {
        $.ajax({
            type: 'POST',
            url: $('#form-iscriviti').attr('action'),
            data: $('#form-iscriviti').serialize(),
            success: function(response) {
                new Noty({
                text: "Iscrizione avvenuta con successo",
                type: "success",
                timeout: 3000
                }).show();
            },
            error: function(xhr, status, error) {
                new Noty({
                text: "Studente già iscritto all'appello",
                type: "warning",
                timeout: 3000
                }).show();
            }
        });
    }
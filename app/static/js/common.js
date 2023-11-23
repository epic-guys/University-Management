function serializeForm(form) {
    let data = {};
    let array = form.serializeArray();
    for (const field of array) {
        data[field.name] = field.value;
    }
    return JSON.stringify(data);
}

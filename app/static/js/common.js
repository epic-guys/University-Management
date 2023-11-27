function serializeForm(form) {
    let data = {};
    let array = form.serializeArray();
    for (const field of array) {
        data[field.name] = field.value;
    }
    return JSON.stringify(data);
}


const votoString = {
        "0": "assente",
        "1": "insufficiente",
        "2": "ritirato",

        /*
        * Fa confusione ma ecco una spiegazione.
        * Crea una lambda che si limita a creare un oggetto
        * che associa ogni numero a sé stesso.
        * Viene chiamata la lambda.
        * Poi l'operatore ... "spacchetta" l'oggetto e lo
        * inserisce in quello attuale.
        */
        ...(() => {
            let dict = {};
            for (let i = 18; i <= 31; i++) {
                let iStr= i.toString();
                dict[iStr] = iStr;
            }
            return dict;
        })()
    };

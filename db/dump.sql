DROP TABLE IF EXISTS esami CASCADE ;
CREATE TABLE esami (
    cod_esame TEXT NOT NULL PRIMARY KEY,
    nome_corso TEXT NOT NULL,
    anno INT NOT NULL,
    cfu INT NOT NULL
);

DROP TABLE IF EXISTS ruoli CASCADE;
CREATE TABLE ruoli (
    ruolo CHAR(1) NOT NULL PRIMARY KEY
);

DROP TABLE IF EXISTS persone CASCADE;
CREATE TABLE persone (
    ruolo CHAR(1) NOT NULL,
    cod_persona TEXT NOT NULL PRIMARY KEY,
    nome TEXT NOT NULL,
    cognome TEXT NOT NULL,
    data_nascita DATE NOT NULL,
    sesso CHAR(1) CHECK ( sesso IN ('M', 'F') ),
    email TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    FOREIGN KEY (ruolo) REFERENCES ruoli(ruolo)
);

DROP TABLE IF EXISTS studenti;
CREATE TABLE studenti (
    matricola TEXT NOT NULL PRIMARY KEY,
    FOREIGN KEY (matricola) REFERENCES persone (cod_persona)
                      ON UPDATE CASCADE
                      ON DELETE CASCADE
);

DROP TABLE IF EXISTS docenti;
CREATE TABLE docenti (
    cod_docente TEXT NOT NULL PRIMARY KEY,
    FOREIGN KEY (cod_docente) REFERENCES persone (cod_persona)
                     ON UPDATE CASCADE
                     ON DELETE CASCADE
);

DROP TABLE IF EXISTS esami;
CREATE TABLE esami (
    cod_esame TEXT NOT NULL PRIMARY KEY,
    nome_corso TEXT NOT NULL,
    anno INT NOT NULL,
    cfu INT NOT NULL
);

DROP TABLE IF EXISTS prove CASCADE;
CREATE TABLE prove (
    cod_prova TEXT NOT NULL PRIMARY KEY,
    scadenza DATE DEFAULT NULL,
    cod_esame TEXT NOT NULL,
    FOREIGN KEY (cod_esame) REFERENCES esami (cod_esame)
                   ON UPDATE CASCADE
                   ON DELETE CASCADE
);

DROP TABLE IF EXISTS appelli CASCADE;
CREATE TABLE appelli(
    data DATE NOT NULL,
    cod_prova TEXT NOT NULL,
    PRIMARY KEY (cod_prova, data),
    FOREIGN KEY (cod_prova) REFERENCES prove(cod_prova)
                    ON UPDATE CASCADE
                    ON DELETE CASCADE
);

-- Trigger
DROP TRIGGER IF EXISTS role_check_docenti_t ON docenti;
DROP TRIGGER IF EXISTS role_check_studenti_t ON studenti;
DROP FUNCTION IF EXISTS role_check();
CREATE FUNCTION role_check()
RETURNS TRIGGER
AS $$
DECLARE persona persone;
BEGIN


    IF tg_table_name = 'studenti' THEN
        SELECT *
            INTO persona
            FROM persone
            WHERE cod_persona = NEW.matricola;
        IF persona.ruolo <> 'S' THEN
            RETURN NULL;
        END IF;
    ELSIF tg_table_name = 'docenti' THEN
        SELECT *
        INTO persona
        FROM persone
        WHERE cod_persona = NEW.cod_docente;
        IF persona.ruolo <> 'D' THEN
            RETURN NULL;
        END IF;
    END IF;

    RETURN NEW;
END
$$ LANGUAGE plpgsql;


CREATE TRIGGER role_check_docenti_t
    BEFORE INSERT OR UPDATE
    ON docenti
    FOR EACH ROW
EXECUTE FUNCTION role_check();


CREATE TRIGGER role_check_studenti_t
    BEFORE INSERT OR UPDATE
    ON studenti
    FOR EACH ROW
EXECUTE FUNCTION role_check();

-- Data

-- Ruoli di docente e studente
INSERT INTO ruoli VALUES ('D'), ('S');

INSERT INTO persone VALUES
                        ('D', '01','Alvise','Spanò','03-07-67','M', 'sample1@unive.it', 'lmao'),
                        ('D', '02', 'Stefano', 'Calzavara', '01-02-69', 'M', 'sample2@unive.it', 'zedong'),
                        ('S', '03', 'Zio', 'Pera', '01-01-69', 'F', 'aa@bb.cum', 'e');

INSERT INTO docenti VALUES
                        ('01'),
                        ('02');

INSERT INTO studenti VALUES
                         ('03');
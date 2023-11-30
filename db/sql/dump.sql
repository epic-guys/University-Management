DROP TABLE IF EXISTS corsi_laurea CASCADE;
CREATE TABLE corsi_laurea
(
    cod_corso_laurea  TEXT NOT NULL PRIMARY KEY CHECK ( cod_corso_laurea SIMILAR TO 'C[TM]\d+' ),
    nome_corso_laurea TEXT NOT NULL
);


DROP TABLE IF EXISTS anni_accademici CASCADE;
CREATE TABLE anni_accademici
(
    cod_anno_accademico INTEGER PRIMARY KEY,
    anno_accademico     CHAR(9),
    inizio_anno         DATE,
    fine_anno           DATE,
    CHECK ( inizio_anno < fine_anno )
);


DROP TABLE IF EXISTS ruoli CASCADE;
CREATE TABLE ruoli
(
    ruolo CHAR(1) NOT NULL PRIMARY KEY
);


DROP TABLE IF EXISTS persone CASCADE;
CREATE TABLE persone
(
    ruolo         CHAR(1) NOT NULL,
    cod_persona   TEXT    NOT NULL PRIMARY KEY CHECK (cod_persona SIMILAR TO '[a-zA-Z0-9_]+'),
    nome          TEXT    NOT NULL CHECK ( nome <> ''),
    cognome       TEXT    NOT NULL CHECK ( cognome <> ''),
    data_nascita  DATE    NOT NULL,
    sesso         CHAR(1) CHECK ( sesso IN ('M', 'F') ),
    email         TEXT    NOT NULL CHECK ( email <> ''),
    password_hash TEXT    NOT NULL CHECK ( password_hash <> '' ),
    FOREIGN KEY (ruolo) REFERENCES ruoli (ruolo)
);


DROP TABLE IF EXISTS studenti CASCADE;
CREATE TABLE studenti
(
    matricola               TEXT NOT NULL PRIMARY KEY,
    cod_corso_laurea        TEXT NOT NULL,
    cod_anno_iscrizione     INT  NOT NULL,
    FOREIGN KEY (matricola) REFERENCES persone (cod_persona),
    FOREIGN KEY (cod_corso_laurea) REFERENCES corsi_laurea (cod_corso_laurea),
    FOREIGN KEY (cod_anno_iscrizione) REFERENCES anni_accademici (cod_anno_accademico)
);


DROP TABLE IF EXISTS docenti CASCADE;
CREATE TABLE docenti
(
    cod_docente TEXT NOT NULL PRIMARY KEY,
    FOREIGN KEY (cod_docente) REFERENCES persone (cod_persona)
);


DROP TABLE IF EXISTS esami CASCADE;
CREATE TABLE esami
(
    cod_esame         TEXT NOT NULL PRIMARY KEY CHECK ( cod_esame SIMILAR TO 'E\d+' ),
    nome_corso        TEXT NOT NULL CHECK ( nome_corso SIMILAR TO '[a-zA-Z0-9_ ]+'),
    descrizione_corso TEXT,
    anno              INT  NOT NULL,
    cfu               INT  NOT NULL,
    cod_corso_laurea  TEXT NOT NULL,
    FOREIGN KEY (cod_corso_laurea) REFERENCES corsi_laurea (cod_corso_laurea)
);


DROP TABLE IF EXISTS esami_anni_accademici CASCADE;
CREATE TABLE esami_anni_accademici
(
    cod_esame           TEXT    NOT NULL,
    cod_anno_accademico INTEGER NOT NULL,
    cod_presidente      TEXT    NOT NULL,

    PRIMARY KEY (cod_anno_accademico, cod_esame),
    FOREIGN KEY (cod_esame) REFERENCES esami (cod_esame),
    FOREIGN KEY (cod_anno_accademico) REFERENCES anni_accademici (cod_anno_accademico)
);


DROP TABLE IF EXISTS voti_esami CASCADE;
CREATE TABLE voti_esami
(
    cod_esame           TEXT        NOT NULL,
    cod_anno_accademico INTEGER     NOT NULL,
    matricola           TEXT        NOT NULL,
    voto                INT         NOT NULL
        CHECK (
                (voto >= 0 AND voto <= 2)
            OR  (voto >= 18 AND voto <= 31)
        ),
    data_completamento  timestamptz NOT NULL,

    -- È più frequente cercare gli esami a partire dallo studente piuttosto che viceversa
    -- Usando matricola e cod_esame, si impone il vincolo che uno studente non possa sostenere lo stesso esame più volte
    -- Se si usasse anche cod_anno_accademico, uno studente potrebbe sostenere lo stesso esame più volte in anni accademici diversi
    PRIMARY KEY (matricola, cod_esame),
    FOREIGN KEY (cod_esame, cod_anno_accademico) REFERENCES esami_anni_accademici (cod_esame, cod_anno_accademico),
    FOREIGN KEY (cod_esame) REFERENCES esami (cod_esame),
    FOREIGN KEY (matricola) REFERENCES studenti (matricola)
);


DROP TABLE IF EXISTS tipi_prove CASCADE;
CREATE TABLE tipi_prove
(
    tipo_prova TEXT NOT NULL PRIMARY KEY
);

DROP TABLE IF EXISTS prove CASCADE;
CREATE TABLE prove
(
    cod_prova           TEXT          NOT NULL PRIMARY KEY CHECK ( cod_prova SIMILAR TO 'P\d+' ),
    tipo_prova          TEXT          NOT NULL,
    denominazione_prova TEXT          NOT NULL CHECK ( denominazione_prova <> ''),
    descrizione_prova   TEXT,
    peso                NUMERIC(2, 1) NOT NULL CHECK ( peso BETWEEN 0 AND 1),
    scadenza            DATE          NOT NULL,
    cod_esame           TEXT          NOT NULL,
    cod_docente         TEXT          NOT NULL,
    cod_anno_accademico INT           NOT NULL,

    FOREIGN KEY (cod_anno_accademico, cod_esame) REFERENCES esami_anni_accademici (cod_anno_accademico, cod_esame),
    FOREIGN KEY (cod_esame) REFERENCES esami (cod_esame),
    FOREIGN KEY (cod_docente) REFERENCES docenti (cod_docente),
    FOREIGN KEY (tipo_prova) REFERENCES tipi_prove (tipo_prova),
    FOREIGN KEY (cod_anno_accademico) REFERENCES anni_accademici (cod_anno_accademico)
);

DROP TABLE IF EXISTS appelli CASCADE;
CREATE TABLE appelli
(
    cod_appello  TEXT        NOT NULL PRIMARY KEY CHECK ( cod_appello SIMILAR TO 'A\d+' ),
    data_appello timestamptz NOT NULL,
    cod_prova    TEXT        NOT NULL,
    aula         TEXT        NOT NULL,
    FOREIGN KEY (cod_prova) REFERENCES prove (cod_prova)
);

DROP TABLE IF EXISTS iscrizioni_appelli CASCADE;
CREATE TABLE iscrizioni_appelli
(
    cod_appello     TEXT        NOT NULL,
    matricola       TEXT        NOT NULL,
    data_iscrizione timestamptz NOT NULL,

    PRIMARY KEY (cod_appello, matricola),
    FOREIGN KEY (cod_appello) REFERENCES appelli (cod_appello)
);


DROP TABLE IF EXISTS voti_appelli CASCADE;
CREATE TABLE voti_appelli
(
    cod_appello TEXT NOT NULL,
    matricola   TEXT NOT NULL,
    voto        INT  NOT NULL,

    PRIMARY KEY (cod_appello, matricola),
    FOREIGN KEY (cod_appello, matricola) REFERENCES iscrizioni_appelli (cod_appello, matricola),

    FOREIGN KEY (cod_appello) REFERENCES appelli (cod_appello),
    FOREIGN KEY (matricola) REFERENCES studenti (matricola)
);


--#region Viste

DROP VIEW IF EXISTS voti_prove CASCADE;
CREATE VIEW voti_prove AS
WITH appelli_recenti AS (SELECT a.cod_prova, v.matricola, MAX(a.data_appello) AS appello_recente
                         FROM voti_appelli v
                                  NATURAL JOIN appelli a
                         GROUP BY a.cod_prova, v.matricola)
SELECT v2.*
FROM voti_appelli v2
         NATURAL JOIN appelli a2
         JOIN appelli_recenti ar ON a2.cod_prova = ar.cod_prova
    AND v2.matricola = ar.matricola
    AND a2.data_appello = ar.appello_recente
WHERE v2.voto >= 18;



--#endregion


--#region Funzioni

DROP FUNCTION IF EXISTS get_voti_prove_esame(TEXT, INT);
CREATE FUNCTION get_voti_prove_esame(cod_esame_ TEXT, anno_accademico_ INT)
RETURNS SETOF voti_prove
AS $$
BEGIN
    RETURN QUERY
    SELECT v.cod_appello, s.matricola, v.voto
    FROM studenti s
    CROSS JOIN prove p
    LEFT JOIN appelli a ON a.cod_prova = p.cod_prova
    LEFT JOIN voti_prove v ON v.cod_appello = a.cod_appello AND v.matricola = s.matricola
    WHERE p.cod_esame = cod_esame_
    AND p.cod_anno_accademico = anno_accademico_
    AND s.matricola IN (
        /* per una query corretta si dovrebbe usare DISTINCT, ma dato che
        stiamo solo controllando che la matricola sia presente nella tabella, si
        può fare senza, in modo da velocizzare la query */
        SELECT v.matricola
        FROM voti_prove v
        JOIN appelli a ON a.cod_appello = v.cod_appello
        JOIN prove p ON p.cod_prova = a.cod_prova
        WHERE p.cod_esame = cod_esame_
        );
END; $$ LANGUAGE plpgsql;

--#region Trigger

DROP TRIGGER IF EXISTS role_check_t ON docenti;
DROP TRIGGER IF EXISTS role_check_t ON studenti;
DROP FUNCTION IF EXISTS role_check();
CREATE FUNCTION role_check()
    RETURNS TRIGGER
AS
$$
DECLARE
    persona persone;
BEGIN
    IF tg_table_name = 'studenti' THEN
        SELECT *
        INTO persona
        FROM persone
        WHERE cod_persona = NEW.matricola;
        IF persona.ruolo <> 'S' THEN
            RAISE EXCEPTION 'Ruolo sbagliato in tabella studenti';
        END IF;
    ELSIF tg_table_name = 'docenti' THEN
        SELECT *
        INTO persona
        FROM persone
        WHERE cod_persona = NEW.cod_docente;
        IF persona.ruolo <> 'D' THEN
            RAISE EXCEPTION 'Ruolo sbagliato in tabella docenti';
        END IF;
    END IF;

    RETURN NEW;
END
$$ LANGUAGE plpgsql;


CREATE TRIGGER role_check_t
    BEFORE INSERT OR UPDATE
    ON docenti
    FOR EACH ROW
EXECUTE FUNCTION role_check();


CREATE TRIGGER role_check_t
    BEFORE INSERT OR UPDATE
    ON studenti
    FOR EACH ROW
EXECUTE FUNCTION role_check();

DROP TRIGGER IF EXISTS data_appello_check_t ON appelli;
DROP FUNCTION IF EXISTS data_appello_check();
CREATE FUNCTION data_appello_check()
    RETURNS TRIGGER
AS
$$
DECLARE
    appello appelli;
BEGIN
    SELECT *
    INTO appello
    FROM appelli
    WHERE appello.cod_appello = NEW.cod_appello;

    IF NEW.data_iscrizione > appello.data_appello THEN
        RAISE EXCEPTION 'Iscrizione appello supera scadenza della prova';
    END IF;

    RETURN NEW;

END
$$ LANGUAGE plpgsql;

CREATE TRIGGER data_appello_check_t
    BEFORE INSERT OR UPDATE
    ON iscrizioni_appelli
    FOR EACH ROW
EXECUTE FUNCTION data_appello_check();

--#endregion

--#region Dati

COPY ruoli
FROM '/csv/ruoli.csv'
DELIMITER ','
CSV HEADER;

COPY corsi_laurea
FROM '/csv/corsi_laurea.csv'
DELIMITER ','
CSV HEADER;

COPY tipi_prove
FROM '/csv/tipi_prove.csv'
DELIMITER ','
CSV HEADER;

COPY anni_accademici
FROM '/csv/anni_accademici.csv'
DELIMITER ','
CSV HEADER;

COPY persone
FROM '/csv/persone.csv'
DELIMITER ','
CSV HEADER;

COPY studenti
FROM '/csv/studenti.csv'
DELIMITER ','
CSV HEADER;

COPY docenti
FROM '/csv/docenti.csv'
DELIMITER ','
CSV HEADER;

COPY esami
FROM '/csv/esami.csv'
DELIMITER ','
CSV HEADER;

COPY esami_anni_accademici
FROM '/csv/esami_anni_accademici.csv'
DELIMITER ','
CSV HEADER;

COPY prove
FROM '/csv/prove.csv'
DELIMITER ','
CSV HEADER;

COPY appelli
FROM '/csv/appelli.csv'
DELIMITER ','
CSV HEADER;

COPY iscrizioni_appelli
FROM '/csv/iscrizioni_appelli.csv'
DELIMITER ','
CSV HEADER;


COPY voti_appelli
FROM '/csv/voti_appelli.csv'
DELIMITER ','
CSV HEADER;


COPY voti_esami
FROM '/csv/voti_esami.csv'
DELIMITER ','
CSV HEADER;

--#endregion

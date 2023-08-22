DROP TABLE IF EXISTS corso_laurea CASCADE;
CREATE TABLE corsi_laurea (
    cod_corso_laurea TEXT NOT NULL PRIMARY KEY,
    nome_corso_laurea TEXT NOT NULL
);

DROP TABLE IF EXISTS esami CASCADE;
CREATE TABLE esami (
    cod_esame TEXT NOT NULL PRIMARY KEY,
    nome_corso TEXT NOT NULL,
    descrizione_corso TEXT,
    anno INT NOT NULL,
    cfu INT NOT NULL,
    cod_corso_laurea TEXT NOT NULL,
    FOREIGN KEY (cod_corso_laurea) REFERENCES corsi_laurea (cod_corso_laurea)
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
    cod_corso_laurea TEXT NOT NULL,
    FOREIGN KEY (matricola) REFERENCES persone (cod_persona)
                      ON UPDATE CASCADE
                      ON DELETE CASCADE,
    FOREIGN KEY (cod_corso_laurea) REFERENCES corsi_laurea (cod_corso_laurea)
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

-- Data

-- Ruoli di docente e studente
INSERT INTO ruoli VALUES ('D'), ('S');

INSERT INTO corsi_laurea VALUES
                             ('CT3', 'Informatica');

INSERT INTO corsi VALUES
                      ('123', 'Basi di dati', 'Dati basati?', 2, 'CT3');

-- Docenti
INSERT INTO persone VALUES
                        ('D', '01','Alvise','Spanò','03-07-67','M', 'sample1@unive.it', 'lmao'),
                        ('D', '02', 'Stefano', 'Calzavara', '01-02-69', 'M', 'sample2@unive.it', 'zedong');

INSERT INTO docenti VALUES
                        ('01'),
                        ('02');


-- Studenti (assolutamente non generati da ChatGPT)
INSERT INTO persone (ruolo, cod_persona, nome, cognome, data_nascita, sesso, email, password_hash)
VALUES
    ('S', '1', 'Marco', 'Rossi', '2000-01-01', 'M', 'marco@email.com', 'hash1'),
    ('S', '2', 'Linda', 'Bianchi', '2000-02-02', 'F', 'linda@email.com', 'hash2'),
    ('S', '3', 'Luca', 'Verdi', '2000-03-03', 'M', 'luca@email.com', 'hash3'),
    ('S', '4', 'Alessia', 'Neri', '2000-04-04', 'F', 'alessia@email.com', 'hash4'),
    ('S', '5', 'Simone', 'Giallo', '2000-05-05', 'M', 'simone@email.com', 'hash5'),
    ('S', '6', 'Chiara', 'Rosa', '2000-06-06', 'F', 'chiara@email.com', 'hash6'),
    ('S', '7', 'Fabio', 'Marrone', '2000-07-07', 'M', 'fabio@email.com', 'hash7'),
    ('S', '8', 'Laura', 'Blu', '2000-08-08', 'F', 'laura@email.com', 'hash8'),
    ('S', '9', 'Giovanni', 'Viola', '2000-09-09', 'M', 'giovanni@email.com', 'hash9'),
    ('S', '10', 'Valeria', 'Arancio', '2000-10-10', 'F', 'valeria@email.com', 'hash10');

INSERT INTO studenti (matricola, cod_corso_laurea)
VALUES
    ('1', 'CT3'),
    ('2', 'CT3'),
    ('3', 'CT3'),
    ('4', 'CT3'),
    ('5', 'CT3'),
    ('6', 'CT3'),
    ('7', 'CT3'),
    ('8', 'CT3'),
    ('9', 'CT3'),
    ('10', 'CT3');


-- Esami (anche questi non li ha generati ChatGPT, soprattutto perché sono tutti esami che abbiamo anche noi)

INSERT INTO esami (cod_esame, nome_corso, descrizione_corso, anno, cfu, cod_corso_laurea)
VALUES
    ('E1', 'Matematica 1', 'Fondamenti di matematica', 1, 6, 'CT3'),
    ('E2', 'Fisica 1', 'Principi della fisica classica', 1, 6, 'CT3'),
    ('E3', 'Informatica 1', E'Introduzione all\'informatica', 1, 9, 'CT3'),
    ('E4', 'Chimica', 'Introduzione alla chimica', 1, 6, 'CT3'),
    ('E5', 'Ingegneria del Software', E'Principi dell\'ingegneria del software', 2, 9, 'CT3'),
    ('E6', 'Sistemi Operativi', 'Fondamenti dei sistemi operativi', 2, 9, 'CT3'),
    ('E7', 'Elettrotecnica', 'Principi di elettrotecnica', 2, 6, 'CT3'),
    ('E8', 'Analisi dei Dati', 'Metodi di analisi dei dati', 3, 9, 'CT3'),
    ('E9', 'Reti di Calcolatori', 'Introduzione alle reti di calcolatori', 3, 6, 'CT3'),
    ('E10', 'Progettazione dei Circuiti', 'Progettazione di circuiti elettronici', 3, 9, 'CT3');


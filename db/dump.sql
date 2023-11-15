DROP TABLE IF EXISTS corsi_laurea CASCADE;
CREATE TABLE corsi_laurea (
    cod_corso_laurea TEXT NOT NULL PRIMARY KEY,
    nome_corso_laurea TEXT NOT NULL
);


DROP TABLE IF EXISTS anni_accademici CASCADE;
CREATE TABLE anni_accademici (
     cod_anno_accademico INTEGER PRIMARY KEY,
     anno_accademico CHAR(9)
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


DROP TABLE IF EXISTS studenti CASCADE;
CREATE TABLE studenti (
                          matricola TEXT NOT NULL PRIMARY KEY,
                          cod_corso_laurea TEXT NOT NULL,
                          FOREIGN KEY (matricola) REFERENCES persone (cod_persona)
                              ON UPDATE CASCADE
                              ON DELETE CASCADE,
                          FOREIGN KEY (cod_corso_laurea) REFERENCES corsi_laurea (cod_corso_laurea)
);


DROP TABLE IF EXISTS docenti CASCADE;
CREATE TABLE docenti (
                         cod_docente TEXT NOT NULL PRIMARY KEY,
                         FOREIGN KEY (cod_docente) REFERENCES persone (cod_persona)
                             ON UPDATE CASCADE
                             ON DELETE CASCADE
);


DROP TABLE IF EXISTS esami CASCADE;
CREATE TABLE esami (
    cod_esame TEXT NOT NULL PRIMARY KEY,
    nome_corso TEXT NOT NULL,
    descrizione_corso TEXT,
    anno INT NOT NULL,
    cfu INT NOT NULL,
    cod_corso_laurea TEXT NOT NULL,
    FOREIGN KEY (cod_corso_laurea) REFERENCES corsi_laurea (cod_corso_laurea),
    FOREIGN KEY (cod_presidente) REFERENCES docenti (cod_docente)
);


DROP TABLE IF EXISTS esami_anni_accademici CASCADE;
CREATE TABLE esami_anni_accademici (
    cod_esame TEXT NOT NULL,
    cod_anno_accademico INTEGER NOT NULL,
    cod_presidente TEXT NOT NULL,

    PRIMARY KEY (cod_anno_accademico, cod_esame),
    FOREIGN KEY (cod_esame) REFERENCES esami (cod_esame),
    FOREIGN KEY (cod_anno_accademico) REFERENCES anni_accademici (cod_anno_accademico)
);


DROP TABLE IF EXISTS voti_esami CASCADE;
CREATE TABLE voti_esami (
    cod_esame TEXT NOT NULL,
    matricola TEXT NOT NULL,
    voto INT NOT NULL,
    data_completamento timestamptz NOT NULL,

    -- È più frequente cercare gli esami a partire dallo studente piuttosto che viceversa
    PRIMARY KEY (matricola, cod_esame),
    FOREIGN KEY (cod_esame) REFERENCES esami (cod_esame),
    FOREIGN KEY (matricola) REFERENCES studenti (matricola)
);


DROP TABLE IF EXISTS tipi_prove CASCADE;
CREATE TABLE tipi_prove (
    tipo_prova TEXT NOT NULL PRIMARY KEY
);

DROP TABLE IF EXISTS prove CASCADE;
CREATE TABLE prove (
    cod_prova TEXT NOT NULL PRIMARY KEY,
    tipo_prova TEXT NOT NULL,
    denominazione_prova TEXT NOT NULL,
    descrizione_prova TEXT NOT NULL,
    peso NUMERIC(2, 1) NOT NULL CHECK ( peso BETWEEN 0 AND 1),
    scadenza DATE NOT NULL,
    cod_esame TEXT NOT NULL,
    cod_docente TEXT NOT NULL,
    cod_anno_accademico INT NOT NULL,

    FOREIGN KEY (cod_anno_accademico, cod_esame) REFERENCES esami_anni_accademici (cod_anno_accademico, cod_esame),
    FOREIGN KEY (cod_esame) REFERENCES esami (cod_esame)
                   ON UPDATE CASCADE
                   ON DELETE CASCADE,
    FOREIGN KEY (cod_docente) REFERENCES docenti(cod_docente),
    FOREIGN KEY (tipo_prova) REFERENCES tipi_prove(tipo_prova),
    FOREIGN KEY (cod_anno_accademico) REFERENCES anni_accademici (cod_anno_accademico)
);

DROP TABLE IF EXISTS appelli CASCADE;
CREATE TABLE appelli(
    cod_appello TEXT NOT NULL PRIMARY KEY,
    data_appello timestamptz NOT NULL,
    cod_prova TEXT NOT NULL,
    aula TEXT NOT NULL,
    FOREIGN KEY (cod_prova) REFERENCES prove(cod_prova)
                    ON UPDATE CASCADE
                    ON DELETE CASCADE
);

DROP TABLE IF EXISTS iscrizioni_appelli CASCADE;
CREATE TABLE iscrizioni_appelli (
    cod_appello TEXT NOT NULL,
    matricola TEXT NOT NULL,
    data_iscrizione timestamptz NOT NULL,

    PRIMARY KEY (cod_appello, matricola),
    FOREIGN KEY (cod_appello) REFERENCES appelli(cod_appello)
);

DROP TABLE IF EXISTS voti_prove CASCADE;
CREATE TABLE voti_prove (
    cod_appello TEXT NOT NULL,
    matricola TEXT NOT NULL,
    voto INT NOT NULL,

    PRIMARY KEY (cod_appello, matricola),
    FOREIGN KEY (cod_appello, matricola) REFERENCES iscrizioni_appelli(cod_appello, matricola),

    FOREIGN KEY (cod_appello) REFERENCES appelli(cod_appello),
    FOREIGN KEY (matricola) REFERENCES studenti(matricola)
                 ON UPDATE CASCADE
                 ON DELETE CASCADE
);

-- Trigger
DROP TRIGGER IF EXISTS role_check_t ON docenti;
DROP TRIGGER IF EXISTS role_check_t ON studenti;
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
AS $$
DECLARE prova prove;
BEGIN
    SELECT * INTO prova
    FROM prove p
    NATURAL JOIN iscrizioni_appelli i
    WHERE i.cod_appello = NEW.cod_appello;

    IF NEW.data_iscrizione > prova.scadenza THEN
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

-- Data

-- Ruoli di docente e studente
INSERT INTO ruoli VALUES ('D'), ('S');

INSERT INTO corsi_laurea VALUES
                             ('CT3', 'Informatica');

INSERT INTO tipi_prove VALUES
                           ('Scritto'),
                           ('Orale'),
                           ('Pratico');


-- Anni accademici
INSERT INTO anni_accademici (cod_anno_accademico, anno_accademico)
VALUES
    (2023, '2023-2024'),
    (2022, '2022-2023'),
    (2021, '2021-2022'),
    (2020, '2020-2021');



--#region DATI STUDENTI

-- Studenti (assolutamente non generati da ChatGPT)
INSERT INTO persone (ruolo, cod_persona, nome, cognome, data_nascita, sesso, email, password_hash)
VALUES
    ('S', '11', 'Marco', 'Rossi', '2000-01-01', 'M', 'marco@email.com', 'hash1'),
    ('S', '12', 'Linda', 'Bianchi', '2000-02-02', 'F', 'linda@email.com', 'hash2'),
    ('S', '13', 'Luca', 'Verdi', '2000-03-03', 'M', 'luca@email.com', 'hash3'),
    ('S', '14', 'Alessia', 'Neri', '2000-04-04', 'F', 'alessia@email.com', 'hash4'),
    ('S', '15', 'Simone', 'Giallo', '2000-05-05', 'M', 'simone@email.com', 'hash5'),
    ('S', '16', 'Chiara', 'Rosa', '2000-06-06', 'F', 'chiara@email.com', 'hash6'),
    ('S', '17', 'Fabio', 'Marrone', '2000-07-07', 'M', 'fabio@email.com', 'hash7'),
    ('S', '18', 'Laura', 'Blu', '2000-08-08', 'F', 'laura@email.com', 'hash8'),
    ('S', '19', 'Giovanni', 'Viola', '2000-09-09', 'M', 'giovanni@email.com', 'hash9'),
    ('S', '20', 'Valeria', 'Arancio', '2000-10-10', 'F', 'valeria@email.com', 'hash10');

INSERT INTO studenti (matricola, cod_corso_laurea)
VALUES
    ('11', 'CT3'),
    ('12', 'CT3'),
    ('13', 'CT3'),
    ('14', 'CT3'),
    ('15', 'CT3'),
    ('16', 'CT3'),
    ('17', 'CT3'),
    ('18', 'CT3'),
    ('19', 'CT3'),
    ('20', 'CT3');

--#endregion


--#region DATI DOCENTI

-- Inserisci docenti con codici da 1 a 10 e ruolo 'D'
INSERT INTO persone (ruolo, cod_persona, nome, cognome, data_nascita, sesso, email, password_hash)
VALUES
    ('D', '1', 'Alvise', 'Spanò', '1975-05-10', 'M', 'alvise.spano@example.com', 'hash1'),
    ('D', '2', 'Maria', 'Verdi', '1980-03-15', 'F', 'maria.verdi@example.com', 'hash2'),
    ('D', '3', 'Stefano', 'Calzavara', '1972-11-22', 'M', 'stefano.calzavara@example.com', 'hash3'),
    ('D', '4', 'Elena', 'Marchetti', '1985-07-18', 'F', 'elena.marchetti@example.com', 'hash4'),
    ('D', '5', 'Fabio', 'Martini', '1988-09-02', 'M', 'fabio.martini@example.com', 'hash5'),
    ('D', '6', 'Laura', 'Ferrari', '1979-12-09', 'F', 'laura.ferrari@example.com', 'hash6'),
    ('D', '7', 'Marco', 'Santoro', '1974-06-25', 'M', 'marco.santoro@example.com', 'hash7'),
    ('D', '8', 'Paola', 'Gallo', '1983-04-14', 'F', 'paola.gallo@example.com', 'hash8'),
    ('D', '9', 'Luca', 'Lombardi', '1981-08-30', 'M', 'luca.lombardi@example.com', 'hash9'),
    ('D', '10', 'Francesca', 'Conti', '1977-01-12', 'F', 'francesca.conti@example.com', 'hash10');

-- Inserisci dati per la tabella "docenti"
INSERT INTO docenti (cod_docente)
VALUES
    ('1'),
    ('2'),
    ('3'),
    ('4'),
    ('5'),
    ('6'),
    ('7'),
    ('8'),
    ('9'),
    ('10');

--#endregion


--#region DATI ESAMI

-- Esami (anche questi non li ha generati ChatGPT, soprattutto perché sono tutti esami che abbiamo anche noi)
INSERT INTO esami (cod_esame, nome_corso, descrizione_corso, anno, cfu, cod_presidente, cod_corso_laurea)
VALUES
    ('E1', 'Matematica 1', 'Fondamenti di matematica', 1, 6, '1', 'CT3'),
    ('E2', 'Fisica 1', 'Principi della fisica classica', 1, 6, '4', 'CT3'),
    ('E3', 'Informatica 1', E'Introduzione all\'informatica', 1, 9, '6', 'CT3'),
    ('E4', 'Chimica', 'Introduzione alla chimica', 1, 6, '8', 'CT3'),
    ('E5', 'Ingegneria del Software', E'Principi dell\'ingegneria del software', 2, 9, '9', 'CT3'),
    ('E6', 'Sistemi Operativi', 'Fondamenti dei sistemi operativi', 2, 9, '2', 'CT3'),
    ('E7', 'Elettrotecnica', 'Principi di elettrotecnica', 2, 6, '3', 'CT3'),
    ('E8', 'Analisi dei Dati', 'Metodi di analisi dei dati', 3, 9, '5', 'CT3'),
    ('E9', 'Reti di Calcolatori', 'Introduzione alle reti di calcolatori', 3, 6, '7', 'CT3'),
    ('E10', 'Progettazione dei Circuiti', 'Progettazione di circuiti elettronici', 3, 9, '10', 'CT3');


INSERT INTO esami_anni_accademici
VALUES
    ('E1', 2023),
    ('E2', 2023),
    ('E3', 2023),
    ('E4', 2023),
    ('E5', 2023),
    ('E6', 2023),
    ('E7', 2023),
    ('E8', 2023),
    ('E9', 2023),
    ('E10', 2023);


-- Inserisci dati delle prove
INSERT INTO prove (cod_prova, tipo_prova, denominazione_prova, descrizione_prova, cod_anno_accademico, peso, scadenza, cod_esame, cod_docente)
VALUES
    ('P1', 'Scritto', E'Esame Matematico Avanzato', 'Un esame scritto impegnativo per testare le tue abilità matematiche.', 2023, 0.5, '2024-01-01', 'E1', '1'),
    ('P2', 'Orale', E'Discussione dei Principi della Fisica', E'Un esame orale coinvolgente per discutere i principi della fisica.', 2023, 0.2, '2024-02-01', 'E1', '2'),
    ('P3', 'Pratico', E'Applicazione delle Teorie Matematiche', E'Un esame pratico che richiede l\'applicazione delle teorie matematiche.', 2023, 0.3, '2024-03-01', 'E1', '3'),

    ('P4', 'Scritto', E'Comprensione della Fisica Classica', E'Un esame scritto completo per valutare la comprensione della fisica classica.', 2023, 0.7, '2024-04-01', 'E2', '4'),
    ('P5', 'Orale', E'Discussione sui Principi della Fisica', E'Un esame orale coinvolgente per discutere i principi della fisica.', 2023, 0.3, '2024-05-01', 'E2', '5'),

    ('P6', 'Scritto', E'Valutazione delle Competenze Informatiche', E'Un esame scritto impegnativo per valutare le tue competenze informatiche.', 2023, 0.5, '2024-06-01', 'E3', '6'),
    ('P7', 'Orale', E'Discussione dei Concetti Informatici Fondamentali', E'Un esame orale coinvolgente per discutere i concetti informatici fondamentali.', 2023, 0.5, '2024-07-01', 'E3', '7'),

    ('P8', 'Scritto', E'Comprensione dei Concetti Chimici di Base', E'Un esame scritto completo per valutare la comprensione dei concetti chimici di base.', 2023, 1, '2024-08-01', 'E4', '8'),

    ('P9', 'Scritto', E'Conoscenza dell\'Ingegneria del Software', E'Un esame scritto impegnativo per testare la tua conoscenza dell\'ingegneria del software.', 2023, 0.6, '2024-09-01', 'E5', '9'),
    ('P10', 'Orale', E'Discussione dei Principi dell\'Ingegneria del Software', E'Un esame orale coinvolgente per discutere i principi dell\'ingegneria del software.', 2023, 0.4, '2024-10-01', 'E5', '10'),

    ('P11', 'Scritto', E'Comprensione dei Sistemi Operativi', E'Un esame scritto impegnativo per testare la tua comprensione dei sistemi operativi.', 2023, 0.8, '2024-11-01', 'E6', '1'),
    ('P12', 'Orale', E'Discussione dei Fondamenti dei Sistemi Operativi', E'Un esame orale coinvolgente per discutere i fondamenti dei sistemi operativi.', 2023, 0.2, '2024-12-01', 'E6', '2'),

    ('P13', 'Scritto', E'Comprensione dei Principi di Elettrotecnica', E'Un esame scritto completo per valutare la comprensione dei principi di elettrotecnica.', 2023, 0.5, '2024-01-01', 'E7', '3'),
    ('P14', 'Orale', E'Discussione dei Concetti di Base dell\'Elettrotecnica', E'Un esame orale coinvolgente per discutere i concetti di base dell\'elettrotecnica.', 2023, 0.5, '2024-02-01', 'E7', '4'),

    ('P15', 'Scritto', E'Analisi Avanzata dei Dati', E'Un esame scritto impegnativo per testare le tue abilità di analisi dei dati.', 2023, 0.5, '2024-03-01', 'E8', '5'),
    ('P16', 'Orale', E'Discussione sui Metodi di Analisi dei Dati', E'Un esame orale coinvolgente per discutere i metodi di analisi dei dati.', 2023, 0.5, '2024-04-01', 'E8', '6'),

    ('P17', 'Scritto', E'Comprensione delle Reti di Calcolatori', E'Un esame scritto completo per valutare la comprensione delle reti di calcolatori.', 2023, 0.6, '2024-05-01', 'E9', '7'),
    ('P18', 'Orale', E'Discussione dei Concetti Introduttivi sulle Reti di Calcolatori', E'Un esame orale coinvolgente per discutere i concetti introduttivi sulle reti di calcolatori.', 2023, 0.4, '2024-06-01', 'E9', '8'),

    ('P19', 'Scritto', E'Progettazione di Circuiti Elettronici', E'Un esame scritto impegnativo per testare la progettazione di circuiti elettronici.', 2023, 0.5, '2024-07-01', 'E10', '9'),
    ('P20', 'Orale', E'Discussione sulla Progettazione dei Circuiti Elettronici', E'Un esame orale coinvolgente per discutere la progettazione dei circuiti elettronici.', 2023, 0.5, '2024-08-01', 'E10', '10');



-- Inserimento dati nella tabella degli appelli
INSERT INTO appelli (cod_appello, data_appello, cod_prova, aula)
VALUES
    ('App1', '2023-11-15', 'P1', 'Aula 1'),
    ('App2', '2023-11-17', 'P2', 'Aula 2'),
    ('App3', '2023-11-20', 'P3', 'Aula 3'),
    ('App4', '2023-11-15', 'P4', 'Aula 1'),
    ('App5', '2023-11-17', 'P5', 'Aula 2'),
    ('App6', '2023-11-20', 'P6', 'Aula 3'),
    ('App7', '2023-11-15', 'P7', 'Aula 1'),
    ('App8', '2023-11-17', 'P8', 'Aula 2'),
    ('App9', '2023-11-20', 'P9', 'Aula 3'),
    ('App10', '2023-11-15', 'P10', 'Aula 1'),
    ('App11', '2023-11-17', 'P11', 'Aula 2'),
    ('App12', '2023-11-20', 'P12', 'Aula 3'),
    ('App13', '2023-11-15', 'P13', 'Aula 1'),
    ('App14', '2023-11-17', 'P14', 'Aula 2'),
    ('App15', '2023-11-20', 'P15', 'Aula 3'),
    ('App16', '2023-11-15', 'P16', 'Aula 1'),
    ('App17', '2023-11-17', 'P17', 'Aula 2'),
    ('App18', '2023-11-20', 'P18', 'Aula 3'),
    ('App19', '2023-11-15', 'P19', 'Aula 1'),
    ('App20', '2023-11-17', 'P20', 'Aula 2');


INSERT INTO iscrizioni_appelli (cod_appello, matricola, data_iscrizione)
VALUES
    ('App1', '11', NOW() - INTERVAL '3 days'),
    ('App1', '12', NOW() - INTERVAL '2 days'),
    ('App2', '13', NOW() - INTERVAL '1 days'),
    ('App2', '14', NOW() - INTERVAL '1 days'),
    ('App3', '15', NOW() - INTERVAL '2 days'),
    ('App3', '16', NOW() - INTERVAL '3 days'),
    ('App4', '17', NOW() - INTERVAL '1 days'),
    ('App4', '18', NOW() - INTERVAL '2 days'),
    ('App5', '19', NOW() - INTERVAL '3 days'),
    ('App5', '20', NOW() - INTERVAL '1 days');


INSERT INTO voti_prove (cod_appello, matricola, voto)
VALUES
    ('App1', '11', 18),
    ('App1', '12', 22),
    ('App2', '13', 25),
    ('App2', '14', 20),
    ('App3', '15', 28),
    ('App3', '16', 31),
    ('App4', '17', 19),
    ('App4', '18', 24),
    ('App5', '19', 27),
    ('App5', '20', 21);

--#endregion

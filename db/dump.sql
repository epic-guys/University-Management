DROP TABLE IF EXISTS esami CASCADE ;
CREATE TABLE esami (
    cod_esame TEXT NOT NULL PRIMARY KEY,
    nome_corso TEXT NOT NULL,
    anno INT NOT NULL,
    cfu INT NOT NULL
);

DROP TABLE IF EXISTS ruoli;
CREATE TABLE ruoli (
    ruolo CHAR(1) NOT NULL PRIMARY KEY
);

DROP TABLE IF EXISTS persone CASCADE;
CREATE TABLE persone (
    ruolo CHAR(1) NOT NULL,
    cod_persona TEXT NOT NULL,
    nome TEXT NOT NULL,
    cognome TEXT NOT NULL,
    data_nascita DATE NOT NULL,
    sesso CHAR(1) CHECK ( sesso IN ('M', 'F') ),
    email TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    FOREIGN KEY (ruolo) REFERENCES ruoli(ruolo),
    PRIMARY KEY (ruolo, cod_persona)
);

DROP TABLE IF EXISTS studenti;
CREATE TABLE studenti (
    matricola TEXT NOT NULL PRIMARY KEY ,
    FOREIGN KEY (matricola) REFERENCES Persone (cod_persona)
                      ON UPDATE CASCADE
                      ON DELETE CASCADE
);

DROP TABLE IF EXISTS docenti;
CREATE TABLE docenti (
    cod_docente TEXT NOT NULL PRIMARY KEY,
    FOREIGN KEY (cod_docente) REFERENCES Persone (cod_persona)
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

DROP TABLE IF EXISTS prove;
CREATE TABLE prove (
    cod_prova TEXT NOT NULL PRIMARY KEY,
    scadenza DATE DEFAULT NULL,
    cod_esame TEXT NOT NULL,
    FOREIGN KEY (cod_esame) REFERENCES Esami(cod_esame)
                   ON UPDATE CASCADE
                   ON DELETE CASCADE
);

DROP TABLE IF EXISTS appelli;
CREATE TABLE appelli(
    data DATE NOT NULL PRIMARY KEY,
    cod_prova TEXT NOT NULL,
    FOREIGN KEY (cod_prova) REFERENCES Prove(cod_prova)
                    ON UPDATE CASCADE
                    ON DELETE CASCADE
);


-- Data

INSERT INTO persone VALUES
                        ('P', 'P01','Alvise','Spanò','03-07-67','M', 'P01@unive.it', 'password'),
                        ('P','P02', 'Stefano', 'Calzavara', '01-02-69', 'M', 'P02@unive.it', 'password');

INSERT INTO docenti VALUES
                        ('P01'),
                        ('P02');

INSERT INTO ruoli VALUES
                      ('P'),
                      ('S');
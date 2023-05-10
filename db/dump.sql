DROP TABLE IF EXISTS Esami;
CREATE TABLE Esami (
    cod_esame TEXT NOT NULL PRIMARY KEY,
    nome_corso TEXT NOT NULL,
    anno INT NOT NULL,
    cfu INT NOT NULL
);

DROP TABLE IF EXISTS Persone;
CREATE TABLE Persone (
    cod_persona TEXT NOT NULL PRIMARY KEY,
    nome TEXT NOT NULL,
    cognome TEXT NOT NULL,
    data_nascita DATE NOT NULL,
    sesso CHAR(1) CHECK ( sesso IN ('M', 'F') )
);

DROP TABLE IF EXISTS Studenti;
CREATE TABLE Studenti (
    matricola TEXT NOT NULL PRIMARY KEY,
    cod_persona TEXT NOT NULL,
    FOREIGN KEY (cod_persona) REFERENCES Persone (cod_persona)
                      ON UPDATE CASCADE
                      ON DELETE CASCADE
);

DROP TABLE IF EXISTS Docenti;
CREATE TABLE Docenti (
    cod_prof TEXT NOT NULL PRIMARY KEY,
    cod_persona TEXT NOT NULL,
    FOREIGN KEY (cod_persona) REFERENCES Persone (cod_persona)
                     ON UPDATE CASCADE
                     ON DELETE CASCADE
);

DROP TABLE IF EXISTS Esami;
CREATE TABLE Esami (
    cod_esame TEXT NOT NULL PRIMARY KEY,
    nome_corso TEXT NOT NULL,
    anno INT NOT NULL,
    cfu INT NOT NULL
);

DROP TABLE IF EXISTS Prove;
CREATE TABLE Prove (
    cod_prova TEXT NOT NULL PRIMARY KEY,
    scadenza DATE DEFAULT NULL,
    cod_esame TEXT NOT NULL,
    FOREIGN KEY (cod_esame) REFERENCES Esami(cod_esame)
                   ON UPDATE CASCADE
                   ON DELETE CASCADE
);

DROP TABLE IF EXISTS Appelli;
CREATE TABLE Appelli(
    data DATE NOT NULL PRIMARY KEY,
    cod_prova TEXT NOT NULL,
    FOREIGN KEY (cod_prova) REFERENCES Prove(cod_prova)
                    ON UPDATE CASCADE
                    ON DELETE CASCADE
);
# Progetto di Basi di Dati 2022-2023
## Sicurezza
### XSS
Per mitigare Cross-Site Scripting (XSS) sono state adottate le seguenti misure:
* Utilizzo di [Jinja2](https://jinja.palletsprojects.com/en/3.0.x/) per la generazione dinamica delle pagine HTML.
* La libreria [DataTables](https://datatables.net/), fornisce dei metodi renderer che fanno escaping dei dati inseriti 
nelle celle delle tabelle.
* Regex nelle primary key delle tabelle, per forzare un pattern specifico. Questo approccio è stato deciso perché
le primary key vengono spesso utilizzate nella formazione di URL. Le regex sono state inserite direttamente nella
dichiarazione della tabella, nel DBMS.

### SQL Injection
Attraverso la libreria [SQLAlchemy](https://www.sqlalchemy.org/) è stato adottato il pattern
[ORM](https://en.wikipedia.org/wiki/Object-relational_mapping) che associa le entità del database a classi Python.
Le query quindi sono effettuate attraverso metodi della libreria e non con query SQL dirette. SQLAlchemy
genera le query SQL in modo sicuro, evitando SQL Injection.

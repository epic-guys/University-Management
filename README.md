# Progetto di Basi di Dati 2022-2023
## Database
TODO

## SQLAlchemy
[SQLAlchemy](https://www.sqlalchemy.org/) è una potente libreria Python che permette di interfacciarsi a un database
in più modi.
I vantaggi principali di questa libreria sono:
* Compatibilità con più driver database: capitano alcune volte in cui si vuole migrare il database a un 
altro DBMS per alcune ragioni. SQLAlchemy 
* [Object Relational Mapping](https://en.wikipedia.org/wiki/Object-relational_mapping): ORM è un design pattern
che mappa le relazioni di un database a delle classi del linguaggio di programmazione, chiamate **Modelli**.
L'utilizzo dei modelli ha due grossi vantaggi:
  * Sincronizzazione dei dati tra i dati nel backend e quelli del database.
  * Essendo i modelli delle classi, gli si può implementare qualsiasi comportamento all'interno dell'app.
  * 

## Autenticazione
L'autenticazione è stata implementata con la libreria [Flask-Login](https://flask-login.readthedocs.io/en/latest/).
Viene data per scontata già la presenza degli utenti, quindi la registrazione non è stata implementata.
Flask-Login è stato impostato in modo che carichi gli utenti dal database tramite SQLAlchemy.

## Autorizzazione
L'autorizzazione è stata implementata attraverso il modulo flask_roles, sviluppato appositamente per questo progetto.
Questo modulo fornisce due componenti principali:
* Una classe chiamata `RoleManager`.
* Un mixin `RoleMixin` per definire un utente da controllare. 

### Role manager
Lo scopo di questa classe è di salvare il metodo `role_loader` con cui essa deve caricare l'utente di cui
si vuole controllare il ruolo.
Una volta salvato questo metodo, si può utilizzare il suo decoratore `@roles` sulle view dell'applicazione.

Questo decoratore prende in input delle classi che estendono `RoleMixin`.
Una volta che viene chiamato il metodo decorato, il decoratore utilizza `role_loader` per caricare l'utente attuale,
quindi controlla se questo utente è sottoclasse di almeno una delle classi specificata nel decoratore.
Se le classi corrispondono, allora l'utente ha il ruolo corretto per accedere e l'accesso procede correttamente.
Se invece l'utente non ha nessuno dei ruoli specificati, allora non è autorizzato ad accedere e viene reindirizzato
a una delle pagine definite nel roles manager.


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

# Installazione CKAN 2.8.4 + DCATAPIT + Plugin Lait

## Prerequisiti

 1. Python (almeno v2.7.9) con abilitato il supporto alle librerie condivise (files *.so)
 2. git (almeno v1.7.1)
 3. Apache (almeno v2.2.15)
 4. Tool RedHat per sviluppatori (yum install "Development Tools" o equivalente)
 5. Accesso un server PostgreSQL, con inidirizzo IP e 2 utenze, una per il db ckan e l'altra per il datastore
 6. Accesso ad un server SOLR (almeno v6.6.6)
 7. Accesso ad un server REDIS (almeno v3.2.12)

## Installazione / aggiornamento CKAN

Nelle seguenti istruzioni si fa riferimento ad un utente di sistema ``ckan`` che abbia come gruppo primario ``ckan`` ed home directory ``/opt/opendata/ckan``. Se necessario fare riferimento all'utente e directory prescelta al momento dell'installazione.

 1. Creare una direcotry per l'installazione ed il virtual environment python

    ```
    cd
    mkdir ckan28
    cd ckan28
    ```

2. Clonare il repository ,creare il virtual environment python, attivarlo ed aggiornarlo

    ```
    git clone https://github.com/lynxlab/ckan28-lazio.git
    virtualenv --no-site-packages /opt/opendata/ckan/ckan28-lazio/ckan28
    cd ckan28
    . bin/activate
    pip install --upgrade pip
    pip install --upgrade setuptools wheel
    ```

    **ATTENZIONE**: da questo punto in poi, per tutti i comandi di tipo pip, paster, python si assume che il virtual environment ckan28 sia stato attivato.

3. Installare e compilare i sorgenti ckan

    ```
    pip install -r requirements.txt
    ```

    Se ci fossero problemi nella compilazione del modulo wsgi per apache probabilmente python non è configurato per supportare le libreire condivise, fare rieferimento alla sezione Note di questo file per possibili aiuti.
    Potrebbe essere necessario installare il pacchetto ```httpd-devel``` (yum install httpd-devel)

4. Configurare il file ```etc/production.ini``` facendo massima attenzione alle credenziali di accesso ai DB, a tutte le url coinvolte (solr, redis, etc...) ed alle directory di filesystem necessarie (storage_path, files *.ini, etc...).

5. Se necessario, creare un nuovo core di solr oppure usare quello esistente, in ogni caso copiare i files ```solr-config/solrconfig.xml``` e ```solr-config/schema.xml``` nella directory di configurazione del core di solr, da cui è necessario anche rinominare il file ```managed-schema``` in un nome a piacere, ad esempio ```managed-schema.disabled```

6. Eseguire l'aggiornamento del database ckan alla versione 2.8.4

    ```
    cd src/ckan
    paster db upgrade -c ../../etc/production.ini
    ```

7. Configurazione plugin spatial

    ```
    paster --plugin=ckanext-spatial spatial initdb 4326 --config=../../etc/production.ini
    ```

8. Creazione tabelle plugin multilang

    ```
    paster --plugin=ckanext-multilang multilangdb initdb --config=../../etc/production.ini
    ```

9. Ricostruzione indice SOLR

    Per via di alcuni bug in ckan, è necessario commentare i plugin ```multilingual_group```, ```multilingual_tag``` dal file di configurazione, dopo averlo fatto:

    ```
    paster --plugin=ckan search-index rebuild --config=../../etc/production.ini
    ```

    Decommentare i plugin commentati in precedenza.

10. Configurare apache per usare il modulo wsgi compilato al punto 3 ed il virtualhost per ckan

    Modifcare il file ```/opt/opendata/ckan/ckan28-lazio/ckan28/etc/ckan28.wsgi``` scrivendo a riga 3 il path assoulto in uso.

    Commentare l'unica riga presente ed aggiunre ```LoadModule wsgi_module /opt/opendata/ckan/ckan28-lazio/ckan28/lib/python2.7/site-packages/mod_wsgi/server/mod_wsgi-py27.so``` al file  ```/etc/httpd/conf.d/wsgi.conf```.

    _Nota_: La posizione del file e/o la direttiva LoadModule wsgi_module potrebbero variare dipendentemente dall'installazione di apache.

    Modificare il file ```etc/httpd/conf.d/mod_jk.conf``` sostiuendo percorsi e nome utente/gruppo giusti, ad esempio

    ```
    WSGIScriptAlias /catalog /opt/opendata/ckan/ckan28-lazio/ckan28/etc/ckan28.wsgi
    ```

    e

    ```
    WSGIDaemonProcess ckan_produzione display-name=ckan_produzione processes=2 threads=15 user=ckan group=ckan
    ```

    _Nota_: Fare attenzione ad usare i percorsi di file e nome/utente gruppo corretti.
    La posizione del file e/o le configurazioni WSGIScriptAlias, WSGIDaemonProcess potrebbero variare dipendentemente dall'installazione di apache.

    Riavviare di apache.

11. Fare login in ckan (alla url configurata nel file production.ini) e dall'interfaccia web creare i seguenti gruppi:

| url | Nome |
|-----|------|
|cultura | Cultura|
|agricoltura-pesca | Agricoltura e pesca|
|ambiente | Ambiente|
|attivita-produttive | Attività produttive|
|finanze-patrimonio | Finanze|
|mobilita-infrastrutture | Mobilità e infrastrutture|
|politiche-sociali-giovanili | Politiche sociali e giovanili|
|sanita | Sanità|
|territorio | Territorio|
|turismo-sport | Turismo, sport e tempo libero|
|formazione-lavoro | Formazione e lavoro|
|pubblica-amministrazione | Istituzioni e politica|

12. Creazione e popolazione tabelle plugin dcatapit

    ```
    cd /opt/opendata/ckan/ckan28-lazio/ckan28/src/ckanext-dcatapit

    paster --plugin=ckanext-dcatapit vocabulary initdb --config=../../etc/production.ini

    paster --plugin=ckanext-dcatapit vocabulary load --url "https://op.europa.eu/o/opportal-service/euvoc-download-handler?cellarURI=http%3A%2F%2Fpublications.europa.eu%2Fresource%2Fcellar%2Fe887963f-d894-11e9-9c4e-01aa75ed71a1.0001.05%2FDOC_1&fileName=languages-skos.rdf" --name languages --config=../../etc/production.ini

    paster --plugin=ckanext-dcatapit vocabulary load --url "https://op.europa.eu/o/opportal-service/euvoc-download-handler?cellarURI=http%3A%2F%2Fpublications.europa.eu%2Fresource%2Fcellar%2F8e06fe1d-261d-11e8-ac73-01aa75ed71a1.0001.02%2FDOC_1&fileName=data-theme-skos.rdf" --name eu_themes --config=../../etc/production.ini

    paster --plugin=ckanext-dcatapit vocabulary load --url "https://op.europa.eu/o/opportal-service/euvoc-download-handler?cellarURI=http%3A%2F%2Fpublications.europa.eu%2Fresource%2Fcellar%2F3306cc97-4366-11ea-b81b-01aa75ed71a1.0001.02%2FDOC_1&fileName=places-skos.rdf" --name places --config=../../etc/production.ini

    paster --plugin=ckanext-dcatapit vocabulary load --url "https://op.europa.eu/o/opportal-service/euvoc-download-handler?cellarURI=http%3A%2F%2Fpublications.europa.eu%2Fresource%2Fcellar%2Fe20301fe-928e-11e9-9369-01aa75ed71a1.0001.02%2FDOC_1&fileName=frequencies-skos.rdf" --name frequencies --config=../../etc/production.ini

    paster --plugin=ckanext-dcatapit vocabulary load --url "https://op.europa.eu/o/opportal-service/euvoc-download-handler?cellarURI=http%3A%2F%2Fpublications.europa.eu%2Fresource%2Fcellar%2F2c036d46-6891-11ea-b735-01aa75ed71a1.0001.04%2FDOC_1&fileName=filetypes-skos.rdf"  --name filetype --config=../../etc/production.ini

    paster --plugin=ckanext-dcatapit vocabulary load --filename ../../etc/regions.rdf --name regions --config=../../etc/production.ini

    paster --plugin=ckanext-dcatapit vocabulary load --filename examples/eurovoc_mapping.rdf --name subthemes --config=../../etc/production.ini examples/eurovoc.rdf

    paster --plugin=ckanext-dcatapit vocabulary load --filename examples/licenses.rdf --name licenses --config=../../etc/production.ini
    ```

13. Far girare lo script lynx che relizza le mappature categoria => tema e gruppo

    ```
    cd /opt/opendata/ckan/ckan28-lazio/scritps
    ```

    configurare lo script modificando il file ```conf.ini``` con le informazioni necessarie

    ```
    python dbrepair_script.py map-themes
    ```

    controllare che non ci siano errori e che non siano stati creati file di errore come descritto in ```cd /opt/opendata/ckan/ckan28-lazio/scritps/README.md```. Se tutto è andato bene, rendere persistenti le modifiche:

    ```
    python dbrepair_script.py map-themes commit
    ```

## Installazione/configurazione datapusher

1. Disattivare il virtualenvironment ckan28, crearne uno per il datapusher ed attivarlo

    ```
    cd
    deactivate
    virtualenv --no-site-packages /opt/opendata/ckan/ckan28-lazio/datapusher
    cd datapusher
    . bin/activate
    pip install --upgrade pip
    pip install --upgrade setuptools wheel
    ```
    **ATTENZIONE**: da questo punto in poi, per tutti i comandi di tipo pip, paster, python si assume che il virtual environment ckan28 sia stato attivato.

2. Installare il datapusher

    ```
    pip install -r requirements.txt
    ```

3. Configurare il virtualhost per il datapusher

    Modifcare il file ```/opt/opendata/ckan/ckan28-lazio/datapusher/etc/datapusher.wsgi``` scrivendo a righe 5 e 9 il path assoulto in uso.

    Modificare il file ```etc/httpd/conf.d/datapusher.conf``` sostiuendo percorsi e nome utente/gruppo giusti, ad esempio

    ```
    WSGIScriptAlias / /opt/opendata/ckan//ckan28-lazio/datapusher/etc/datapusher.wsgi
    ```

    e

    ```
    WSGIDaemonProcess datapusher display-name=datapusher processes=1 threads=15 user=ckan group=ckan
    ```

    _Nota_: Fare attenzione ad usare i percorsi di file e nome/utente gruppo corretti.
    La posizione del file e/o le configurazioni WSGIScriptAlias, WSGIDaemonProcess potrebbero variare dipendentemente dall'installazione di apache.

    Riavviare di apache.

4. Testare il datapusher (opzionale)

    ```
    curl http://127.0.0.1:8800
    ```
## Passi conclusivi

1. Disattivare il virtualenvironment datapusher attivare ckan28

    ```
    deactivate
    cd /opt/opendata/ckan/ckan28-lazio/ckan28
    . bin/activate
    cd src/ckan
    ```

2. Resubmit di tutte le risorse al datapusher

    Per via di alcuni bug in ckan, è necessario commentare i plugin ```multilingual_group```, ```multilingual_tag``` dal file di configurazione

    ```
    paster --plugin=ckan datapusher resubmit -c ../../etc/production.ini
    ```

3. Creazione/aggiornamento delle viste delle risorse

    Per via di alcuni bug in ckan, è necessario commentare i plugin ```multilingual_group```, ```multilingual_tag``` dal file di configurazione

    ```
    paster views create --config=../../etc/production.ini
    ```

4. Ricostruzione indice SOLR

    Per via di alcuni bug in ckan, è necessario commentare i plugin ```multilingual_group```, ```multilingual_tag``` dal file di configurazione

    ```
    paster --plugin=ckan search-index rebuild --config=../../etc/production.ini

    ```

5. Decommentare i plugin commentati in precedenza.


### Note

1. Compilazione, installazione di python2.7.9 e mod_wsgi

    ```
    # ./configure --enable-shared
    # make altinstall
    ```

    Ci potrebbero dei problemi relativi ai percori di installazione delle librerie condivise di python, capire dove il sistema le cerca e fare un link simbolico, ad esempio:

    ```
    # ln -s /usr/local/lib/libpython2.7.so.1.0 /usr/lib64/
    ```

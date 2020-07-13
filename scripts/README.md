# dbrepair_script.py

- _dd-TABLENAME_: delete duplicate rows from table TABLENAME (es: -dd-mytable)
- _add-tags_: add to table tag_old ther rows from table tag where vocabulary_id is not null
- _map-themes_: map all package with category or category_id extra_field to the corresponding theme and add the package to the corresponding group (if not already present)
- _commit_: commit all changes (preferable to run once without commit, if all works well then run with commit)

## Notes:

- Rename table tag to tag_old and delete table vocabulary
- Change conf.ini with ip-address of the postgres server, db name, user and password.
- The order of the parameters does not matter.
- Check the presence, in folder scripts, of txt files ```*_failed_*.txt```: they contain the failed postgresql queries (selection or insertion).

**Important**: Before run map-themes check the existence of the correct groups:
1. "cultura"
2. "agricoltura-pesca"
3. "ambiente"
4. "attivita-produttive"
5. "finanze-patrimonio"
6. "mobilita-infrastrutture"
7. "politiche-sociali-giovanili"
8. "pubblica-amministrazione"
9. "sanita"
10. "territorio"
11. "turismo-sport"
12. "formazione-lavoro"

(sql query: select name from "group" where is_organization=false)
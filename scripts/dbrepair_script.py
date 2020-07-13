import psycopg2
from psycopg2 import sql
from config import config
import json
import uuid
import sys

jobs_to_run = sys.argv[1:]

category_theme_dict = {'agricoltura-pesca': 'AGRI', 'cultura': 'EDUC', 'ambiente-meteo': 'ENVI',
                       'attivita-produttive': 'ECON', 'bilanci-pagamenti': 'ECON', 'mobilita-transporti': 'TRAN',
                       'politiche-sociali-giovanili': 'SOCI', 'sanita': 'HEAL', 'territorio-urbanistica': 'REGI',
                       'turismo-sport':'EDUC',
                       'lavoro': 'SOCI', 'formazione': 'SOCI',
                       'istituzioni-politica': 'SOCI', 'istruzione-ricerca': 'SOCI', 'bandi-concorso': 'SOCI',
                       'tasse-tributi': 'ECON', 'opere-pubbliche': 'ECON', 'finanziamenti-pubblici': 'ECON',
                       'beni-gestione': 'ECON', 'normativa-atti': 'GOVE'}



query_dict = {'dcatapit_license_old': """insert into dcatapit_license_old
    (id, license_type, version, uri, path, document_uri, rank_order, default_name, parent_id) values 
    (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                  'dcatapit_localized_license_name_old': """insert into dcatapit_localized_license_name_old
    (id, license_id, lang, label) values 
    (%s, %s, %s, %s)""",
                  'dcatapit_subtheme_old': """insert into dcatapit_subtheme_old
    (id, version, identifier, uri, default_label, parent_id, depth, path) values 
    (%s, %s, %s, %s, %s, %s, %s, %s)""",
                  'dcatapit_subtheme_labels_old': """insert into dcatapit_subtheme_labels_old
    (id, subtheme_id, lang, label) values 
    (%s, %s, %s, %s)""",
                  'dcatapit_theme_to_subtheme_old': """insert into dcatapit_theme_to_subtheme_old
    (id, tag_id, subtheme_id) values 
    (%s, %s, %s)""",
                  'dcatapit_vocabulary_old': """insert into dcatapit_vocabulary_old
    (id, tag_id, tag_name, lang, text) values 
    (%s, %s, %s, %s, %s)""",
                  'tag_old': """insert into tag_old
    (id, name, vocabulary_id) values 
    (%s, %s, %s)""",
                  'vocabulary_old': """insert into vocabulary_old
    (id, name) values 
    (%s, %s)""",
          'dcatapit_license': """insert into dcatapit_license
    (id, license_type, version, uri, path, document_uri, rank_order, default_name, parent_id) values 
    (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
          'dcatapit_localized_license_name': """insert into dcatapit_localized_license_name
    (id, license_id, lang, label) values 
    (%s, %s, %s, %s)""",
          'dcatapit_subtheme': """insert into dcatapit_subtheme
    (id, version, identifier, uri, default_label, parent_id, depth, path) values 
    (%s, %s, %s, %s, %s, %s, %s, %s)""",
          'dcatapit_subtheme_labels': """insert into dcatapit_subtheme_labels
    (id, subtheme_id, lang, label) values 
    (%s, %s, %s, %s)""",
          'dcatapit_theme_to_subtheme': """insert into dcatapit_theme_to_subtheme
    (id, tag_id, subtheme_id) values 
    (%s, %s, %s)""",
          'dcatapit_vocabulary': """insert into dcatapit_vocabulary
    (id, tag_id, tag_name, lang, text) values 
    (%s, %s, %s, %s, %s)""",
          'tag': """insert into tag
    (id, name, vocabulary_id) values 
    (%s, %s, %s)""",
          'vocabulary': """insert into vocabulary
    (id, name) values 
    (%s, %s)"""
              }

package_id_pos = 1
revision_id_pos = 4
state_id_pos = 5

def execute_jobs2(cursor):
    failed_member_insertions = []
    failed_extra_updates = []
    failed_theme_check = []

    # get categories (groups) id
    query = """select * from "group" where "is_organization"=false"""
    cursor.execute(query)
    try:
        group_list = cursor.fetchall()
    except psycopg2.ProgrammingError as e:
        raise RuntimeError('Cannot get group_list from DB: {}'.format(str(e)))
    category_group_dict = {}
    category_name_dict = {}
    for group_el in group_list:
        category_group_dict[group_el[2]] = group_el[0]
        category_name_dict[group_el[2]] = group_el[1]
    print 'category_id_dict'
    print category_group_dict
    print 'category_name_dict'
    print category_name_dict
    print 'group_list'
    print group_list
    for cat, cat_id in category_group_dict.items():
        print "cat:"
        print cat
        # query in table 'package_extra' all rows where key='category' and value=cat
        query = """select * from package_extra where key=%s and value=%s"""
        cursor.execute(query, ("category_id", str(category_name_dict[cat])))
        try:
            package_extra_cat = cursor.fetchall()
        except psycopg2.ProgrammingError:
            print 'error'
            continue

        for pkg_x in package_extra_cat:
            # check if exists in table 'member' a row where table_id=package_id and group_id=cat_id
            query = """select * from member where table_id=%s and group_id=%s and state=%s"""
            cursor.execute(query, (pkg_x[package_id_pos], cat_id, "active"))
            member_rows = cursor.fetchall()
            if len(member_rows) == 0:

                # if does not exists create and add to 'member'
                print 'inserting member'
                query = """insert into member(id, table_id, group_id, state, revision_id, table_name, capacity) 
                           values (%s, %s, %s, %s, %s, %s, %s);"""
                member_to_insert = (str(uuid.uuid4()), pkg_x[package_id_pos], cat_id, pkg_x[state_id_pos], pkg_x[revision_id_pos],
                                    'package', 'public')
                print member_to_insert
                try:
                    cursor.execute(query, member_to_insert)
                except psycopg2.ProgrammingError:
                    failed_member_insertions.append(member_to_insert)
            print 'member rows'
            print member_rows

            # check if the package is connected with a theme
            query = """select * from package_extra where package_id=%s and key=%s"""
            try:
                cursor.execute(query, (pkg_x[package_id_pos], 'theme'))
                if len(cursor.fetchall()) > 0:
                    continue
            except psycopg2.ProgrammingError as e:
                failed_theme_check.append(pkg_x)
                continue

            # add in 'package_extra' the new extra field 'theme' with value [{'subthemes'=[], 'theme'=category_theme_dict[cat]}]
            query = """insert into package_extra(id, package_id, key, value, revision_id, state) 
                                       values (%s, %s, %s, %s, %s, %s);"""
            extra_to_insert = (str(uuid.uuid4()), pkg_x[1], "theme",
                               json.dumps([{'subthemes': [], 'theme': category_theme_dict[category_name_dict[cat]]}]),
                               pkg_x[4], pkg_x[5])
            print 'inserting extra'
            print extra_to_insert
            try:
                cursor.execute(query, extra_to_insert)
            except psycopg2.ProgrammingError as e:
                print 'error'
                print str(e)
                failed_extra_updates.append(extra_to_insert)
    print 'finish!'
    return {'member': failed_member_insertions, 'extra': failed_extra_updates, 'theme': failed_theme_check}

def execute_jobs(cursor):
    failed_member_insertions = []
    failed_extra_updates = []

    # get categories (groups) id
    query = """select * from "group" where "is_organization"=false"""
    cursor.execute(query)
    try:
        group_list = cursor.fetchall()
    except psycopg2.ProgrammingError as e:
        raise RuntimeError('Cannot get group_list from DB: {}'.format(str(e)))
    category_id_dict = {}
    category_name_dict = {}
    for group_el in group_list:
        category_id_dict[group_el[2]] = group_el[0]
        category_name_dict[group_el[2]] = group_el[1]
    print 'category_id_dict'
    print category_id_dict
    print 'group_list'
    print group_list
    for cat, cat_id in category_id_dict.items():
        print "cat:"
        print cat
        # query in table 'package_extra' all rows where key='category' and value=cat
        query = """select * from package_extra where key=%s and value=%s"""
        cursor.execute(query, ("category", str(cat)))
        try:
            package_extra_cat = cursor.fetchall()
        except psycopg2.ProgrammingError:
            print 'error'
            continue
        for pkg_x in package_extra_cat:
            # check if exists in table 'member' a row where table_id=package_id and group_id=cat_id
            query = """select * from member where table_id=%s and group_id=%s and state=%s"""
            cursor.execute(query, (pkg_x[package_id_pos], cat_id, "active"))
            member_rows = cursor.fetchall()
            if len(member_rows) == 0:

                # if does not exists create and add to 'member'
                print 'inserting member'
                query = """insert into member(id, table_id, group_id, state, revision_id, table_name, capacity) 
                           values (%s, %s, %s, %s, %s, %s, %s);"""
                member_to_insert = (str(uuid.uuid4()), pkg_x[package_id_pos], cat_id, pkg_x[state_id_pos], pkg_x[revision_id_pos],
                                    'package', 'public')
                print member_to_insert
                try:
                    cursor.execute(query, member_to_insert)
                except psycopg2.ProgrammingError:
                    failed_member_insertions.append(member_to_insert)
            print 'member rows'
            print member_rows

            # add in 'package_extra' the new extra field 'theme' with value [{'subthemes'=[], 'theme'=category_theme_dict[cat]}]
            query = """insert into package_extra(id, package_id, key, value, revision_id, state) 
                                       values (%s, %s, %s, %s, %s, %s);"""
            extra_to_insert = (str(uuid.uuid4()), pkg_x[1], "theme",
                               json.dumps([{'subthemes': [], 'theme': category_theme_dict[category_name_dict[cat]]}]),
                               pkg_x[4], pkg_x[5])
            print 'inserting extra'
            print extra_to_insert
            try:
                cursor.execute(query, extra_to_insert)
            except psycopg2.ProgrammingError as e:
                print 'error'
                print str(e)
                failed_extra_updates.append(extra_to_insert)
    print 'finish!'
    return {'member': failed_member_insertions, 'extra': failed_extra_updates}


def add_tags(cursor):
    query = """select * from tag where vocabulary_id is not null"""
    try:
        cursor.execute(query)
        tags = cursor.fetchall()
        print tags
        query2 = """insert into tag_old(id, name, vocabulary_id) 
                                      values (%s, %s, %s);"""
        cursor.executemany(query2, tuple(tags))
    except psycopg2.ProgrammingError as e:
        print str(e)


def replace_to_old(cursor, table):
    if table == 'tag':
        query = "select * from {} where vocabulary_id is not null".format(table)
    else:
        query = "select * from {}".format(table)
    cursor.execute(query, ())
    data_tup = cursor.fetchall()

    print 'QUERY DATA:'
    for el in data_tup:
        print el

    if table != 'tag':
        query = "truncate {}_old cascade".format(table)
        cursor.execute(query, ())

    cursor.executemany(query_dict['{}_old'.format(table)], data_tup)
    print 'Finish to replace into old table {}'.format(table)


def delete_duplicates_from_table(cursor, table):
    query = "select * from {}".format(table)
    cursor.execute(query, ())
    duplicates_tup = cursor.fetchall()
    print 'duplicates:'
    print duplicates_tup
    to_insert = []
    for el in duplicates_tup:
        if el not in to_insert:
            to_insert.append(el)
    print 'to insert'
    for el in to_insert:
        print el
    query = "delete from {}".format(table)
    cursor.execute(query, ())
    cursor.executemany(query_dict[table], to_insert)


def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        # execute jobs

        # DELETE DUPLICATES FROM TABLES
        delete_duplicates_table_list = []
        # get tables name for which delete duplicates
        for job in jobs_to_run:
            if 'dd-' in job:
                delete_duplicates_table_list.append(job.split('-')[-1])
        # delete duplicates for each table
        for table in delete_duplicates_table_list:
            print 'deleting duplicates from tables: {}'.format(table)
            delete_duplicates_from_table(cursor=cur, table=table)
            #replace_to_old(cursor=cur, table=table)

        # ADD TAGS
        if 'add-tags' in jobs_to_run:
            add_tags(cursor=cur)

        # MAP DATASETS WITH CATEGORY TO THEME AND GROUP
        if 'map-themes' in jobs_to_run:
            failed = execute_jobs(cursor=cur)
            if len(failed['member']) > 0:
                with open('./member_failed.txt', 'w') as outfile:
                    json.dump(failed['member'], outfile)
            if len(failed['extra']) > 0:
                with open('./extra_failed.txt', 'w') as outfile:
                    json.dump(failed['extra'], outfile)
            print 'FAILED:'
            print failed

            failed = execute_jobs2(cursor=cur)
            if len(failed['member']) > 0:
                with open('./member_failed_2.txt', 'w') as outfile:
                    json.dump(failed['member'], outfile)
            if len(failed['extra']) > 0:
                with open('./extra_failed_2.txt', 'w') as outfile:
                    json.dump(failed['extra'], outfile)
            if len(failed['theme']) > 0:
                with open('./theme_check_failed.txt', 'w') as outfile:
                    json.dump(failed['theme'], outfile)

            print 'FAILED 2:'
            print failed

        # commit changes
        if 'commit' in jobs_to_run:
            conn.commit()

        # close the communication with the PostgreSQL
        cur.close()
    except psycopg2.DatabaseError as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


if __name__ == '__main__':
    connect()

#!/usr/bin/python
#-*- coding: utf-8 -*-

###########################################################
# © 2011 Daniel 'grindhold' Brendle and Team
#
# This file is part of Skarphed.
#
# Skarphed is free software: you can redistribute it and/or 
# modify it under the terms of the GNU Affero General Public License 
# as published by the Free Software Foundation, either 
# version 3 of the License, or (at your option) any later 
# version.
#
# Skarphed is distributed in the hope that it will be 
# useful, but WITHOUT ANY WARRANTY; without even the implied 
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
# PURPOSE. See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public 
# License along with Skarphed. 
# If not, see http://www.gnu.org/licenses/.
###########################################################

import re
import fdb
import time
import os

from skarphedcore.configuration import Configuration
from common.errors import DatabaseException
    

class Database(object):
    """
    The Database-Class handles the connection to a Firebird 2.5+ Database
    """
    _borgmind = {}
    def __init__(self):
        """
        The Database loads connectiondata to the database from the config of Core
        """
        self.__dict__ = Database._borgmind
        if self.__dict__ == {}:
            self._connection = None
            self._ip = None
            self._dbname = None
            self._user = None
            self._password = None

            self._queryCache = QueryCache()
            
            c = Configuration()
            self.set_ip(c.get_entry('db.ip'))
            self.set_db_name(c.get_entry('db.name'))
            self.set_user(c.get_entry('db.user'))
            self.set_password(c.get_entry('db.password'))
            self.connect()

    def connect(self):
        """
        The class actually connects to the database and stores the 
        connection in _connection
        """
        if None in (self._user, self._ip, self._dbname, self._password):
            raise DatabaseException(DatabaseException.get_msg(1))
            #TODO: Globally Definable DB-Path
        try:
            self._connection = fdb.connect(
                        host=self._ip, 
                        database='/var/lib/firebird/2.5/data/'+self._dbname,
                        user=self._user, 
                        password=self._password,
                        charset="UTF8")
        except fdb.fbcore.DatabaseError, e:
            raise DatabaseException(e.args[0])
        return

    def set_ip(self, ip):
        """
        trivial
        """
        self._ip = str(ip)

    def set_db_name(self, dbname):
        """
        trivial
        """
        self._dbname = str(dbname)

    def set_user(self, user):
        """
        trivial
        """
        self._user = str(user)

    def set_password(self, password):
        """
        trivial
        """
        self._password = str(password)

    def get_connection(self):
        """
        trivial
        """
        return self._connection

    def commit(self):
        """
        commits a pending transaction to the database
        """
        self._connection.commit()

    def query(self, statement, args=(), module=None, forceNoCache=False, commit=False):
        """
        execute a query on the database. be sure to deliver the module.
        it is necessary to determine tablenames
        """
        try:
            mutex = Configuration().get_entry("core.webpath")+"/db.mutex"

            if commit: #only if writing stuff
                while os.path.exists(mutex):
                    time.sleep(0.000001)

                os.mkdir(mutex)

            if self._connection is None:
                raise DatabaseException(DatabaseException.get_msg(2))
            if module is not None:
                statement = self._replace_module_tables(module,statement)
            cur = self._connection.cursor()    
            try:
                prepared, cur = self._queryCache(cur, statement)
                cur.execute(prepared,args)
            except fdb.fbcore.DatabaseError,e:
                raise DatabaseException(str(e))
            if commit:
                self.commit()
            return cur
        finally:
            if commit:
                os.rmdir(mutex)

    def _replace_module_tables(self, module, query):
        """
        replaces module-based tablenames like
         'de.grinhold.skarphed.news.news'
        with an actual SQL-table like
         'TAB_000004'
        """
        tagpattern = re.compile('\$\{[A-Za-z0-9.]+\}')
        matches = tagpattern.findall(query)
        matches = list(set(matches)) # making matches unique
        matches = map(lambda s: s[2:-1], matches)

        matchesRaw = list(matches)

        modules = [module.get_name()]

        for match in matches:
            splitted = match.split(".")
            if len(splitted) > 1:
                matches.append(splitted[-1])
                matches.remove(match)
                splitted.remove(splitted[-1])
                modules.append(".".join(splitted))

        tableQuery = """SELECT MDT_ID, MDT_NAME, MOD_NAME
                     FROM MODULETABLES 
                      INNER JOIN MODULES ON (MDT_MOD_ID = MOD_ID )
                     WHERE MOD_NAME IN (%s) 
                      AND MDT_NAME IN (%s) ;"""%("'"+"','".join(modules)+"'","'"+"','".join(matches)+"'")
        cur = self._connection.cursor()
        cur.execute(tableQuery)

        replacementsDone = []
        for res in cur.fetchallmap():
            pattern = "${"+res["MOD_NAME"]+"."+res["MDT_NAME"]+"}"
            tableId = str(res["MDT_ID"])
            tableId = "TAB_"+"0"*(6-len(tableId))+tableId
            query = query.replace(pattern, tableId)
            replacementsDone.append(res["MOD_NAME"]+"."+res["MDT_NAME"])
            if res["MOD_NAME"] == module.get_name():
                query = query.replace("${"+res["MDT_NAME"]+"}", tableId)

        if len(matchesRaw) != len(replacementsDone):
            for replacement in replacementsDone:
                matchesRaw.remove(replacement)
            raise DatabaseException(DatabaseException.get_msg(3,str(matchesRaw)))
        return query

    def get_seq_next(self,sequenceId):
        """
        Yields the next value of a given sequence (e.g. 'MOD_GEN') 
        and increments it
        if the sequence contains a "$"-character, tries to resolve name of table
        """
        cur = self._connection.cursor()
        if sequenceId.startswith("${"):
            statement = "SELECT MDT_ID FROM MODULETABLES INNER JOIN MODULES ON MOD_ID = MDT_MOD_ID WHERE MOD_NAME = ? AND MDT_NAME = ? ;"
            args = tuple(sequenceId[2:-1].split("."))
            cur.execute(statement, args)
            res = cur.fetchone()
            seqnum = str(res[0])
            sequenceId = "SEQ_"+"0"*(6-len(seqnum))+seqnum
        statement = "SELECT GEN_ID ( %s , 1) FROM RDB$DATABASE ;"%str(sequenceId)
        cur.execute(statement)
        res = cur.fetchone()
        return res[0]

    def get_seq_current(self,sequenceId):
        """
        Yields the current value of a given sequence (e.g. 'MOD_GEN') 
        without incrementing it
        """
        cur = self._connection.cursor()
        if sequenceId.startswith("${"):
            statement = "SELECT MDT_ID FROM MODULETABLES INNER JOIN MODULES ON MOD_ID = MDT_MOD_ID WHERE MOD_NAME = ? AND MDT_NAME = ? ;"
            args = tuple(sequenceId[2:-1].split("."))
            cur.execute(statement, args)
            res = cur.fetchone()
            seqnum = str(res[0])
            sequenceId = "SEQ_"+"0"*(6-len(seqnum))+seqnum
        statement = "SELECT GEN_ID ( %s , 0) FROM RDB$DATABASE ;"%str(sequenceId)
        cur.execute(statement)
        res = cur.fetchone()
        return res[0]

    def set_seq_to(self,sequenceId, value):
        """
        Yields the current value of a given sequence (e.g. 'MOD_GEN') 
        without incrementing it
        """
        cur = self._connection.cursor()
        statement = "SET GENERATOR %s TO %d ;"%(str(sequenceId), int(value))
        cur.execute(statement)
        self.commit()

    def remove_tables_for_module(self, module):
        """
        remove tables as part of module uninstallation
        """
        stmnt = "SELECT MDT_ID \
                        FROM MODULETABLES \
                        WHERE MDT_MOD_ID = ? ;"
        cur = self.query(stmnt,(module.get_id(),))
        rows = cur.fetchallmap()
        for row in rows:
            tab_id = "0"*(6-len(str(row["MDT_ID"])))+str(row["MDT_ID"])
            stmnt = "DROP TABLE TAB_%s ;"%tab_id
            self.query(stmnt,commit=True)
            stmnt = "DROP GENERATOR SEQ_%s ;"%tab_id
            self.query(stmnt,commit=True)
            stmnt = "DELETE FROM MODULETABLES WHERE MDT_ID = ? ;"
            self.query(stmnt,(row["MDT_ID"],),commit=True)

    def update_tables_for_module(self, module):
        """
        update tables as part of module update
        """
        tables = module.get_tables()
        stmnt = "SELECT MDT_NAME FROM MODULETABLES WHERE MDT_MOD_ID = ? ;"
        cur = self.query(stmnt,(module.get_id(),))
        rows = cur.fetchallmap()
        for row in rows:
            if row["MDT_NAME"] not in [tbl["name"] for tbl in tables]:
                self._remove_table_for_module(module,row["MDT_NAME"])
        for table in tables:
            if table["name"] not in [tbl["MDT_NAME"] for tbl in rows]:
                self._create_table_for_module(module,table)
            else:
                self._update_columns_for_table(module, table)

    def _update_columns_for_table(self, module, table):
        """
        Deletes columns that exist but are not defined in module's manifest
        Adds columns that doe not exist but are defined in modules's  manifest
        """
        stmnt = "SELECT RDB$FIELD_NAME FROM RDB$RELATION_FIELDS WHERE RDB$RELATION_NAME = ? ;"
        stmnt_drop = "ALTER TABLE %s DROP %s ;"
        stmnt_add = "ALTER TABLE %s ADD %s %s ;"

        db_tablename = self._replace_module_tables(module,"${"+table["name"]+"}")
        cur = self.query( stmnt, (db_tablename,))
        rows = cur.fetchallmap()
        for row in rows:
            field_name = row["RDB$FIELD_NAME"].strip()
            if field_name == "MOD_INSTANCE_ID":
                continue
            if field_name not in [col["name"] for col in table["columns"]]:
                self.query( stmnt_drop%(db_tablename, field_name),commit=True)
        for col in table["columns"]:
            if col["name"] not in [r["RDB$FIELD_NAME"].strip() for r in rows]:
                self.query( stmnt_add%(db_tablename, col["name"], col["type"]),commit=True)
        
    def create_tables_for_module(self, module):
        """
        create tables as part of module installation
        """
        tables = module.get_tables()

        for table in tables:
            self._create_table_for_module(module,table)
    
    def _remove_table_for_module(self, module, tablename):
        """
        remove tables as part of module uninstallation
        """
        stmnt = "SELECT MDT_ID \
                        FROM MODULETABLES \
                        WHERE MDT_MOD_ID = ? AND MDT_NAME = ? ;"
        cur = self.query(stmnt,(module.get_id(),tablename))
        rows = cur.fetchallmap()
        row = rows[0]
        tab_string = "0"*(6-len(str(row["MDT_ID"])))+str(row["MDT_ID"])
        stmnt = "DROP TABLE TAB_%s"%tab_string
        self.query(stmnt,commit=True)
        stmnt = "DROP GENERATOR SEQ_%s"%tab_string
        self.query(stmnt,commit=True)
        stmnt = "DELETE FROM MODULETABLES WHERE MDT_ID = ? ;"
        self.query(stmnt,(row["MDT_ID"],),commit=True)

    def _create_table_for_module(self, module, table):
        """
        creates a database table for a module
        """
        new_table_id = self.get_seq_next('MDT_GEN')
        new_table_string = "0"*(6-len(str(new_table_id)))+str(new_table_id)
        stmnt = "CREATE TABLE TAB_%s ( MOD_INSTANCE_ID INT "%new_table_string
        autoincrement = None
        for col in table["columns"]:
            stmnt += ", %s %s "%(col["name"],col["type"])
            if col.has_key("primary"):
                if type(col["primary"]) == bool and col["primary"]:
                    stmnt+="primary key "
                elif col.has_key("unique") and type(col["unique"])==bool and col["unique"]:
                    stmnt+="unique "
            else:
                if col.has_key("unique") and type(col["unique"])==bool and col["unique"]:
                    stmnt+="unique "
            if col.has_key("notnull") and type(col["notnull"])==bool and col["notnull"]:
                stmnt+="not null "
            if col.has_key("autoincrement") and type(col["autoincrement"])==bool and col["autoincrement"]:
                if autoincrement is None:
                    autoincrement = col["name"]
        stmnt+=") ;"
        

        mst_stmnt = "INSERT INTO MODULETABLES (MDT_ID, MDT_NAME, MDT_MOD_ID ) VALUES ( ?, ?, ?) ;"
        self.query( mst_stmnt, (new_table_id, table["name"], module.get_id()),commit=True)
        self.query( stmnt,commit=True)
        stmnt = "CREATE GENERATOR SEQ_%s ;"%new_table_string
        self.query( stmnt,commit=True)
        stmnt = "SET GENERATOR SEQ_%s TO 1 ;"%new_table_string
        self.query( stmnt,commit=True)

        #if autoincrement is not None:
        #    
        #    stmnt = """SET TERM ^ ;
        #            CREATE TRIGGER TRG_AUTO_%(nts)s FOR TAB_%(nts)s
        #            ACTIVE BEFORE INSERT POSITION 0
        #            AS
        #                DECLARE VARIABLE tmp DECIMAL(18,0);
        #            BEGIN
        #                IF (NEW.%(autoinc)s IS NULL) THEN
        #                    NEW.%(autoinc)s = GEN_ID(SEQ_%(nts)s, 1);
        #                ELSE BEGIN
        #                    tmp = GEN_ID(SEQ_%(nts)s, 0);
        #                    IF (tmp < new.%(autoinc)s) THEN
        #                        tmp = GEN_ID(SEQ_%(nts)s, new.%(autoinc)s - tmp);
        #                END
        #            END^
        #            SET TERM ; ^"""%{'autoinc':autoincrement,'nts':new_table_string}
        #    self.query(stmnt,commit=True)


class QueryCache(object):
    """
    caches prepared statements and delivers them on demand
    """
    RANK = 0
    PREP = 1
    CUR = 2
    MAX_QUERIES = 20
    def __init__(self):
        """
        trivial
        """
        self.queries = {}

    def __call__(self, cur, query):
        """
        looks if the given query is in the cache, if not, creates and returns
        it. if the number of cached query exceeds the MAX_QUERIES, it deletes
        the less used query
        """
        if query not in self.queries:
            if len(self.queries) >= self.MAX_QUERIES:
                lowest = self._get_lowest_use_query()
                del(self.queries[lowest])
            self.queries[query] = {self.RANK:0,self.PREP:cur.prep(query), self.CUR: cur}
        self.queries[query][self.RANK] += 1
        return (self.queries[query][self.PREP] , self.queries[query][self.CUR])


    def _get_lowest_use_query(self):
        """
        returns the query that has been used the fewest times.
        """
        lowest = None
        lquery = None
        for query, querydict in self.queries.items():
            if lowest is None or querydict[self.RANK] < lowest:
                lowest = querydict[self.RANK]
                lquery = query
        return lquery

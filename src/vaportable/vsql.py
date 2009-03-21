"""
vaportable/vsql.py

Defines mappings from VQL->SQL
"""

from vaportable import VaporTable

class SimpleVaporTable(VaporTable):
    """
    Magic for mapping VQL to SQL on an actual table,
    including exposing the fields allowed to be queried on,
    etc.
    """

    def __init__(self, internal_name, external_name, mappings):
        VaporTable.__init__(self, external_name)
        self.internal_name = internal_name.lower()
        self.external_name = external_name.lower()
        for key in mappings.keys():
            val = mappings[key]
            self.vqlsql_map[val] = key
            self.sqlvql_map[key] = val

    def _preflight_query(self, vql, parsed):
        """
        _preflight_query( 'SELECT * FROM FOO' )
        does "EXPLAIN" after using super version
        """
        # TODO: the explain test
        assert self.external_name == parsed.table_name, "External Name Mismatch... how'd you get routed here? %s %s" % (self.external_name, parsed.table_name)
        VaporTable._preflight_query(self, vql, parsed)
        return True

    def query( self, vql, parsed ):
        self._preflight_query( vql, parsed )
        sql = "SELECT %s FROM %s"
        cols = ", ".join([self.vqlsql_map[x] for x in parsed.columns])
        table = self.internal_name
        if parsed.wheres:
            sql += " WHERE %s"
            wheres = " AND ".join(["=".join((self.vqlsql_map[k],parsed.wheres[k])) for k in parsed.wheres.keys()])
            sql = sql % (cols,table,wheres)
        else:
            sql = sql % (cols,table)
        print "SQL generated : %s" % sql


class SimpleVaporView(VaporTable):
    """
    A VaporTable implementation that actually builds
    joins on some related tables in the DB.
    """
    def __init__(self, internal_tables, external_name, join_columns, mappings):
        VaporTable.__init__(self, external_name)
        self.internal_tables = [t.lower() for t in internal_tables]
        self.external_name = external_name.lower()
        self.join_columns = join_columns
        for k in mappings.keys():
            v = mappings[k]
            assert k.find('.') > -1, "SVV internal mappings must be qualified, %s %s" % (k,v)
            assert k.split('.')[0] in internal_tables, "SVV mapping doesn't match a table %s %s" % ( internal_tables, mappings )
            self.vqlsql_map[v] = k
            self.sqlvql_map[k] = v

    def _preflight_query(self, vql, parsed):
        assert self.external_name == parsed.table_name, "SVV ExName wrong %s %s" % (self.external_name, parsed.table_name)
        VaporTable._preflight_query( self, vql, parsed )
        #TODO: anything specific for a View?

    def query( self, vql, parsed ):
        #this is a little more complicated
        assert self.where_required, "SVV must be qualified, too dangerous"
        self._preflight_query( vql, parsed )
        sql = "SELECT %s FROM %s WHERE %s"
        tables = ", ".join( self.internal_tables )
        cols = ", ".join( [self.vqlsql_map[x] for x in parsed.columns] )
        wheres = " AND ".join(["=".join((self.vqlsql_map[k],parsed.wheres[k])) for k in parsed.wheres.keys()])
        sql = sql % ( cols, tables, wheres )
        print "View SQL = %s" % sql
        pass

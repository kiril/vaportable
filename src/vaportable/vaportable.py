"""
VaporTables

Defines a framework for an injection-safe SQL-like interface
into Python code.  Support for translating into SQL, into
Django models, or into any function call or intermediary one might want.
"""


###########  Here there be VaporTable ##############

class VaporTableRouter:
    """
    Nothing but a wrapper around a dictionary, really.
    Tiny bit of logic that knows how to look up 
    """
    def __init__(self):
        self.routes = {}

    def add_route(self,table):
        self.routes[ table.external_name ] = table

    def route(self, vql, parsed):
        if not self.routes.has_key( parsed.table_name ):
            return None
        return self.routes[ parsed.table_name ]

class VaporTable:
    """
    Base abstract class with utils for processing queries
    against a 'table' that may or may not actually exist.
    """

    def __init__(self,external_name):
        self.external_name = external_name
        self.vqlsql_map = {}#mapping of VQL columns to SQL columns
        self.sqlvql_map = {}#mapping of SQL columns to VQL result columns
        self.wild_allowed = False#whether 'SELECT *...' is allowed
        self.where_required = True#whether a WHERE clause must be present
        self.required_query_fields = {}#you've got to constrain stuff according to this map

    def __repr__(self):
        return "||%s||" % self.externalname

    def require_column( c ):
        self.where_required = True
        self.required_query_fields[c] = 1

    def _preflight_query(self, vql, parsed):
        """
        Tests against basic constraints.
        """
        if parsed.query_type == "SELECT":
            if self.where_required and not parsed.wheres:
                raise "Missing WHERE clause"

            if self.required_query_fields:
                for f in self.required_query_fields.keys():
                    if f not in parsed.wheres.keys():
                        raise "Missing required constrained field: '%s'" % f

            assert parsed.columns, "Must select some columns, yo"

            is_wild = len(parsed.columns) == 1 and parsed.columns[0] == "*"
            if is_wild:  assert self.wild_allowed, "No WildCarding allowed for this VaporTable"
            else:
                for c in parsed.columns:
                    assert self.vqlsql_map.has_key(c), "Invalid External Column"

    def query( vql, parsed ):
        pass

############ Here there be GCQL ##############

from vql import vql_grammar

def parse_vql( vql ):
    """
    Turns VQL into VQLQuery objects for use in
    VaporTable interface.
    There is validation in the query type implementations.
    """
    intermediary = vql_grammar.parseString( vql )

    exp_type = intermediary[0].upper()
    assert exp_type in ["SELECT","INSERT","UPDATE"]

    if exp_type == "SELECT":
        columns = intermediary[1]
        tables = intermediary[2]
        wheres = None
        if len( intermediary ) > 3:
            wheres = intermediary[3]
        return SelectVQLQuery( tables, columns, wheres )

    elif exp_type == "INSERT":
        table = intermediary[2]
        is_implicit = ( intermediary[3] == "VALUES" )
        if is_implicit:
            names = None
            values = intermediary[4]
        else:
            names = intermediary[3]
            values = intermediary[5]
        return InsertVQLQuery( table, names, values )

    else:#UPDATE
        table = intermediary[1]
        pairs = intermediary[2]
        return UpdateVQLQuery( table, pairs )

    return None

def _pairs_to_dict( pairs ):
    """
    Helper function for taking nested lists->dicts

    >>> _pairs_to_dict( None )
    {}
    >>> _pairs_to_dict( [['a','b'],['c','d']] )
    {'a': 'b', 'c': 'd'}
    """
    d = {}
    if not pairs: return d
    for pair in pairs: d[pair[0]] = pair[1]
    return d

class VQLQuery:
    def __init__(self,query_type):
        self.query_type = query_type
    pass

class SelectVQLQuery(VQLQuery):
    def __init__(self, tables, columns, wheres):
        VQLQuery.__init__(self, "SELECT")
        #maybe I shouldn't even allow multiple tables in the syntax...
        #it's actually a real feature to only allow 1.
        assert len(tables)==1, "Must have *exactly* 1 table"
        self.table_name = tables[0].lower()
        self.columns = [c.lower() for c in columns]
        self.wheres = _pairs_to_dict([(w[0].lower(),w[1]) for w in wheres])

    def __repr__(self):
        return "%s %s %s" % ( self.table_name , self.columns, self.wheres )

class InsertVQLQuery(VQLQuery):
    def __init__(self, table, names, values):
        VQLQuery.__init__(self, "INSERT")
    pass

class UpdateVQLQuery(VQLQuery):
    def __init__(self, table, pairs):
        VQLQuery.__init__(self, "UPDATE")
    pass

# Yays for testing
import doctest

doctest.testmod()

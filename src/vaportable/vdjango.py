"""
vaportable/django.py

Hook a VaporTable up to a Django model, turning
VQL into fetch / save calls on the Django object(s).
"""
from vaportable import VaporTable

class DjangoVaporTable(VaporTable):
    def __init__(self, model, external_name, mappings):
        VaporTable.__init__(self, external_name)
        self.model = model
        self.external_name = external_name.lower()
        for key in mappings.keys():
            val = mappings[key]
            self.vqlsql_map[val] = key
            self.sqlvql_map[key] = val

    def _preflight_query(self, vql, parsed):
        #todo
        VaporTable._preflight_query( self, vql, parsed )
        pass

    def query(self, vql, parsed):
        kvs = {}
        for k in parsed.wheres.keys():
            kvs[self.vqlsql_map[k]] = parsed.wheres[k]
        print "kvs = %s" % kvs
        res = apply( self.model.objects.filter, [], kvs )
        print res
        pass

class DjangoVaporView(VaporTable):
    #TODO: implement VQL->django model joins
    pass

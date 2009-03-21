from vaportable.vsql import SimpleVaporTable, SimpleVaporView
from vaportable.vdjango import DjangoVaporTable
from vaportable.vaportable import parse_vql

raw_query = "SELECT col1, col2 FROM table WHERE testcol1 = 'testval' AND testcol2 = 3333"
select_query = parse_vql( raw_query )
print "Select Query %s" % select_query


test_table = SimpleVaporTable( "internal_table", "table", {"itestcol1":"testcol1","itestcol2":"testcol2","icol1":"col1","icol2":"col2"} )
test_table.query( raw_query, select_query )

test_view = SimpleVaporView( ["a","b"], "foo", {"a.x":"b.x"}, {"a.ic":"ec","b.ic2":"ec2"} )
v_query = "select ec, ec2 from foo where ec = 4"
v_parsed = parse_vql( v_query )
test_view.query( v_query, v_parsed )




"""
# If you set up a Django model like this, you can try out this code

import one.models as mod

dvt = DjangoVaporTable( mod.Flog, "flip", {"a":"ao"} )
v_query = "select * from flip where ao = '123'"
v_parsed = parse_vql( v_query )
dvt.query( v_query, v_parsed )
"""


from pyparsing import *

def AListOf(x):
    return x + ZeroOrMore( Suppress( Word(",") ) + x)

#basic components
_AND = Suppress(CaselessLiteral("AND"))
_FROM = Suppress(CaselessLiteral("FROM"))
_WHERE = Suppress(CaselessLiteral("WHERE"))

name = Word( srange("[a-z]") + nums + "_" + "-" )
lquot = ( Literal("\"")|Literal( "'") )
string_value = Combine( lquot + Word(alphas+nums) + lquot )
numeric_value = Word( nums + "." + "-" )
value = ( string_value | numeric_value )
assignment = Group( name + Suppress( Literal("=") ) + value )

and_claus = Group( assignment + ZeroOrMore( _AND + assignment ) )

#larger VQL unites
vql_columns = ( Literal( "*" ) | Group( AListOf( name ) ) )
vql_from = ( _FROM + Group( AListOf( name ) ) )
vql_where = (  _WHERE + and_claus )
name_list = Suppress( Literal("(") ) + Group( AListOf( name ) ) + Suppress( Literal(")") )
value_list = Suppress( Literal("(") ) + Group( AListOf( value ) ) + Suppress( Literal(")") )

#complete statement structures
vql_select = CaselessLiteral( "SELECT" ) + vql_columns + vql_from + vql_where
vql_update = CaselessLiteral( "UPDATE" ) + name + CaselessLiteral( "SET" ) + AListOf( assignment ) + vql_where
vql_insert = CaselessLiteral( "INSERT" ) + CaselessLiteral( "INTO" ) + \
    Group( name + Optional( name_list ) ) + \
    CaselessLiteral( "VALUES" ) + Group( value_list )

vql_grammar = ( vql_select ) | ( vql_update ) | ( vql_insert )

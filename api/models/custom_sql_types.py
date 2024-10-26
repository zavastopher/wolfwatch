from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import Text

class LONGTEXT(Text):
    pass

@compiles(LONGTEXT, 'sqlite')
def compile_longtext_sqlite(element, compiler, **kw):
    return "TEXT"

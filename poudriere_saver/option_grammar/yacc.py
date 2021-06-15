import ply.yacc
from poudriere_saver.option_grammar.lex import tokens, get_lexer, err


# A document is just a dictionnary of value
def p_doc(p):
    """doc : definitions
    |"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = dict()


def p_definitions(p):
    """definitions : definitions definition
    | definition"""
    if len(p) == 3:
        name, op, value = p[2]
        # If this entry did not exists, create it
        if name in p[1]:
            op(p[1][name], value)
        else:
            p[1][name] = [value]
        p[0] = p[1]
    else:
        # Anyway, name can not be part of the definitions
        name, op, value = p[1]
        p[0] = dict(((name, [value]),))


def p_definition(p):
    """definition : name operator value"""
    p[0] = p[1:4]


def p_name(p):
    """name : WORD"""
    p[0] = p[1]


def p_value(p):
    """value : WORD"""
    p[0] = p[1]


def _set(entry, value):
    entry = [value]


def append(entry, value):
    entry.append(value)


OPERATOR = {"=": _set, "+=": append}


def p_operator(p):
    """operator : EQUAL
    | PLUS_EQUAL"""
    p[0] = OPERATOR[p[1]]


def p_error(p):
    if p is not None:
        err(f"Yacc error (line {p.lexer.lineno + 1}) : {p}")


def parse(fd):
    lexer = get_lexer(False)
    parser = ply.yacc.yacc()
    # Really, really, really not safe
    return parser.parse(fd.read(), lexer=lexer)

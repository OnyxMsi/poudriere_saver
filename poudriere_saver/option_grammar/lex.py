import ply.lex
import sys

tokens = ("WORD", "EQUAL", "PLUS_EQUAL")

t_WORD = r"[a-zA-Z0-9_]+"
t_EQUAL = r"="
t_PLUS_EQUAL = r"\+="

t_ignore = " \t"
t_ignore_COMMENT = r"\#.*"


def err(msg):
    sys.stderr.write(msg + "\n")


def t_ANY_NEWLINE(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


def t_error(t):
    err(f"Lexer error (line {t.lexer.lineno + 1}) : {t}")


def get_lexer(dbg):
    return ply.lex.lex(debug=dbg)

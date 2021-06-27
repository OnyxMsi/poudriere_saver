import logging


LOGGER = logging.getLogger("pty.parser")


def operator_set(lineno, res, key, value):
    LOGGER.debug("[Line %d] SET %s <- %s", lineno, key, value)
    res[key] = [value]


def operator_append(lineno, res, key, value):
    LOGGER.debug("[Line %d] APPEND %s <- %s", lineno, key, value)
    if key not in res:
        res[key] = [value]
    else:
        res[key].append(value)


def operator_remove(lineno, res, key, value):
    LOGGER.debug("[Line %d] REMOVE %s : %s", lineno, key, value)
    if key in res:
        res[key] = list(filter(lambda v: v != value), res[key])


SUPPORTED_OPERATORS = {"=": operator_set, "+=": operator_append, "-=": operator_remove}


def line_split(lineno, line):
    # Find operator start
    op_idx_st = -1
    op_idx_end = -1
    for i, c in enumerate(line):
        if not (c.isalnum() or c in ("_", "-")):
            op_idx_st = i
            break
    if op_idx_st == -1:
        LOGGER.error("[Line %d] Can't find operator in line : %s", lineno, line)
        raise ValueError(line)
    key = line[:op_idx_st]
    line2 = line[op_idx_st:].strip()
    for i, c in enumerate(line2):
        if c not in ("-", "+", "="):
            op_idx_end = i
            break
    if op_idx_end == -1:
        LOGGER.error("[Line %d] Can't find value in line : %s", lineno, line)
        raise ValueError(line)
    op_str = line2[:op_idx_end]
    # Value is what remains
    value = line2[op_idx_end:].strip()
    if op_str not in SUPPORTED_OPERATORS:
        LOGGER.error("[Line %d] Unknown operator %s", lineno, op_str)
        raise ValueError(line)
    op_fct = SUPPORTED_OPERATORS[op_str]
    return key, op_fct, value


def parse_line(lineno, line):
    line2 = line.strip()
    # Drop comment if any
    comment_idx = line2.find("#")
    if comment_idx == -1:
        line3 = line2
    else:
        line3 = line2[:comment_idx].strip()
    if len(line3) > 0:
        # Find first occurence which is not a alpha numeric or underscore
        return line_split(lineno, line3)
    else:
        return None, None, None


def parse(fd):
    res = dict()
    for lineno, line in enumerate(fd.readlines(), 1):
        LOGGER.debug("Parse line %d : %s", lineno, line)
        k, o, v = parse_line(lineno, line)
        if k is not None:
            o(lineno, res, k, v)
    return res

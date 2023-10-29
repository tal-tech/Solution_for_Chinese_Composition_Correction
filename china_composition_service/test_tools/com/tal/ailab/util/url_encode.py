from urllib.parse import unquote,quote


def encode(val):
    val = quote(val, 'utf-8')
    return val

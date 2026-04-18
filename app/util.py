# Converte valor em string para float
def to_float(str_val):
    if isinstance(str_val, str):
        try:
            return float(str_val.replace(',', '.'))
        except ValueError:
            return None
    return None


# Corrige string com charset corrompido
def fix_charset(text):
    if not isinstance(text, str):
        return text
    # Converte caracteres corrompidos de volta para bytes e decodifica
    return "".join(
        chr(ord(c) & 0xFF) if 0xDC00 <= ord(c) <= 0xDCFF else c
        for c in text
    )

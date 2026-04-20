from datetime import datetime, timedelta, timezone


# Define o fuso horário de Brasília (UTC-3)
_FUSO_BRASILIA = timezone(timedelta(hours=-3))


def get_str_time():
    return datetime.now(_FUSO_BRASILIA).strftime(r'%d/%m/%Y %H:%M:%S')

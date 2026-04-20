import sys
from os import path
from app.date_time_util import get_str_time


class Logger:
    @staticmethod
    def start(msg):
        print(f'{get_str_time()} [INÍCIO]  {msg}', flush=True)

    @staticmethod
    def info(msg, full_path=None, step=None):
        prefix = f'Etapa {step}: ' if step else ''
        file_name = path.basename(full_path) if full_path is not None else ''
        step_marker = '•' if step is not None else ' ' 
        print(f'{get_str_time()}   INFO: {step_marker} {prefix}{msg} {file_name}', flush=True, file=sys.stdout)

    @staticmethod
    def success(msg, full_path=None, step=None):
        prefix = f'Etapa {step}: ' if step else ''
        file_name = path.basename(full_path) if full_path is not None else ''
        # print(f'[SUCESSO] {prefix}{msg} {file_name}', flush=True, file=sys.stdout)
        print(f'{get_str_time()} [SUCESSO] {prefix}{msg} {file_name}', flush=True, file=sys.stdout)

    # Log de Erro exibe o caminho completo do arquivo
    @staticmethod
    def error(msg, full_path=None, step=None):
        prefix = f'Etapa {step}: ' if step else ''
        file_name_full = f': {full_path}' if full_path else ''
        # print(f'[ERRO] {prefix}{msg} {file_name_full}', flush=True, file=sys.stderr)
        print(f'{get_str_time()}   ERRO: x {prefix}{msg} {file_name_full}', flush=True, file=sys.stderr)

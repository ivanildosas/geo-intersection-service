import sys
from os import path
from app.date_time_util import get_str_time


class Logger:
    def __init__(self, log_queue=None):
        self.log_queue = log_queue

    def queue_append(self, message):
        if self.log_queue is not None:
            self.log_queue.append(message)

    def start(self, msg):
        message = f'{get_str_time()} [INÍCIO]  {msg}'
        print(message, flush=True)
        self.queue_append(message)

    def info(self, msg, full_path=None, step=None):
        prefix = f'Etapa {step}: ' if step else ''
        file_name = path.basename(full_path) if full_path is not None else ''
        step_marker = '•' if step is not None else ' '

        message = f'{get_str_time()}   INFO: {step_marker} {prefix}{msg} {file_name}'
        print(message, flush=True, file=sys.stdout)
        self.queue_append(message)

    def success(self, msg, full_path=None, step=None):
        prefix = f'Etapa {step}: ' if step else ''
        file_name = path.basename(full_path) if full_path is not None else ''

        message = f'{get_str_time()} [SUCESSO] {prefix}{msg} {file_name}'
        print(message, flush=True, file=sys.stdout)
        self.queue_append(message)

    # Log de Erro exibe o caminho completo do arquivo
    def error(self, msg, full_path=None, step=None):
        prefix = f'Etapa {step}: ' if step else ''
        file_name_full = f': {full_path}' if full_path else ''

        message = f'{get_str_time()}   ERRO: x {prefix}{msg} {file_name_full}'
        print(message, flush=True, file=sys.stderr)
        self.queue_append(message)

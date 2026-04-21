import csv
from pathlib import Path

class CsvService:

    # Salva lista de dicionários em arquivo CSV
    @staticmethod
    def save_attributes_to_csv(property_list, output_path):

        out_path = Path(output_path)
        out_path.unlink(missing_ok=True)

        if not property_list:
            return False

        headers = list(property_list[0].keys())
        try:
            with open(output_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers, delimiter=';')
                writer.writeheader()
                writer.writerows(property_list)
            return True
        except PermissionError:
            print(f"Erro: O arquivo {output_path} está aberto. Feche-o e tente novamente.")
            return None
        except Exception as e:
            print(f"Erro ao salvar arquivo CSV: {e}")
            return None

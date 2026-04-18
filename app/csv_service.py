import csv


class CsvService:

    # Salva lista de dicionários em arquivo CSV
    @staticmethod
    def save_attributes_to_csv(property_list, output_path):
        if not property_list:
            print(f'Lista de propriedades vazia, arquivo CSV {output_path} não foi criado.')
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
            return False
        except Exception as e:
            print(f"Erro ao salvar aqrquivo CSV: {e}")
            return False

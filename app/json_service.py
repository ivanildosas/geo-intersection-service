import json


class JsonService:

    @staticmethod
    def get_json_data(file_path):
        json_data = None
        with open(file_path, "r") as json_file:
            json_data = json.load(json_file)
        return json_data

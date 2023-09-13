from typing import Union, Dict
from logger import Logger

import json, os

class JSONer:
    def __init__(self):
        """
        Initialize a JSONer instance.
        """
        self._logger = Logger(__name__).get_logger()

    def read_json(self, json_path: str) -> Union[Dict, None]:
        """
        Read a JSON file and return its contents as a dictionary.

        Args:
            json_path (str): The path to the JSON file.

        Returns:
            Union[Dict, None]: The JSON content as a dictionary, or None if there was an error.
        """
        if os.path.isfile(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as file:
                    return json.load(file)
            except FileNotFoundError:
                self._logger.error(f"JSON file not found: '{json_path}'")
            except json.JSONDecodeError as e:
                self._logger.error(f"Error decoding JSON in '{json_path}': {e}")
        else:
            self._logger.error(f"JSON file not found: '{json_path}'")

        return None

    def write_json(self, json_path: str, json_content: Union[Dict, str]):
        """
        Write JSON content to a file.

        Args:
            json_path (str): The path to the JSON file.
            json_content (Union[Dict, str]): The JSON content to be written. Can be a dictionary or a string.
        """
        try:
            with open(json_path, "w", encoding="utf-8") as json_file:
                if isinstance(json_content, dict):
                    json.dump(json_content, json_file, ensure_ascii=False, indent=4)
                elif isinstance(json_content, str):
                    json_file.write(json_content)
                else:
                    raise ValueError("Unsupported JSON content type. Use Dict or str.")
        except FileNotFoundError:
            self._logger.error(f"JSON file not found: '{json_path}'")
        except Exception as e:
            self._logger.error(f"Error writing JSON to '{json_path}': {e}")

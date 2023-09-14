from logger import Logger
from typing import Union, Dict

import json

class JSONHandler:
    def __init__(self):
        """
        Initialize a JSONHandler instance.

        Creates an instance of the Logger class for logging messages related to JSON handling.
        """
        self._logger = Logger(__name__).get_logger()

    def load_json(self, json_path: str) -> Union[Dict[str, Union[str, int, float, bool, None]], None]:
        """
        Load JSON data from a file.

        Args:
            json_path (str): The path to the JSON file.

        Returns:
            Union[Dict[str, Union[str, int, float, bool, None]], None]: The loaded JSON data as a dictionary,
            or None if an error occurred during loading.
        """
        try:
            with open(json_path, "r", encoding="utf-8") as json_file:
                return json.load(json_file)
        except FileNotFoundError as e:
            self._logger.error(f"File not found: '{json_path}' - {e}")
        except json.JSONDecodeError as e:
            self._logger.error(f"Error decoding JSON in '{json_path}': {e}")
        except Exception as e:
            self._logger.error(f"Error reading JSON from '{json_path}': {e}")
        return None

    def save_json(self, json_path: str, json_content: Union[Dict[str, Union[str, int, float, bool, None]], str]):
        """
        Save JSON data to a file.

        Args:
            json_path (str): The path to the JSON file to be created or overwritten.
            json_content (Union[Dict[str, Union[str, int, float, bool, None]], str]): The JSON data to be saved,
            which can be a dictionary or a JSON-formatted string.

        Raises:
            ValueError: If the JSON content type is unsupported (neither dictionary nor string).
        """
        try:
            with open(json_path, "w", encoding="utf-8") as json_file:
                if isinstance(json_content, str):
                    json_file.write(json_content)
                elif isinstance(json_content, dict):
                    json.dump(json_content, json_file, ensure_ascii=False, indent=4)
                else:
                    raise ValueError("Unsupported JSON content type. Use Dict or str.")
        except FileNotFoundError as e:
            self._logger.error(f"File not found: '{json_path}' - {e}")
        except Exception as e:
            self._logger.error(f"Error writing JSON to '{json_path}': {e}")

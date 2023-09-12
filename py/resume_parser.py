from file_reader import FileReader
from logger import Logger
from pathlib import Path
from typing import Dict

import json, openai, os

class ResumeParser:
    def __init__(self):
        """
        Initialize a ResumeParser instance.

        This class is designed to parse resume documents using OpenAI's GPT-3 language model.

        Attributes:
            _json_dir_path (str): The directory path where JSON files are stored.
            _logger (logging.Logger): The logger instance for logging messages.
        """
        self._json_dir_path = "../json/"
        self._logger = Logger(__name__).get_logger()

        self._set_openai_api_key()
        
    def _read_json(self, json_path: str) -> Dict:
        """
        Read a JSON file and return its contents as a dictionary.

        Args:
            json_path (str): The path to the JSON file.

        Returns:
            Dict: The JSON content as a dictionary.
        """
        with open(json_path, "r", encoding="utf-8") as file:
            return json.load(file)
        
    def _write_json(self, json_path: str, json_content: str):
        """
        Write JSON content to a file.

        Args:
            json_path (str): The path to the JSON file.
            json_content (str): The JSON content to be written.
        """
        with open(json_path, "w") as json_file:
            json_file.write(json_content)

    def _set_openai_api_key(self):
        """
        Set the OpenAI API key from a JSON file.

        If the API key file is not found, an error message is logged.
        """
        api_key_path = os.path.join(self._json_dir_path, "configuration/api_key.json")
        try:
            openai.api_key = self._read_json(api_key_path).get("api_key")
        except FileNotFoundError:
            self._logger.error(f"API key file not found at {api_key_path}. Please provide a valid API key.")
            
    def _parse_resume_with_openai(self, owner: str, resume_content: str, parsing_format: str) -> Dict:
        """
        Parse a resume using OpenAI's GPT-3 language model.

        Args:
            owner (str): The owner's name of the resume.
            resume_content (str): The content of the resume.
            parsing_format (str): The parsing format provided in JSON.

        Returns:
            Dict: The parsed resume content as a dictionary.
        """
        return openai.ChatCompletion.create(
            temperature=1,
            model="gpt-3.5-turbo-16k",
            messages=[
                {
                    "role": "user",
                    "content": f"Parse {owner}'s resume by using the JSON format below.\n\n{resume_content}\n\n{parsing_format}"
                }
            ]
        )

    def parse_resumes(self):
        """
        Parse resumes using OpenAI's GPT-3 language model and store the parsed results as JSON files.
        """
        parsing_format = json.dumps(self._read_json(os.path.join(self._json_dir_path, "configuration/parsing_format.json")), indent=4)
        file_paths_and_file_contents = FileReader(["../docx", "../pdf"]).read_file_contents()

        if file_paths_and_file_contents is not None:
            for file_path, file_content in file_paths_and_file_contents.items():
                self._logger.info(f"Parsing {file_path}")
                
                response = self._parse_resume_with_openai(Path(file_path).stem, file_content, parsing_format)
                self._write_json(os.path.join(self._json_dir_path, "parsed_resume", Path(file_path).stem + ".json"), response["choices"][0]["message"]["content"])
                
                self._logger.info(f"Parsed  {file_path}, Finish Reason: {response['choices'][0]['finish_reason']}")

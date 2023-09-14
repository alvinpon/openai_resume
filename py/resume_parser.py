from file_reader import FileReader
from json_handler import JSONHandler
from logger import Logger
from mongo_db import MongoDB
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
        self._json_handler = JSONHandler()
        self._logger = Logger(__name__).get_logger()

        self._set_openai_api_key()

    def _set_openai_api_key(self):
        """
        Set the OpenAI API key from a JSON file.

        If the API key file is not found, raise a FileNotFoundError and log an error message.

        Raises:
            FileNotFoundError: If the API key file is not found.
        """
        api_key_path = os.path.join(self._json_dir_path, "configuration/api_key.json")
        try:
            openai.api_key = self._json_handler.load_json(api_key_path).get("api_key")
        except FileNotFoundError as e:
            error_message = f"Failed to set API key: API key file not found at {api_key_path}. Please provide a valid API key. {e}"
            self._logger.error(error_message)
            raise FileNotFoundError(error_message)        
            
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
        Parse resumes using OpenAI's GPT-3 language model, store the parsed results as JSON files,
        and insert the parsed data into MongoDB.
        """
        parsed_contents = []

        # Load the parsing format from a JSON file
        parsing_format = json.dumps(self._json_handler.load_json(os.path.join(self._json_dir_path, "configuration/parsing_format.json")), indent=4)

        # Read resume files and their contents
        file_paths_and_file_contents = FileReader(["../docx", "../pdf"]).read_file_contents()

        if file_paths_and_file_contents is not None:
            for file_path, file_content in file_paths_and_file_contents.items():
                self._logger.info(f"Parsing {file_path}")

                # Parse the resume content using OpenAI
                response = self._parse_resume_with_openai(Path(file_path).stem, file_content, parsing_format)
                parsed_contents.append(json.loads(response["choices"][0]["message"]["content"]))

                # Write the parsed content to a JSON file
                self._json_handler.save_json(os.path.join(self._json_dir_path, "parsed_resume", Path(file_path).stem + ".json"), response["choices"][0]["message"]["content"])
                self._logger.info(f"Parsed  {file_path}, Finish Reason: {response['choices'][0]['finish_reason']}")

        # Retrieve the DB configuration information
        db_config = self._json_handler.load_json("../json/configuration/mongo_db.json")

        # Create a MongoDB instance and establish a connection
        with MongoDB(db_config.get("uri"), db_config.get("database_name"), db_config.get("collection_name")) as mongo_db:
            # Insert the parsed resume data into MongoDB
            mongo_db.insert_documents(parsed_contents)

from logger import Logger
from PyPDF2 import PdfReader
from typing import Callable, Union, Dict, List

import docx, io, os

class FileReader:
    def __init__(self, dir_paths: List[str]):
        """
        Initialize a FileReader instance.

        Args:
            dir_paths (List[str]): A list of directory paths to search for files.
        """
        self._dir_paths = dir_paths
        self._valid_extensions = {".docx", ".pdf"}

        # Initialize the logger
        self._logger = Logger(__name__).get_logger()

    def _retrieve_file_paths(self) -> List[str]:
        """
        Retrieve a list of file paths within the specified directories, filtered by valid extensions.

        Returns:
            List[str]: A list of valid file paths.
        """
        file_paths = []
        
        if self._dir_paths is not None:
            for dir_path in self._dir_paths:
                if os.path.isdir(dir_path):
                    for file_name in os.listdir(dir_path):
                        if os.path.splitext(file_name)[1].lower() in self._valid_extensions:
                            file_paths.append(os.path.join(dir_path, file_name))

        return file_paths

    def _read_file(self, file_path: str, reader_func: Callable) -> str: 
        """
        Read a file using the specified reader function.

        Args:
            file_path (str): The path to the file to be read.
            reader_func (Callable): A callable function for reading the file content.

        Returns:
            str: The content of the file as a string.
        """
        try:
            with open(file_path, "rb") as file:
                return reader_func(file)
        except FileNotFoundError as e:
            self._logger.error(f"File not found: {e}")
            return f"File not found: {e}"
        except PermissionError as e:
            self._logger.error(f"Permission error: {e}")
            return f"Permission error: {e}"
        except Exception as e:
            self._logger.error(f"An error occurred: {e}")
            return f"An error occurred: {e}"

    def _read_docx(self, file_path: str) -> str:
        """
        Read the content of a DOCX file.

        Args:
            file_path (str): The path to the DOCX file.

        Returns:
            str: The content of the DOCX file as a string.
        """
        def read_docx_file(file: io.BytesIO) -> str:
            text = []
            for paragraph in docx.Document(file).paragraphs:
                text.append(paragraph.text)
            return '\n'.join(text)

        return self._read_file(file_path, read_docx_file)

    def _read_pdf(self, file_path: str) -> str:
        """
        Read the content of a PDF file.

        Args:
            file_path (str): The path to the PDF file.

        Returns:
            str: The content of the PDF file as a string.
        """
        def read_pdf_file(file: io.BytesIO) -> str:
            text = ""
            pdf_reader = PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text

        return self._read_file(file_path, read_pdf_file)

    def read_file_contents(self) -> Dict[str, str]:
        """
        Read the contents of files within specified directories and return them as a dictionary.

        Returns:
            Dict[str, str]: A dictionary where keys are file paths and values are the
            contents of the respective files.
        """
        # Define a dictionary to map file extensions to reader functions
        file_extensions_and_reader_functions = {
            ".docx": self._read_docx,
            ".pdf": self._read_pdf,
        }
        
        file_paths_and_file_contents = {}

        for file_path in self._retrieve_file_paths():
            self._logger.info(f"Reading {file_path}")
            file_paths_and_file_contents[file_path] = file_extensions_and_reader_functions[os.path.splitext(file_path)[1].lower()](file_path)
            self._logger.info(f"Read    {file_path}")

        return file_paths_and_file_contents

from logger import Logger
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from pymongo.server_api import ServerApi
from typing import Union, Any, Dict, List

class MongoDB:
    def __init__(self, uri: str, database_name: str, collection_name: str):
        """
        Initialize a MongoDB connection object.

        Args:
            uri (str): The MongoDB connection URI.
            database_name (str): The name of the MongoDB database.
            collection_name (str): The name of the MongoDB collection.
        """
        self._uri = uri
        self._database_name = database_name
        self._collection_name = collection_name
        self._logger = Logger(__name__).get_logger()

    def __enter__(self):
        """
        Enter the MongoDB context.

        This method is called when entering a context using the 'with' statement.
        It establishes a connection to MongoDB and initializes database and collection objects.

        Returns:
            MongoDB: The MongoDB connection object.
        """
        try:
            self._logger.info("Connecting to MongoDB.")
            self._client = MongoClient(self._uri, server_api=ServerApi('1'), serverSelectionTimeoutMS=5000)
            self._database = self._client[self._database_name]
            self._collection = self._database[self._collection_name]
            self._logger.info("Connected to MongoDB.")
            return self
        except ConnectionFailure as e:
            error_message = f"Failed to connect to MongoDB: {e}"
            self._logger.error(error_message)
            raise ConnectionFailure(error_message)

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the MongoDB context.

        This method is called when exiting the context created with the 'with' statement.
        It closes the MongoDB client connection.

        Args:
            exc_type: The type of exception that occurred (if any).
            exc_value: The exception object (if any).
            traceback: The traceback object (if any).
        """
        if self._client is not None:
            self._logger.info("Disconnecting from MongoDB.")
            self._client.close()
            self._logger.info("Disconnected from MongoDB.")

    def insert_data(self, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Union[str, List[str]]:
        """
        Insert one or multiple documents into the MongoDB collection.

        Args:
            data (Union[Dict, List[Dict]]): The data to be inserted. It can be a single dictionary or a list of dictionaries.

        Returns:
            Union[str, List[str]]: The inserted document ID (string) or a list of inserted document IDs (list of strings).
        """ 
        try:
            if isinstance(data, dict):
                self._logger.info("Inserting data.")
                result = self._collection.insert_one(data)
                self._logger.info("Inserted  data.")
                return str(result.inserted_id)
            elif isinstance(data, list):
                self._logger.info("Inserting a list of data.")
                result = self._collection.insert_many(data)
                self._logger.info("Inserted  a list of data.")
                return [str(document_id) for document_id in result.inserted_ids]
            else:
                raise ValueError("Invalid data type. It should be a dictionary or a list of dictionaries.")
        except Exception as e:
            error_message = f"Failed to insert data into MongoDB: {e}"
            self._logger.error(error_message)
            raise Exception(error_message)

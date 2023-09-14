from logger import Logger
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, WriteError
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
            self._logger.info("Connected  to MongoDB.")
            return self
        except ConnectionFailure as connection_failure:
            error_message = f"Failed to connect to MongoDB: {connection_failure}"
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
            self._logger.info("Disconnected  from MongoDB.")

    def insert_document(self, document: Dict[str, Any]) -> str:
        """
        Insert a single document into the MongoDB collection.

        Args:
            document (Dict[str, Any]): The document to be inserted as a dictionary.

        Returns:
            str: The inserted document ID (string).
        """
        try:
            self._logger.info("Inserting a document.")
            result = self._collection.insert_one(document)
            self._logger.info("Inserted  a document.")
            return str(result.inserted_id)
        except Exception as exception:
            error_message = f"Failed to insert a document into MongoDB: {exception}"
            self._logger.error(error_message)
            raise Exception(error_message)

    def insert_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """
        Insert multiple documents into the MongoDB collection.

        Args:
            documents (List[Dict[str, Any]]): The list of documents to be inserted as dictionaries.

        Returns:
            List[str]: A list of inserted document IDs (list of strings).
        """
        try:
            self._logger.info(f"Inserting documents.")
            result = self._collection.insert_many(documents)
            self._logger.info(f"Inserted {result.inserted_ids.__len__()} documents.")
            return [str(document_id) for document_id in result.inserted_ids]
        except Exception as exception:
            error_message = f"Failed to insert documents into MongoDB: {exception}"
            self._logger.error(error_message)
            raise Exception(error_message)

    def delete_document(self, query: Dict) -> Union[int, None]:
        """
        Delete a single document from the MongoDB collection based on the given query.

        Args:
            query (Dict): The query criteria for deleting the document.

        Returns:
            Union[int, None]: The number of deleted documents (int) or None if an error occurs.
        """
        try:
            self._logger.info("Deleting a document.")
            result = self._collection.delete_one(query)
            deleted_count = result.deleted_count
            
            if deleted_count == 1:
                self._logger.info(f"Deleted {deleted_count} document.")
            else:
                self._logger.warning("No document found to delete.")
            return deleted_count
        except WriteError as write_error:
            self._logger.error(f"Failed to delete data from MongoDB: {write_error}")
            return None  # Return None to indicate an error
        except Exception as exception:
            self._logger.error(f"An unexpected error occurred: {exception}")
            return None  # Return None to indicate an error

    def delete_documents(self, query: Dict) -> Union[int, None]:
        """
        Delete multiple documents from the MongoDB collection based on the given query.

        Args:
            query (Dict): The query criteria for deleting the documents.

        Returns:
            Union[int, None]: The number of deleted documents (int) or None if an error occurs.
        """
        try:
            self._logger.info("Deleting documents.")
            result = self._collection.delete_many(query)
            deleted_count = result.deleted_count
            
            if deleted_count >= 1:
                self._logger.info(f"Deleted {deleted_count} documents.")
            else:
                self._logger.warning("No documents found to delete.")
            return deleted_count
        except WriteError as write_error:
            self._logger.error(f"Failed to delete data from MongoDB: {write_error}")
            return None  # Return None to indicate an error
        except Exception as exception:
            self._logger.error(f"An unexpected error occurred: {exception}")
            return None  # Return None to indicate an error
        
    def find_document(self, query: Dict[str, Any]) -> Union[Dict[str, Any], None]:
        """
        Find a single document in the MongoDB collection based on the given query.

        Args:
            query (Dict[str, Any]): The query criteria.

        Returns:
            Union[Dict[str, Any], None]: The found document or None if not found or an error occurs.
        """
        try:
            self._logger.info("Finding document.")
            result = self._collection.find_one(query)
            if result:
                self._logger.info("Found document.")
            else:
                self._logger.warning("Document not found.")
            return result
        except Exception as exception:
            self._logger.error(f"An error occurred while finding the document: {exception}")
            return None

    def find_documents(self, query: Dict[str, Any]) -> Union[List[Dict[str, Any]], None]:
        """
        Find multiple documents in the MongoDB collection based on the given query.

        Args:
            query (Dict[str, Any]): The query criteria.

        Returns:
            Union[List[Dict[str, Any]], None]: A list of found documents or None if an error occurs.
        """
        try:
            self._logger.info(f"Finding documents.")
            result = list(self._collection.find(query))
            self._logger.info(f"Found {len(result)} documents.")
            return result
        except Exception as exception:
            self._logger.error(f"An error occurred while finding documents: {exception}")
            return None
 
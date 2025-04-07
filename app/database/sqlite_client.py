import os
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

class SQLiteClient:
    def __init__(self, db_path, username=None, password=None):
        """
        Initialize a SQLite database client
        
        Args:
            db_path (str): Path to the SQLite database file
            username (str, optional): Username for authentication (not typically used for SQLite)
            password (str, optional): Password for authentication (not typically used for SQLite)
        """
        self.db_path = db_path
        self.username = username
        self.password = password
        self.engine = None
        
        self._connect()
    
    def _connect(self):
        """Create database connection"""
        try:
            # SQLite connection string
            connection_string = f"sqlite:///{self.db_path}"
            self.engine = create_engine(connection_string)
        except SQLAlchemyError as e:
            raise ConnectionError(f"Failed to connect to SQLite database: {str(e)}")
    
    def execute_query(self, query, params=None):
        """
        Execute a SQL query and return results as a pandas DataFrame
        
        Args:
            query (str): SQL query to execute
            params (dict, optional): Parameters to bind to the query
            
        Returns:
            pd.DataFrame: Query results as a pandas DataFrame
        """
        if not self.engine:
            raise ConnectionError("Database connection not established")
            
        try:
            with self.engine.connect() as connection:
                if params:
                    result = connection.execute(text(query), params)
                else:
                    result = connection.execute(text(query))
                
                # Convert result to DataFrame
                df = pd.DataFrame(result.fetchall())
                
                # Set column names if results were returned
                if not df.empty:
                    df.columns = result.keys()
                    
                return df
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error executing query: {str(e)}")
    
    def close(self):
        """Close the database connection"""
        if self.engine:
            self.engine.dispose()
            self.engine = None
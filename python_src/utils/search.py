import os
from typing import List

from .database import DocDatabaseWhoosh
from .relevant_doc import RelevantDoc

database = DocDatabaseWhoosh()

def search_database(question_string: str) -> List[RelevantDoc]:
    """Find relevant docs w.r.t the user question
    The result list may be empty
    
    This function is independent on the implementation of the database
    """
    return database.search(question_string)

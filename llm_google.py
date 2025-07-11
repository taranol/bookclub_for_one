import streamlit as st
import base64
import os
from google import genai
from google.genai import types
from pydantic import BaseModel
import json
from typing import List

PROMPT_BOOKS = st.secrets["prompts"]["prompt_books"]
PROMPT_READER_INFO = st.secrets["prompts"]["prompt_reader_info"]
PROMPT_RECOMMENDATION = st.secrets["prompts"]["prompt_recommendation"]
SOCIONIC_TYPES = st.secrets["prompts"]["socionics_types"]


GOOGLE_API_KEY = st.secrets["api_keys"]["google_api_key"]

class Profile(BaseModel):
    type: str
    Base: str
    Creative: str
    PoLR: str
    Suggestive: str
    Mobilizing: str
    description: str
    
class Book(BaseModel):
    title: str
    author: str
    description: str

class Function(BaseModel):
    name: str
    score: float
    #count: int
    # isbn: str

class Analysis(BaseModel):
    
    type: Profile
    age: str
    genre: list[str]
    topics: list[str]
    vibe: str
    library_type: list[str]
    gender: str
    functions: list[Function]
    description: str

    
class BookList(BaseModel):
    description: str
    books: list[Book]
    functions: list[str]


   

class Recommendations(BaseModel):
    identity: BookList
    identity_2: BookList
    dual: BookList
    activation: BookList
    opposite:  BookList
    
    
# class Response(BaseModel):
#     reader: Reader
#     recommendations: Recommendations
    # Configure the API
# genai.configure(api_key=GOOGLE_API_KEY)



# Model selection
MODEL_ID = "learnlm-2.0-flash-experimental"
client = genai.Client(api_key=GOOGLE_API_KEY)

def extract_books_and_authors(file, prompt=PROMPT_BOOKS):
    try:
        
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=[file, prompt]
        )
        return response.text
    except Exception as e:
        st.error(f"Error with Google API: {str(e)}")
        st.error("Please check your Google API key")
        return None
    
def get_reader_info_genai(book_list, prompt=PROMPT_READER_INFO,  socionic_types=SOCIONIC_TYPES):
    try:
        
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=[prompt, book_list, socionic_types],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=Analysis,
                temperature=0.3
            )
            
        )
        return response.text
    
    except Exception as e:
        st.error(f"Error with Google API: {str(e)}")
        st.error("Please check your Google API key")
        return None

def get_recommendations_genai( book_list, reader_info, prompt=PROMPT_RECOMMENDATION, socionic_types=SOCIONIC_TYPES ):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=[prompt, book_list, reader_info, socionic_types], 
            
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=Recommendations,
                temperature=0.9
            )
        )
        return json.loads(response.text)
    except Exception as e:  
        st.error(f"Error with Google API: {str(e)}")
        st.error("Please check your Google API key")
        return None 
    
__all__ = ["extract_books_and_authors", "get_reader_info_genai", "get_recommendations_genai"]



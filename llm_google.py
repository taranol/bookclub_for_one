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


GOOGLE_API_KEY = st.secrets["api_keys"]["google_api_key"]

class Analysis(BaseModel):
    description: list[str]
    jungian: str
    age: str
    genre: str
    subgenre: list[str]
    topics: list[str]
    vibe: list[str]
    


class Book(BaseModel):
    title: str
    author: str
    description: str
    # isbn: str
   

class Recommendations(BaseModel):
    identity: list[Book]
    dual: list[Book]
    mirror: list[Book]
    opposite: list[Book]
    identity_2: list[Book]
    
# class Response(BaseModel):
#     reader: Reader
#     recommendations: Recommendations
    # Configure the API
# genai.configure(api_key=GOOGLE_API_KEY)



# Model selection
MODEL_ID = "learnlm-2.0-flash-experimental"
client = genai.Client(api_key=GOOGLE_API_KEY)

def extract_books_and_authors(file, prompt):
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
    
def get_reader_info_genai(prompt):
    try:
        
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=Analysis,
                temperature=0.4
            )
            
        )
        return json.loads(response.text)
    except Exception as e:
        st.error(f"Error with Google API: {str(e)}")
        st.error("Please check your Google API key")
        return None

def get_recommendations_genai(prompt):
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=[prompt], 
            
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



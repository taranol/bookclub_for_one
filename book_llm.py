import streamlit as st
import base64
import os
import google.generativeai as genai
from google.generativeai import types
from io import BytesIO
import anthropic
import json
import random
import toml
from dotenv import load_dotenv
# from prompts import prompt_books, prompt_reader_info, prompt_recommendation, prompt_book_description

# Load environment variables from .env file
load_dotenv()

# Try to get API keys from Streamlit secrets first, then fall back to .env
try:
    GOOGLE_API_KEY = st.secrets["api_keys"]["google_api_key"]
    ANTHROPIC_API_KEY = st.secrets["api_keys"]["anthropic_api_key"]
    
except Exception as e:
    st.warning("Could not load secrets from .streamlit/secrets.toml, falling back to .env file")
    # Fall back to environment variables
    # GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    # ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    
    # # Fall back to default prompts if not in secrets
    # PROMPT_BOOKS = prompt_books
    
    # PROMPT_READER_INFO = prompt_reader_info
    
    # PROMPT_RECOMMENDATION =prompt_recommendation
    # PROMPT_BOOK_DESCRIPTION = prompt_book_description

PROMPT_BOOKS = st.secrets["prompts"]["prompt_books"]
PROMPT_READER_INFO = st.secrets["prompts"]["prompt_reader_info"]
PROMPT_RECOMMENDATION = st.secrets["prompts"]["prompt_recommendation"]
PROMPT_BOOK_DESCRIPTION = st.secrets["prompts"]["prompt_book_description"]#

#  Verify API keys are available
if not GOOGLE_API_KEY or not ANTHROPIC_API_KEY:
    st.error("""
    API keys not found. Please either:
    1. Add your API keys to .streamlit/secrets.toml, or
    2. Set them in your .env file as:
       GOOGLE_API_KEY=your-key-here
       ANTHROPIC_API_KEY=your-key-here
    """)
    st.stop()

def extract_books_and_authors(file, prompt=PROMPT_BOOKS):
    try:
        client = genai.Client(api_key=GOOGLE_API_KEY)
        response = client.models.generate_content(
            model="learnlm-2.0-flash-experimental",
            contents=[prompt, file]
        )
        return response.text
    except Exception as e:
        st.error(f"Error with Google API: {str(e)}")
        st.error("Please check your Google API key")
        return None

def infer_sociotype(books, prompt_reader_info=PROMPT_READER_INFO):
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        message = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1000,
            temperature=0.5,
            system=prompt_reader_info,
            messages=[
                {"role": "user", "content": f"Based on these books:\n{books}"}
            ]
        )
        # Parse the response into a dictionary
        try:
            response_text = message.content[0].text
            # Find the dictionary part of the response
        except Exception as e:
            print(f"Error parsing response: {e}")
        
        return response_text
    except Exception as e:
        st.error(f"Error with Anthropic API: {str(e)}")
        st.error("Please check your Anthropic API key")
        return None

def get_recommendations(reader_info, book_list, prompt_recommendation=PROMPT_RECOMMENDATION):
    try:
        formatted_prompt = prompt_recommendation.format(
            book_list=book_list, 
            reader_info=reader_info
        )
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        message = client.messages.create(
            model="claude-sonnet-4-0",
            max_tokens=2000,
            temperature=0.9,
            system=formatted_prompt,
            messages=[
                {"role": "user", "content": f"Based on these books:\n{book_list}"}
            ]
        )
        try:
            response_text = message.content[0].text
            # Find the dictionary part of the response
            dict_start = response_text.find('{')
            dict_end = response_text.rfind('}') + 1
            if dict_start >= 0 and dict_end > dict_start:
                dict_str = response_text[dict_start:dict_end]
                recommendations_dict = dict_str
            else:
                # Fallback if parsing fails
                recommendations_dict = {
                    "about you": "Unknown",
                    "recommendations": "Unknown",
                    
                }
        except Exception as e:
            print(f"Error parsing response: {e}")
            recommendations_dict = {
                "about you": "Unknown",
                "recommendations": "Unknown",
                
            }

        return recommendations_dict
    except Exception as e:
        st.error(f"Error with Anthropic API: {str(e)}")
        st.error("Please check your Anthropic API key")
        return None

def get_book_description(book_list, prompt_book_description=PROMPT_BOOK_DESCRIPTION):
    formatted_prompt = prompt_book_description.format(
        book_list=book_list
    )
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    message = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=1000,
        temperature=0.9,
        system=formatted_prompt,
        messages=[
            {"role": "user", "content": f"Based on these books:\n{book_list}"}
        ]
    )
    try:
        response_text = message.content[0].text
        
        return response_text
      
    except Exception as e:
        print(f"Error parsing response: {e}")
        return "[]"
        
    



__all__ = ['get_recommendations', 'infer_sociotype', 'extract_books_and_authors']

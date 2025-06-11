import base64
import os
from google import genai
from google.genai import types
from io import BytesIO
import anthropic
import json
import random
from prompts import prompt_books, prompt_reader_info, prompt_recommendation

def extract_books_and_authors(file, prompt=prompt_books):
    client=genai.Client(
            api_key=os.environ.get("GOOGLE_API_KEY"),
        )
    # file = client.files.upload(file='/Users/Olga/CS_projects/bookclub_for_one/assets/IMG_9D13EB33-A45D-483E-BCCF-D0CDF6143877.JPEG')
    response = client.models.generate_content(
        model="learnlm-2.0-flash-experimental",
        contents=[prompt, file]
    )
    return response.text

def infer_sociotype(books, prompt_reader_info=prompt_reader_info):
    """
    Infer sociotype, age range and topics based on book preferences using Claude.
    
    Args:
        books (list): List of book data dictionaries containing title, dewey, description, and vibe
        
    Returns:
        dict: Dictionary containing:
            - sociotype: str, the inferred sociotype (e.g., "IEI", "LII", etc.)
            - age_range: str, the inferred age range
            - topics: list, main topics of interest
            - genres: list, main book genres
            - subgenres: list, main book subgenres
            - vibe: list, main vibe of the books
    """
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1000,
        temperature=0.7,
        system=prompt_reader_info,
        messages=[
            {"role": "user", "content": f"Based on these books:\n{books}"}
        ]
    )

    # Parse the response into a dictionary
    try:
        response_text = message.content[0].text
        # Find the dictionary part of the response
        dict_start = response_text.find('{')
        dict_end = response_text.rfind('}') + 1
        if dict_start >= 0 and dict_end > dict_start:
            dict_str = response_text[dict_start:dict_end]
            reader_dict = dict_str
        else:
            # Fallback if parsing fails
            reader_dict = {
                "sociotype": "Unknown",
                "age_range": "Unknown",
                "topics": ["Unknown"],
                "genres": ["Unknown"], 
                "subgenres": ["Unknown"],
                "vibe": ["Unknown"]
            }
    except Exception as e:
        print(f"Error parsing response: {e}")
        reader_dict = {
            "sociotype": "Unknown",
            "age_range": "Unknown",
            "topics": ["Unknown"],
            "genres": ["Unknown"],
            "subgenres": ["Unknown"],
            "vibe": ["Unknown"]
        }

    return reader_dict


def get_recommendations(reader_info, book_list, prompt_recommendation=prompt_recommendation):
    formatted_prompt=prompt_recommendation.format(
        book_list=book_list, 
        reader_info=reader_info)
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    message = client.messages.create(
        model="claude-sonnet-4-0",
        max_tokens=2000,
        temperature=0.8,
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
                "music": ["Unknown"]
            }
    except Exception as e:
        print(f"Error parsing response: {e}")
        recommendations_dict = {
            "about you": "Unknown",
            "recommendations": "Unknown",
            "music": ["Unknown"]
        }

    return recommendations_dict
    



__all__ = ['get_recommendations', 'infer_sociotype', 'extract_books_and_authors']

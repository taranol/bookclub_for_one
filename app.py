import streamlit as st
from PIL import Image
from book_llm import get_recommendations, infer_sociotype, extract_books_and_authors
from test_book import display_books
#--------
#Import LLM clients
import base64
import os
# from google import genai
# from google.genai import types
# from io import BytesIO
# import anthropic
import json
import requests
import streamlit.components.v1 as components
import random

# from bs4 import BeautifulSoup
# import cloudscraper

# scraper = cloudscraper.create_scraper()  # Handles Cloudflare


# --------------------------------
# Book Utils functions
# --------------------------------


# ---------------------------
# LLM functions
# ---------------------------

# def extract_books_and_authors(file, prompt):
#     client=genai.Client(
#             api_key=os.environ.get("GOOGLE_API_KEY"),
#         )
#     # file = client.files.upload(file='/Users/Olga/CS_projects/bookclub_for_one/assets/IMG_9D13EB33-A45D-483E-BCCF-D0CDF6143877.JPEG')
#     response = client.models.generate_content(
#         model="learnlm-2.0-flash-experimental",
#         contents=[prompt, file]
#     )
#     return response.text

# def infer_sociotype(books, prompt_reader_info):
#     """
#     Infer sociotype, age range and topics based on book preferences using Claude.
    
#     Args:
#         books (list): List of book data dictionaries containing title, dewey, description, and vibe
        
#     Returns:
#         dict: Dictionary containing:
#             - sociotype: str, the inferred sociotype (e.g., "IEI", "LII", etc.)
#             - age_range: str, the inferred age range
#             - topics: list, main topics of interest
#             - genres: list, main book genres
#             - subgenres: list, main book subgenres
#             - vibe: list, main vibe of the books
#     """
#     client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
#     message = client.messages.create(
#         model="claude-3-5-sonnet-20240620",
#         max_tokens=1000,
#         temperature=0.7,
#         system=prompt_reader_info,
#         messages=[
#             {"role": "user", "content": f"Based on these books:\n{books}"}
#         ]
#     )

#     # Parse the response into a dictionary
#     try:
#         response_text = message.content[0].text
#         # Find the dictionary part of the response
#         dict_start = response_text.find('{')
#         dict_end = response_text.rfind('}') + 1
#         if dict_start >= 0 and dict_end > dict_start:
#             dict_str = response_text[dict_start:dict_end]
#             reader_dict = dict_str
#         else:
#             # Fallback if parsing fails
#             reader_dict = {
#                 "sociotype": "Unknown",
#                 "age_range": "Unknown",
#                 "topics": ["Unknown"],
#                 "genres": ["Unknown"], 
#                 "subgenres": ["Unknown"],
#                 "vibe": ["Unknown"]
#             }
#     except Exception as e:
#         print(f"Error parsing response: {e}")
#         reader_dict = {
#             "sociotype": "Unknown",
#             "age_range": "Unknown",
#             "topics": ["Unknown"],
#             "genres": ["Unknown"],
#             "subgenres": ["Unknown"],
#             "vibe": ["Unknown"]
#         }

#     return reader_dict


# def get_recommendations(reader_info, book_list, prompt_recommendation):
#     formatted_prompt=prompt_recommendation.format(
#         book_list=book_list, 
#         reader_info=reader_info)
#     client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
#     message = client.messages.create(
#         model="claude-sonnet-4-0",
#         max_tokens=2000,
#         temperature=0.8,
#         system=formatted_prompt,
#         messages=[
#             {"role": "user", "content": f"Based on these books:\n{book_list}"}
#         ]
#     )
#     try:
#         response_text = message.content[0].text
#         # Find the dictionary part of the response
#         dict_start = response_text.find('{')
#         dict_end = response_text.rfind('}') + 1
#         if dict_start >= 0 and dict_end > dict_start:
#             dict_str = response_text[dict_start:dict_end]
#             recommendations_dict = dict_str
#         else:
#             # Fallback if parsing fails
#             recommendations_dict = {
#                 "about you": "Unknown",
#                 "recommendations": "Unknown",
#                 "music": ["Unknown"]
#             }
#     except Exception as e:
#         print(f"Error parsing response: {e}")
#         recommendations_dict = {
#             "about you": "Unknown",
#             "recommendations": "Unknown",
#             "music": ["Unknown"]
#         }

#     return recommendations_dict
    

# #--------------------------------
# # Prompts
# #--------------------------------
# prompt_books='''Please extract all books and authors from the photo. Make sure they are real books.  If there are no books in the photo, report "No books found".  Report only a list of books and authors.'''
# prompt_reader_info = """You are a psychologist with expertise in socionics and background in literature. 
# Analyze the given list of books and infer:
# 0. Create three short descriptions of the reader based on the books and the sociotype short description of the reader based on the books describing his personality, values, interests, etc. Create 3 short vignettes with engaging description.
#     (E.g. 1:  🧐 " You're a Seeker of Meaning in Chaos
#     You're drawn to deep philosophical questions, existential uncertainty, and narratives that wrestle with mortality (Broch, Coetzee, Lawrence). You embrace complexity over clarity.
#     2:  📚 " You Trust the Power of Story to Uncover Truth
#     Whether through surrealist fragments (Artaud), postmodern irony (Pynchon), or historical retellings (Kneale, Edge), you believe fiction reveals what history and politics often hide.
#     3: 💔 " You're Emotionally Courageous
#     Your taste for books dealing with trauma, silence, and redemption (Wallant, Norman) shows a willingness to face the hardest truths of the human condition — with empathy, not cynicism.
#     " )

# 1. Generate a short (2-3 sentences) description of the reader's Jungian profile. Describe readers strength and weaknesses based on the sociotype.
# 2. Provide inferred sociotype of the reader based on the books (e.g., "IEI", "LII", etc.)  
# 3. The probable age range of the reader (Begginer Reader, Kids, Older Kids, Young adult, Adult)
# 4. book genres, sorted from most to least common
# 5. book subgenres, sorted from most to least common
# 6. The main topics of interest based on the books (pick up to 5)
# 7. The vibe of the books (pick up to 5) sorted from strongest to weakest


# Respond in a dictionary with the following keys:
# - about you: (description 1: , description 2: , description 3: ),
# - Jungian profile: string including dominant type from 16 personality types with description of strengths and weaknesses,
# - sociotype: string (the sociotype code and name),

# - age_range: string,
# - genres: string, prevalent genre e.g "non-fiction" ,
# - subgenres: top 3 subgenres e.g "romance", "fantasy", "mystery",
# - topics: dictionary (e.g., {"love": 3, "social issues": 2, "travel": 1}) (limit to 5),
# - vibe: list (e.g., ("dark", "funny", "epic", "imaginative", "relatable") (limit to 5)
# """
# prompt_recommendation=  """You are a literary expert and Jungian psychologist with love of books and music. 
# Based on the following  book data
#     and what you know about the reader, 
#     suggest new books for the reader. Stay within reader's age range. Base recommendations on requested sociotype and interests.
#     Suggest the books that are not in the reader's list of books. Try to not suggest more then one book by the same author.
#     generate an output in JSON format with the following fields:
    
#     "recommendations": 
    
#         "books Identity": list of 4 books formatted as "Title (Author)" that the reader with suggested socionic profile and interests like to read.  

#         "books Dual": list of 4 Books based on the Dual Sociotype and a mixture of preffered and least preffered genres formatted as "Title (Author)",
#         "books Mirror": list of 4 Books based on Mirror Sociotype and a mixture of preffered and least preffered genres formatted as "Title (Author)",
#         "books Opposite": list of 4 Books based on the Conflict Sociotype and totally opposite to what the original sociotype would like in topics formatted as "Title (Author)"
#         "books Identity_2": Suggest  another 4 books for readers socionic profile but in a different genre (i.e.fiction/nonfiction, biography/how to, etc)
#         Format as "Title (Author)"
    
    
# Here are the books:
# {book_list}
# Here is the reader info:
# {reader_info}

# """ 

# books=extract_books_and_authors(prompt_books, image)


#--------------------------------
# Streamlit app Main
#--------------------------------

st.set_page_config(page_title="Book Club for one", layout="wide", initial_sidebar_state="collapsed")
with st.sidebar:
    if st.button("Clear Cache"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.rerun()
st.subheader(""" Your Literary Individuation Journey """)
st.image("assets/bookclub_for_one.jpeg", use_container_width=True)
st.title("Book Club for One")

st.markdown("## Welcome to a Bookshelf Analyzer App")
st.markdown ("""
        Ever wondered what your bookshelf says about you? Upload a photo of your books and discover insights about your personality through the lens of Jungian psychology!

## How It Works
1. **Snap a Photo** - Take a clear picture of your bookshelf
2. **Get Your Reading** - Our AI analyzes your book collection and reveals personality insights
3. **Discover New Books** - Receive personalized book recommendations tailored to your unique psychological profile

## The Psychology Behind It
This app draws inspiration from Carl Jung's theories about personality types and psychological preferences. By examining the genres, authors, and themes in your collection, we create a fun personality profile that reflects your reading preferences and interests.

## Important Note
This is purely for entertainment! While based on established psychological concepts, this app is designed for fun exploration and book discovery - not as professional psychological assessment or medical advice.

## Support Local Bookstores 📚
Book recommendations include links to Bookshop.org, where your purchases support local independent bookstores and libraries. As a transparency note: I earn a small commission on purchases made through these links.

Ready to see what your books reveal about you? Upload your bookshelf photo and let's dive in! 📖✨""")
            
st.markdown("---")
st.markdown("### Upload Your Bookshelf Image")

uploaded_file = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"])




if uploaded_file:
    image = Image.open(uploaded_file)
    image.thumbnail((800, 600))
    
    # Create two columns
    col1, col2 = st.columns(2)
    
    # Display image in first column
    with col1:
        st.image(image, caption="Photo of your bookshelf", use_container_width=True, width=400)
    
    # Display text area in second column
    # Extract books from photo

    with col2:
        if st.button("Extract Books"):
            book_list = extract_books_and_authors(image)
            st.session_state['books'] = book_list
        
        if 'books' in st.session_state:
            edited_books = st.text_area("On your Bookshelf (editable)", value=st.session_state['books'], height=400)
            book_list = [line.strip() for line in edited_books.splitlines() if line.strip()]
            random.shuffle(book_list)
    st.markdown("""
        <style>
        div.stButton > button {
            display: block;
            margin: 0 auto;
        }
        </style>
        """, unsafe_allow_html=True)

    # book_list = [line.strip() for line in edited_books.splitlines() if line.strip()]
    # random.shuffle(book_list)

    if st.button("What your books say about you?"):
        
        with st.spinner("🔍 Analyzing your books..."):
            analysis = infer_sociotype(book_list)
            # Parse if needed
            if isinstance(analysis, str):
                analysis = json.loads(analysis)
            st.session_state['analysis'] = analysis

        with st.spinner("🎉 Getting Recommendations..."):
            recommendations=get_recommendations(analysis, book_list)
            recommendations=json.loads(recommendations)
            st.json(recommendations)
            output_books=recommendations
            jungian_profile=recommendations['reader']['jungian']
            about_you=recommendations['reader']['about']
            complete_you=recommendations['recommendations']['books Identity']
            books_Dual=recommendations['recommendations']['books Dual']
            books_Mirror=recommendations['recommendations']['books Mirror']
            books_Opposite=recommendations['recommendations']['books Opposite']
            books_Identity_2=recommendations['recommendations']['books Identity_2']
            st.session_state['recommendations'] = recommendations
                    

        # Always display the analysis if it exists
            if 'recommendations' in st.session_state:
                
                st.markdown("### 📖 About You")

                st.markdown(jungian_profile)
                
                st.markdown(about_you[0])
                st.markdown(about_you[1])
                st.markdown(about_you[2])
                # Display each description separately
                
            
            

                        
                st.markdown(""" ### Books That Might Already Be on Your Shelf:
                            These are the books that people with your sociotype would like.
                                """)
                
                
                display_books(complete_you)

                st.markdown("""You might also consider other books that are in a different genre. These books are based on your Identity personality type but in a different genre.""")
                # st.json(books_Identity_2)
                display_books(books_Identity_2)

                st.markdown("""### Books for your Dual. 
                            Dual is a person with similar values but the opposite personality type
                            that naturally complements you. These are the books that might help you understand your "blind spots" and "shadow" """)
                # st.json(books_Dual)
                display_books(books_Dual)

                st.markdown("""### Books your Cool Friend wants to talk about. 
                            hese books are based on your Mirror personality type: a person whom you might find fascinating and want to learn more about.""")
                # st.json(books_Mirror)
                display_books(books_Mirror)
                

                st.markdown("""### Books you will hate. 
                            These books are based on your Opposite personality type: a person whom you might find annoying and want to avoid.""")
                # st.json(books_Opposite)
                display_books(books_Opposite)
        
    
                        

                
# # In your main app code:
#     if st.button("Show Complete Book Info"):
#         if 'books' in st.session_state:
#             book_list = [line.strip() for line in edited_books.splitlines() if line.strip()]
#             with st.spinner("Gathering book information..."):
#                 complete_info = get_complete_book_info(book_list)
#                 display_book_grid(complete_info)
            
        # recs = recommend_books(analysis)
        # book_titles = recs.get("books", [])
        
        # metadata_list = [get_book_metadata(title) for title in book_titles]

        # st.markdown("### 📖 Recommended Books")
        # rows = [metadata_list[i:i+4] for i in range(0, len(metadata_list), 4)]
        
        # for row in rows:
        #     cols = st.columns(len(row))
        #     for col, book in zip(cols, row):
        #         col.image(book["cover_url"], caption=book["title"],  use_container_width=True)
        
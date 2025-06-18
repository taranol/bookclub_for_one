
import os
import tempfile
os.environ['ISBNTOOLS_LOG_LEVEL'] = 'OFF'

import streamlit as st
from PIL import Image
from llm_google import extract_books_and_authors, get_reader_info_genai, get_recommendations_genai

from book_utils import display_books
#--------
#Import LLM clients
import base64
import os

import json
import requests
import streamlit.components.v1 as components
import random


# os.environ['ISBNTOOLS_LOG_LEVEL'] = 'CRITICAL'
# or completely disable logging



PROMPT_BOOKS = st.secrets["prompts"]["prompt_books"]
PROMPT_READER_INFO = st.secrets["prompts"]["prompt_reader_info"]
PROMPT_RECOMMENDATION = st.secrets["prompts"]["prompt_recommendation"]



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
            book_list = extract_books_and_authors(image, PROMPT_BOOKS)
            st.session_state['book_list'] = book_list
        
        if 'book_list' in st.session_state:
            edited_books = st.text_area("On your Bookshelf (editable)", value=st.session_state['book_list'], height=400)
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


    # Then in the "What your books say about you?" button
    if st.button("What your books say about you?"):
        if 'book_list' not in st.session_state:
            st.error("Please extract books first!")
            st.stop()
            
        with st.spinner("🔍 Analyzing your books..."):
            formatted_prompt = PROMPT_READER_INFO.format(book_list=st.session_state['book_list'])
            analysis = get_reader_info_genai(formatted_prompt)
            # st.markdown(analysis)
            
            if analysis is None:
                st.error("Failed to analyze books. Please try again.")
                st.stop()
            else:
                st.session_state['analysis'] = analysis
                jungian_profile = analysis['jungian']
                about_you = analysis['description']
                st.markdown("### 📖 About You")
                st.markdown(jungian_profile)
                st.markdown(about_you[0])
                st.markdown(about_you[1])
                st.markdown(about_you[2])

            
            
            # try:
            #     # Parse the JSON string into a dictionary
            #     analysis_dict = json.loads(analysis)
            #     st.session_state['analysis'] = analysis_dict
            # except json.JSONDecodeError as e:
            #     st.error(f"Error parsing analysis: {str(e)}")
            #     st.error("Please try again.")
            #     st.stop()

        with st.spinner("🎉 Getting Recommendations..."):
            formatted_prompt = PROMPT_RECOMMENDATION.format(book_list=st.session_state['book_list'], reader_info=analysis)
            recommendations = get_recommendations_genai(formatted_prompt)
            # st.markdown(recommendations)
            if recommendations is None:
                st.error("Failed to get recommendations. Please try again.")
                st.stop()
            
            try:
                # Parse the JSON string into a dictionary
                recommendations_dict = recommendations
                # st.json(recommendations_dict)
                st.session_state['recommendations'] = recommendations_dict
            except json.JSONDecodeError as e:
                st.error(f"Error parsing recommendations to dictionary: {str(e)}")
                st.error("Please try again.")
                st.stop()

            
            
            # st.json(recommendations_dict)
            # output_books = recommendations_dict['recommendations']['books Identity']
           
            complete_you = recommendations_dict['identity']
            
            books_Dual = recommendations_dict['dual']
        
            books_Mirror = recommendations_dict['mirror']
            
            books_Opposite = recommendations_dict['opposite']
            
            books_Identity_2 = recommendations_dict['identity_2']
            

            

            st.markdown(""" 
            ## Books That Might Already Be on Your Shelf:
            These are the books that people with your Jungian profile might like. I have found titles that align with your unique interests and thinking patterns.
                            """)
            for book in complete_you:
                st.markdown(f"***{book['title']} by ({book['author']}).*** {book['description']}")
            display_books(complete_you)

            st.markdown("""
            Here are some other books you might love! I've picked these based on your Identity personality type, but switched up the genre to give you something fresh and exciting to explore.
                        """)
            for book in books_Identity_2:
                st.markdown(f"***{book['title']} by ({book['author']}).*** {book['description']}")
            display_books(books_Identity_2)

            st.markdown("""
            ### Books for your Dual. 
            Your Dual is someone who shares your core values but has a completely opposite personality type—they're your natural complement. These books offer a fascinating window into your "blind spots" and help you explore the hidden "shadow" aspects of your psyche.
                        """)
            for book in books_Dual:
                st.markdown(f"***{book['title']} by ({book['author']}).*** {book['description']}")
            
            display_books(books_Dual)

            st.markdown("""
            ### Books your Cool Friend wants to talk about. 
            Your Mirror shares your core interests and way of seeing the world, but approaches problems from a refreshingly different angle—they're like your intellectual sparring partner. These books are selected to resonate with this unique dynamic, offering perspectives that will both challenge and complement your own thinking.
                        """)
            for book in books_Mirror:
                st.markdown(f"***{book['title']} by ({book['author']}).*** {book['description']}")
           
            display_books(books_Mirror)
            
            st.markdown("""
            ### Books you will hate. 
            Your Conflict represents a completely opposite worldview—they're your psychological polar opposite who challenges every assumption you hold dear. These books are curated to help you understand this fundamentally different perspective, offering insights into motivations and thinking patterns that might seem alien.
                        """)
            for book in books_Opposite:
                st.markdown(f"***{book['title']} by ({book['author']}).*** {book['description']}")
            
            display_books(books_Opposite)
        
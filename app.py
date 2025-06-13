import streamlit as st
from PIL import Image
from book_llm import get_recommendations, infer_sociotype, extract_books_and_authors, get_book_description
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
            if analysis is None:
                st.error("Failed to analyze books. Please try again.")
                st.stop()
            
            # try:
            #     # Parse the JSON string into a dictionary
            #     analysis_dict = json.loads(analysis)
            #     st.session_state['analysis'] = analysis_dict
            # except json.JSONDecodeError as e:
            #     st.error(f"Error parsing analysis: {str(e)}")
            #     st.error("Please try again.")
            #     st.stop()

        with st.spinner("🎉 Getting Recommendations..."):
            recommendations = get_recommendations(analysis, book_list)
            if recommendations is None:
                st.error("Failed to get recommendations. Please try again.")
                st.stop()
            
            try:
                # Parse the JSON string into a dictionary
                recommendations_dict = json.loads(recommendations)
                st.session_state['recommendations'] = recommendations_dict
            except json.JSONDecodeError as e:
                st.error(f"Error parsing recommendations: {str(e)}")
                st.error("Please try again.")
                st.stop()
            # st.json(recommendations_dict)
            # output_books = recommendations_dict['recommendations']['books Identity']
            jungian_profile = recommendations_dict['reader']['jungian']
            about_you = recommendations_dict['reader']['about']
            complete_you = recommendations_dict['recommendations']['identity']
            you_books = get_book_description(book_list=complete_you)
            books_Dual = recommendations_dict['recommendations']['dual']
            dual_books = get_book_description(book_list=books_Dual)
            books_Mirror = recommendations_dict['recommendations']['mirror']
            mirror_books = get_book_description(book_list=books_Mirror)
            books_Opposite = recommendations_dict['recommendations']['opposite']
            opposite_books = get_book_description(book_list=books_Opposite)
            books_Identity_2 = recommendations_dict['recommendations']['identity_2']
            identity_2_books = get_book_description(book_list=books_Identity_2)

            st.markdown("### 📖 About You")
            st.markdown(jungian_profile)
            st.markdown(about_you[0])
            st.markdown(about_you[1])
            st.markdown(about_you[2])

            st.markdown(""" 
            ## Books That Might Already Be on Your Shelf:
            These are the books that people with your Jungian profile might like. I have found titles that align with your unique interests and thinking patterns.
                            """)
            st.markdown(you_books)
            display_books(complete_you)

            st.markdown("""
            Here are some other books you might love! I've picked these based on your Identity personality type, but switched up the genre to give you something fresh and exciting to explore.
                        """)
            st.markdown(identity_2_books)
            display_books(books_Identity_2)

            st.markdown("""
            ### Books for your Dual. 
            Your Dual is someone who shares your core values but has a completely opposite personality type—they're your natural complement. These books offer a fascinating window into your "blind spots" and help you explore the hidden "shadow" aspects of your psyche.
                        """)
            st.markdown(dual_books)
            display_books(books_Dual)

            st.markdown("""
            ### Books your Cool Friend wants to talk about. 
            Your Mirror shares your core interests and way of seeing the world, but approaches problems from a refreshingly different angle—they're like your intellectual sparring partner. These books are selected to resonate with this unique dynamic, offering perspectives that will both challenge and complement your own thinking.
                        """)
            st.markdown(mirror_books)
            display_books(books_Mirror)
            
            st.markdown("""
            ### Books you will hate. 
            Your Conflict represents a completely opposite worldview—they're your psychological polar opposite who challenges every assumption you hold dear. These books are curated to help you understand this fundamentally different perspective, offering insights into motivations and thinking patterns that might seem alien.
                        """)
            st.markdown(opposite_books)
            display_books(books_Opposite)
        
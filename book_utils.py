
import os
import tempfile
import logging

# Set up logging configuration before any other imports
os.environ['ISBNTOOLS_LOG_LEVEL'] = 'CRITICAL'
temp_dir = tempfile.gettempdir()
os.environ['ISBNTOOLS_LOG_FILE'] = os.path.join(temp_dir, 'isbntools.log')

# Override logging to prevent file creation in restricted directories
def safe_log_config(*args, **kwargs):
    if 'filename' in kwargs and ('/home/adminuser/venv' in str(kwargs['filename']) or 'isbntools' in str(kwargs['filename'])):
        kwargs.pop('filename', None)
    return logging._original_basicConfig(*args, **kwargs)

# Store original and replace
if not hasattr(logging, '_original_basicConfig'):
    logging._original_basicConfig = logging.basicConfig
    logging.basicConfig = safe_log_config

import streamlit as st
import requests
from isbntools.app import isbn_from_words
from streamlit.components.v1 import html
from bs4 import BeautifulSoup
import cloudscraper

from PIL import Image, ImageDraw, ImageFont
import io

scraper = cloudscraper.create_scraper()  # Handles Cloudflare

def get_isbn(title, author):
    query=f"{title} by {author}"
    isbn=isbn_from_words(query)
    if len(isbn)==13:
        return isbn
    return None

def get_cover_by_isbn(isbn):
    url = f'https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}'
    response = requests.get(url)
    data = response.json()

    if 'items' not in data or not data['items']:
        return None

    image_links = data['items'][0]['volumeInfo'].get('imageLinks', {})

    # Try to get medium, fall back to larger or smaller
    return (
        image_links.get('medium') or
        image_links.get('large') or
        image_links.get('thumbnail') or
        image_links.get('smallThumbnail') )
        

def book_in_shop(isbn):       
    url = f"https://bookshop.org/a/114086/{isbn}"
    response = scraper.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    if "a book by" in soup.title.string:
        return True
    else:
        return False
    

def display_bookshop_widget(isbn, max_width="50%", scale=0.8):
    st.write(f"🔍 DEBUG: Trying to display widget for ISBN: {isbn}")
    html_code = f"""
    <div style="
        width: 100%;
        display: flex;
        justify-content: flex-start;
        align-items: center;
        overflow: visible;
    ">
        <div style="
            transform: scale({scale});
            transform-origin: top left;
            width: fit-content;
        ">
            <script 
                src="https://bookshop.org/widgets.js" 
                data-type="book" 
                data-affiliate-id="114086" 
                data-sku="{isbn}">
            </script>
        </div>
    </div>
    """
    st.components.v1.html(html_code, height=500)
    st.write("✅ Widget HTML generated")

def display_bookshop_widget_search(scale=0.5):
    """Display Bookshop.org widget for a given ISBN."""
    st.write("🔍 DEBUG: Displaying search widget")
    html_code = f"""
                <div style="
                    width: 100%;
                    display: flex;
                    justify-content: flex-start;
                    align-items: center;
                    overflow: visible;
                ">
                    <div style="
                        transform: scale({scale});
                        transform-origin: top left;
                        width: fit-content;
                    ">
                 <script 
                    src="https://bookshop.org/widgets.js" 
                    data-type="search" 
                    data-include-branding="false" 
                    data-affiliate-id="114086">
                </script>
                </div>
                </div>
                """
    
    st.components.v1.html(html_code, height=50)
    st.write("✅ Search widget HTML generated")

def create_book_thumbnail(title, author):
    """Create a thumbnail image with book title and author when no cover is available."""
    # Create a blank image with a light gray background
    width = 200
    height = 300
    background_color = (240, 240, 240)  # Light gray
    image = Image.new('RGB', (width, height), background_color)
    draw = ImageDraw.Draw(image)
    
    # Try to load a font, fall back to default if not available
    try:
        title_font = ImageFont.truetype("Arial", 24)
        author_font = ImageFont.truetype("Arial", 18)
    except:
        title_font = ImageFont.load_default()
        author_font = ImageFont.load_default()
    
    # Add a border
    border_color = (200, 200, 200)  # Darker gray
    draw.rectangle([(0, 0), (width-1, height-1)], outline=border_color, width=2)
    
    # Add title and author text
    # Wrap text to fit width
    def wrap_text(text, font, max_width):
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_width - 40:  # 40px padding
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        return lines
    
    # Draw title
    title_lines = wrap_text(title, title_font, width)
    y_position = 50
    for line in title_lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        text_width = bbox[2] - bbox[0]
        x_position = (width - text_width) // 2
        draw.text((x_position, y_position), line, font=title_font, fill=(0, 0, 0))
        y_position += 30
    
    # Draw author
    author_lines = wrap_text(f"by {author}", author_font, width)
    y_position += 20
    for line in author_lines:
        bbox = draw.textbbox((0, 0), line, font=author_font)
        text_width = bbox[2] - bbox[0]
        x_position = (width - text_width) // 2
        draw.text((x_position, y_position), line, font=author_font, fill=(100, 100, 100))
        y_position += 25
    
    # Convert to bytes for display
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    return img_byte_arr    
        

def display_books(book_list):
    st.write(f"🔍 DEBUG: Processing {len(book_list)} books")
    
    for i in range(0, min(len(book_list), 8), 4):
        cols = st.columns(4)       # Display up to 4 books in this row
        for j in range(4):
            if i + j < len(book_list):
                with cols[j]:
                    try:
                        title = book_list[i+j]['title']
                        author = book_list[i+j]['author']
                        st.write(f"📖 **{title}** by {author}")
                        
                        isbn = get_isbn(title, author)
                        st.write(f"📚 ISBN: {isbn}")
                        
                        if isbn:
                            cover = get_cover_by_isbn(isbn)
                            st.write(f"🖼️ Cover found: {cover is not None}")
                            
                            in_shop = book_in_shop(isbn)
                            st.write(f"🛒 In bookshop: {in_shop}")
                            
                            if in_shop:
                                display_bookshop_widget(isbn)
                            elif cover is not None: 
                                st.image(cover, use_container_width=True)
                                display_bookshop_widget_search()
                            else: 
                                thumbnail = create_book_thumbnail(title, author)
                                st.image(thumbnail, use_container_width=True)
                                display_bookshop_widget_search()
                        else:
                            st.write("❌ No ISBN found")
                            thumbnail = create_book_thumbnail(title, author)
                            st.image(thumbnail, use_container_width=True)
                            display_bookshop_widget_search()
                        
                        st.write("---")  # Separator between books
                        
                    except Exception as e:
                        st.error(f"Error processing book: {str(e)}")
                        st.write(f"Book data: {book_list[i+j]}")

__all__ = ['display_books']
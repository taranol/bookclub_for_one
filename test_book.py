import streamlit as st
import requests
from streamlit.components.v1 import html
from bs4 import BeautifulSoup
import cloudscraper

from PIL import Image, ImageDraw, ImageFont
import io

scraper = cloudscraper.create_scraper()  # Handles Cloudflare



def get_book_metadata(book_list):
    """Get metadata for books from Google Books API."""
    metadata = []
    for book in book_list:
        
        # Parse "Book Name (Author)" format
        if "(" in book and ")" in book:
            title = book[:book.find("(")].strip()
            author = book[book.find("(")+1:book.find(")")].strip()
        else:
            title = book
            author = ""
            
        # Construct query for Google Books API
        query = f"intitle:{book}"
        if author:
             query += f"+inauthor:{author}"
            
        url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
        
        try:
            response = requests.get(url).json()
            isbn13s = []

            if 'items' in response and len(response['items']) > 0:
                book_info = response['items'][0]['volumeInfo']
                title = book_info.get('title', None)
                author = book_info.get('authors', None)
                # cover = book_info.get('imageLinks', {})
                # description = book_info.get('description', None)
                cover = next((img for k in ['large','medium','small','thumbnail','smallThumbnail'] if (img := book_info.get('imageLinks', {}).get(k))), None)
                isbn = next((id['identifier'] for id in book_info.get('industryIdentifiers', []) if id['type'] == 'ISBN_13'), None)
                
                isbn13s.append(isbn)

                if len(response['items'])>0:
                    for item in response['items'][1:]:
                        info=item.get('volumeInfo', {})
                        next_title=info.get('title', None)
                        next_author=info.get('authors', None)
                        next_isbn=next((id['identifier'] for id in info.get('industryIdentifiers', []) 
                               if id['type'] == 'ISBN_13'), None)
                        if  next_title == title and (author == next_author or 
                        author in next_author or 
                        next_author in author):
                            isbn13s.append(next_isbn)
                
                isbn = list(set(isbn13s))
           
                metadata.append({
                        "title": title,
                        "author": author,
                        "isbn13": isbn,
                        "cover": cover, 
                        # "description": description
                    })
            else:
                metadata.append({
                    "title": title,
                    "author": author,
                    "isbn13": None,
                    "cover": None
                })
  
        except Exception as e:
            print(f"Error fetching metadata for {title}: {e}")
            metadata.append({
                "title": title,
                "author": author,
                "isbn13": None,
                "cover": None
            })
    
    return metadata




def book_in_shop(isbn_list):
    test=[]
    for isbn in isbn_list:
            
            url = f"https://bookshop.org/a/114086/{isbn}"
            response = scraper.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            if "a book by" in soup.title.string:
                    test.append(isbn)
    if len(test)>0:
        return max(test)
    else:
        return 


def display_bookshop_widget(isbn, max_width="50%", scale=0.5):
    """Display Bookshop.org widget for a given ISBN."""
    
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
                    data-type="book_button"
                    data-affiliate-id="114086"
                    data-sku="{isbn}">
                </script>
                </div>
                </div>
                """
    st.components.v1.html(html_code, height=50)

def display_bookshop_widget_search( scale=0.5):
    """Display Bookshop.org widget for a given ISBN."""
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
                    src=https://bookshop.org/widgets.js 
                    data-type="search" 
                    data-include-branding="false" 
                    data-affiliate-id="114086">
                </script>
                </div>
                </div>
                """
    
    
    
    st.components.v1.html(html_code, height=50)

def create_book_thumbnail(title, author):
    """Create a thumbnail image with book title and author when no cover is available."""
    # Create a blank image with a light gray background
    width = 300
    height = 450
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
    books_metadata=get_book_metadata(book_list)   
    # st.text(books_metadata) 
    # st.text(len(books_metadata))           
    for i in range(0, min(len(books_metadata), 8), 4):
        cols = st.columns(4)       # Display up to 4 books in this row
        for j in range(4):
            if i + j < len(books_metadata):
            
                with cols[j]:
                    try:
                        if books_metadata[i+j]['cover']:
                            st.image(books_metadata[i+j]['cover'],  use_container_width=True)
                        else:
                            # Create and display thumbnail when no cover is available
                            thumbnail = create_book_thumbnail(
                                books_metadata[i+j]['title'],
                                books_metadata[i+j]['author'] if books_metadata[i+j]['author'] else "Unknown Author"
                            )
                            st.image(thumbnail, use_container_width=True)
                        item = book_in_shop(books_metadata[i+j]['isbn13'])
                        # st.write(item)
                        if len(item)==13:
                            display_bookshop_widget(item)
                        else:
                            display_bookshop_widget_search()
                        
                            
                    except:
                        display_bookshop_widget_search()

# books=['The Rings of Saturn (W.G. Sebald)', 'The Book of Disquiet (Fernando Pessoa)', 'Stoner (John Williams)', 'The Passion According to G.H. (Clarice Lispector)', 'The Man Without Qualities (Robert Musil)', 'Dept. of Speculation (Jenny Offill)', 'The Waves (Virginia Woolf)', 'Austerlitz (W.G. Sebald)', 'The Notebooks of Malte Laurids Brigge (Rainer Maria Rilke)', 'My Struggle: Book 1 (Karl Ove Knausgård)']
# # books= [line.strip() for line in books.splitlines() if line.strip()]

# # Create an editable text area for books
# edited_books = st.text_area("Paste your book list here", height=200)

# if st.button("Get Books"):
#     import ast
#     book_list = ast.literal_eval(edited_books)
#     display_books(book_list)
    
# display_books(books)
__all__ = ['display_books']









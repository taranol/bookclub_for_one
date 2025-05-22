# Bookshelf Scanner

A Streamlit application that uses SmolLM2 to extract book and author names from photos of bookshelves.

## Setup

1. Create a conda environment:
```bash
conda create -n bookshelf python=3.10
conda activate bookshelf
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Make sure your conda environment is activated:
```bash
conda activate bookshelf
```

2. Run the Streamlit app:
```bash
streamlit run app.py
```

## Usage

1. Open your web browser and navigate to the URL shown in the terminal (usually http://localhost:8501)
2. Upload a photo of your bookshelf
3. Click "Extract Book Information" to process the image
4. View the extracted book and author names

## Notes

- The application works best with clear, well-lit photos of bookshelves
- Make sure book spines are clearly visible
- Processing time may vary depending on image size and complexity

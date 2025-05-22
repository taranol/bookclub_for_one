import streamlit as st
import torch
from transformers import AutoProcessor, AutoModelForVision2Seq
from PIL import Image
import io

# Set page config
st.set_page_config(
    page_title="Bookshelf Scanner",
    page_icon="📚",
    layout="wide"
)

# Initialize the model and processor
@st.cache_resource
def load_model():
    processor = AutoProcessor.from_pretrained("microsoft/smol-2")
    model = AutoModelForVision2Seq.from_pretrained("microsoft/smol-2")
    return processor, model

def process_image(image, processor, model):
    # Process the image
    inputs = processor(images=image, return_tensors="pt")
    
    # Generate text
    generated_ids = model.generate(
        pixel_values=inputs.pixel_values,
        max_length=100,
        num_beams=5,
        early_stopping=True
    )
    
    # Decode the generated text
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return generated_text

def main():
    st.title("📚 Bookshelf Scanner")
    st.write("Upload a photo of your bookshelf to extract book and author names")
    
    # Load model
    try:
        processor, model = load_model()
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return
    
    # File uploader
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # Display the uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        
        # Process button
        if st.button("Extract Book Information"):
            with st.spinner("Processing image..."):
                try:
                    # Process the image
                    result = process_image(image, processor, model)
                    
                    # Display results
                    st.subheader("Extracted Information")
                    st.write(result)
                    
                except Exception as e:
                    st.error(f"Error processing image: {str(e)}")

if __name__ == "__main__":
    main()

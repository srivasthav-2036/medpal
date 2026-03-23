import os
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ImageProcessor:
    def __init__(self):
        # Configure Gemini
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")
    
    def get_gemini_response(self, input_text, image):
        """Get response from Gemini model for image analysis"""
        if input_text != "":
            response = self.model.generate_content([input_text, image])
        else:
            response = self.model.generate_content(image)
        return response.text
    
    def process_image(self, uploaded_files):
        """Process uploaded images and return summary"""
        if not uploaded_files:
            return "No images uploaded"
        
        results = []
        for file_info in uploaded_files:
            file_type = file_info.get('type', '').lower()
            if file_type in ['png', 'jpg', 'jpeg']:
                try:
                    image = Image.open(file_info['filepath'])
                    response = self.get_gemini_response("""
    You are a madical assistant. Read the document and try to figure out the 
        patients problem. Answer the questions based on the uploaded document.
        If you cant answer the question, say I DONT KNOW instead of making up some answer. 
        Make sure you answer like a professional medical assistant. 
""", image)
                    results.append({
                        'filename': file_info['original_name'],
                        'analysis': response
                    })
                except Exception as e:
                    results.append({
                        'filename': file_info['original_name'],
                        'error': str(e)
                    })
        
        return results
    
    def answer_question(self, question, uploaded_files):
        """Answer questions about uploaded images"""
        if not uploaded_files:
            return "No images available to analyze"
        
        # For simplicity, we'll analyze the first image
        # In a production system, you might want to handle multiple images
        image_files = [f for f in uploaded_files if f.get('type', '').lower() in ['png', 'jpg', 'jpeg']]
        
        if not image_files:
            return "No valid image files found"
        
        try:
            image = Image.open(image_files[0]['filepath'])
            response = self.get_gemini_response(question, image)
            return response
        except Exception as e:
            return f"Error processing image: {str(e)}"

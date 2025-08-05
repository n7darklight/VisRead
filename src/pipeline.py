import io
import os
import requests
from PIL import Image
import time # Import the time module for delays
import base64 # Import for decoding the new API response

# --- Globals to hold initialized clients ---
# We keep them in the global scope to reuse them after the first load.
flux_client = None
gemma_model = None
imagen_model = None

def create_style_guide(paragraph: str) -> str:
    """
    Uses Gemma to create a style and character guide from the first paragraph of a story.
    """
    global gemma_model
    if gemma_model is None:
        # This will trigger the lazy load and configuration
        enhance_prompt_with_gemma("initialize")

    if not gemma_model:
        print("Gemma model not available, cannot create style guide.")
        return ""

    print("--- Creating Style Guide with Gemma ---")
    try:
        instructional_prompt = (
            "Read the following text from the first chapter of a story. "
            "Identify the main character(s) and the overall art style. "
            "Create a concise consistency guide for an AI image generator. "
            "For example: 'A young woman with long, flowing red hair, wearing green robes. The art style is a vibrant, detailed fantasy digital painting.' "
            "Only output the guide itself, with no extra text.\n\n"
            f"Text: \"{paragraph}\""
        )
        response = gemma_model.generate_content(instructional_prompt)
        guide = response.text.strip()
        print(f"--- Style Guide Created: {guide} ---")
        return guide
    except Exception as e:
        print(f"An error occurred during style guide creation: {e}")
        return ""

def enhance_prompt_with_gemma(paragraph: str, style_guide: str = None) -> str:
    """
    Enhances a prompt using the Gemma model, applying a style guide if provided.
    """
    global gemma_model
    
    # Lazy load and initialize on first call
    if gemma_model is None:
        print("--- First time initialization: Importing google.generativeai and configuring Gemma ---")
        import google.generativeai as genai
        try:
            GOOGLE_API_KEY = os.environ.get("GOOGLE_AI_API_KEY")
            if not GOOGLE_API_KEY:
                raise ValueError("GOOGLE_AI_API_KEY is not set.")
            genai.configure(api_key=GOOGLE_API_KEY)
            gemma_model = genai.GenerativeModel('gemma-3-27b-it')
            print("--- Gemma configured successfully ---")
        except Exception as e:
            print(f"Error configuring Google AI for Gemma: {e}")
            return paragraph # Return original paragraph if setup fails

    print("--- Enhancing Prompt with Gemma ---")
    try:
        # Build the prompt with the style guide if it exists
        if style_guide:
            instructional_prompt = (
                "You are an AI assistant for an image generator. Your task is to create a vivid image prompt based on the user's text, while strictly following a consistency guide. "
                f"CONSISTENCY GUIDE (MUST FOLLOW): '{style_guide}'.\n\n"
                "Now, based on the following paragraph, create a single, vivid, and artistic image prompt that adheres to the guide. "
                "Focus on the visual details, atmosphere, and the setting described in the paragraph. "
                "Do not add any explanations or introductory text. Just provide the prompt itself.\n\n"
                f"Paragraph: \"{paragraph}\""
            )
        else:
            # Original prompt without the guide
            instructional_prompt = (
                "Based on the following paragraph from a story, create a single, vivid, and artistic image prompt. "
                "Focus on the visual details, the atmosphere, the characters' appearance, and the setting. "
                "The prompt should be in English and formatted as a single, continuous sentence or a short paragraph suitable for an advanced text-to-image AI model. "
                "Do not add any explanations or introductory text. Just provide the prompt itself.\n\n"
                f"Paragraph: \"{paragraph}\""
            )
        
        response = gemma_model.generate_content(instructional_prompt)
        return response.text.strip()
    except Exception as e:
        print(f"An error occurred during prompt enhancement: {e}")
        return paragraph

def generate_with_flux(prompt: str) -> bytes:
    """Generates an image using the primary FLUX client (with lazy loading)."""
    global flux_client
    
    # Lazy load and initialize on first call
    if flux_client is None:
        print("--- First time initialization: Importing gradio_client and initializing FLUX.1 ---")
        from gradio_client import Client
        try:
            flux_client = Client("black-forest-labs/FLUX.1-Krea-dev")
            print("--- FLUX.1 Client Initialized ---")
        except Exception as e:
            print(f"Error initializing FLUX client: {e}")
            raise # Re-raise the exception to trigger the fallback

    print("--- Attempting Image Generation with FLUX.1 ---")
    result = flux_client.predict(prompt=prompt)
    if isinstance(result, tuple):
        result_path = result[0]
    else:
        result_path = result
    
    with open(result_path, "rb") as f:
        return f.read()

def generate_with_gemini(prompt: str) -> bytes:
    """Fallback function to generate an image using the free Gemini preview model."""
    global imagen_model
    
    # Lazy load and initialize on first call
    if imagen_model is None:
        print("--- First time initialization: Configuring Gemini for Image Generation ---")
        import google.generativeai as genai
        try:
            if gemma_model is None: # Configure if not already done
                GOOGLE_API_KEY = os.environ.get("GOOGLE_AI_API_KEY")
                if not GOOGLE_API_KEY:
                    raise ValueError("GOOGLE_AI_API_KEY is not set.")
                genai.configure(api_key=GOOGLE_API_KEY)
            
            imagen_model = genai.GenerativeModel('gemini-2.0-flash-preview-image-generation')
            print("--- Gemini (Imagen) configured successfully ---")
        except Exception as e:
            print(f"Error configuring Gemini for Image Generation: {e}")
            raise

    print("--- Attempting Image Generation with Gemini ---")
    
        # FIX: Request both IMAGE and TEXT as required by the model
    response = imagen_model.generate_content(
        contents={"parts": [{"text": prompt}]},
        generation_config={"response_modalities": ["IMAGE", "TEXT"]}
    )
    
    # Iterate through the response parts to find the one with image data
    for part in response.candidates[0].content.parts:
        if part.inline_data:
            print("Image data found in Gemini response.")
            return part.inline_data.data
            
    # If no image part is found after checking all parts, raise an error
    raise ValueError("No image data found in Gemini response parts.")

def generate_image(paragraph: str, style_guide: str = None) -> bytes:
    """
    Generates an image by trying the primary service first, then falling back to Gemini.
    """
    image_prompt = enhance_prompt_with_gemma(paragraph, style_guide=style_guide)
    
    try:
        image_bytes = generate_with_flux(image_prompt)
        print("Successfully generated image with FLUX.1.")
    except Exception as e:
        print(f"FLUX.1 generation failed: {e}. Switching to Gemini fallback.")
        try:
            image_bytes = generate_with_gemini(image_prompt)
            print("Successfully generated image with Gemini.")
        except Exception as e_alt:
            print(f"Gemini fallback generation also failed: {e_alt}")
            return None

    if not image_bytes:
        return None
    
    try:
        image = Image.open(io.BytesIO(image_bytes))
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()
    except Exception as e_proc:
        print(f"Failed to process the final image: {e_proc}")
        return None

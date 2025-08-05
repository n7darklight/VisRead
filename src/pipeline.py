# src/pipeline.py

import io
import os
import requests
from PIL import Image

# --- Globals to hold initialized clients ---
# We keep them in the global scope to reuse them after the first load.
flux_client = None
gemma_model = None
imagen_model = None

def enhance_prompt_with_gemma(paragraph: str) -> str:
    """
    Enhances a prompt using the Gemma model.
    It will only import and initialize the model on the first run.
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
            print(f"Error configuring Google AI: {e}")
            return paragraph # Return original paragraph if setup fails

    print("--- Enhancing Prompt with Gemma ---")
    try:
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
    """Fallback function to generate an image using Gemini (with lazy loading)."""
    global imagen_model
    
    # Lazy load and initialize on first call
    if imagen_model is None:
        print("--- First time initialization: Configuring Imagen ---")
        import google.generativeai as genai
        try:
            # Ensure Google AI is configured
            if not gemma_model: # If gemma hasn't been configured, do it now
                enhance_prompt_with_gemma("") # This will trigger configuration
            imagen_model = genai.GenerativeModel('gemini-2.0-flash-preview-image-generation')
            print("--- Imagen configured successfully ---")
        except Exception as e:
            print(f"Error configuring Imagen: {e}")
            raise

    print("--- Attempting Image Generation with Gemini ---")
    final_prompt = f"Generate an image of: {prompt}"
    response = imagen_model.generate_content(final_prompt)
    
    image_part = next((part for part in response.parts if part.file_data), None)
    if not image_part:
        raise Exception("No image data found in Gemini response.")
        
    image_url = image_part.file_data.file_uri
    image_response = requests.get(image_url)
    image_response.raise_for_status()
    return image_response.content

def generate_image(paragraph: str) -> bytes:
    """
    Generates an image by trying the primary service first, then falling back to Gemini.
    """
    image_prompt = enhance_prompt_with_gemma(paragraph)
    
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
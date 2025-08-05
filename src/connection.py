import os
from supabase import create_client, Client
import cloudinary
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# --- Supabase Setup ---
# Get Supabase credentials from environment variables.
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

# Create a Supabase client.
supabase: Client = create_client(url, key)

# --- Cloudinary Setup ---
# Get Cloudinary credentials from environment variables.
cloudinary.config( 
  cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME"), 
  api_key = os.environ.get("CLOUDINARY_API_KEY"), 
  api_secret = os.environ.get("CLOUDINARY_API_SECRET"),
  secure = True
)

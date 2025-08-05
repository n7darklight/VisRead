# VisRead - AI-Powered Visual Story Reader

VisRead is a desktop application that brings your stories to life by generating beautiful, AI-powered images for each paragraph. Paste in your text, and let VisRead create a unique visual experience that enhances your reading journey.

## Features

* **AI Image Generation**: Automatically generates a unique image for each paragraph of your story using a powerful AI model.
* **Intelligent Fallback System**: Prioritizes a primary image generation service and seamlessly switches to a free, high-volume alternative (Google's Gemini) if the first is unavailable.
* **User Authentication**: Secure login and registration system to keep your reading history private.
* **Reading History**: Access all your previously generated stories and view them anytime.
* **Light & Dark Modes**: A sleek, modern interface with theme switching available on every page.
* **Cross-Platform Desktop App**: Built with Flet to be packaged into a single executable for Windows, macOS, and Linux.

## Tech Stack

* **Framework**: [Flet](https://flet.dev/) - for the cross-platform desktop UI.
* **Language**: Python
* **Database**: [Supabase](https://supabase.io/) - for user authentication and story storage.
* **Image Hosting**: [Cloudinary](https://cloudinary.com/) - for storing and serving generated images.
* **AI Models**:
    * [FLUX.1-Krea-dev](https://huggingface.co/black-forest-labs/FLUX.1-Krea-dev) (Primary Image Generation)
    * [Google Gemini API](https://ai.google.dev/) (Fallback Image Generation & Prompt Enhancement)

## Getting Started

Follow these instructions to set up and run the project on your local machine for development and testing purposes.

### Prerequisites

* Python 3.10 or higher
* A Supabase account for the database.
* A Cloudinary account for image storage.
* A Google AI API key for Gemini.

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd VisRead
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your environment variables:**
    * Create a file named `.env` in the root directory of the project.
    * Copy the contents of `.env.example` (if provided) or add the following keys, replacing the placeholder values with your actual credentials:

    ```env
    # Supabase Credentials
    SUPABASE_URL=[https://your-project-ref.supabase.co](https://your-project-ref.supabase.co)
    SUPABASE_KEY=your-supabase-service-role-key

    # Google Generative AI Credentials
    GOOGLE_AI_API_KEY=your-google-ai-api-key

    # Cloudinary Credentials
    CLOUDINARY_CLOUD_NAME=your-cloudinary-cloud-name
    CLOUDINARY_API_KEY=your-cloudinary-api-key
    CLOUDINARY_API_SECRET=your-cloudinary-api-secret
    ```

5. **Set up the db scheme:**
   * Use db scheme for supabase like in db_scheme.sql

## Usage

### Running the Application Locally

To run the application in a development window, execute the `main.py` script:

```bash
python src/main.py
```
Building the Desktop Executable
To package the application into a standalone executable for your operating system (e.g., a .exe file on Windows), run the build.py script:

```bash

python build.py
```
The script will:

- Automatically detect your operating system (Windows, macOS, or Linux).

- Clean up any previous builds.

- Package the application and all its dependencies.

- Place the final executable inside a dist folder.

## Contributing
Contributions are welcome! If you have suggestions for improvements or want to fix a bug, please feel free to open an issue or submit a pull request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
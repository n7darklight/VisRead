# VisRead: Your Visual Reading Companion

VisRead is a Flet-based desktop application designed to enhance your reading experience by providing a visual and interactive way to consume text. It aims to make reading more engaging and accessible, especially for long-form content.

## Features

- **Clean and Distraction-Free Interface:** Focus on your content without unnecessary clutter.
- **Adjustable Text Presentation:** Customize font size, line spacing, and background color for optimal comfort.
- **Progress Tracking:** Visually see your reading progress within a document.
- **Interactive Elements (Planned):** Future updates will include features like highlighting, note-taking, and quick lookups.

## Getting Started

To get VisRead up and running on your machine, follow these steps:

### Prerequisites

- **Python 3.x:** Ensure you have Python 3 installed on your system.

### Installation and Running

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/your-username/visread.git
    cd visread
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Build the Application (Optional, for standalone executables):**
    You can build a standalone executable for your operating system. Replace `macos` with `windows` or `linux` as needed.
    ```bash
    flet build macos -v
    ```
    The built application will be located in the `build` directory.

4.  **Run the Application:**
    To run VisRead directly from the source code:
    ```bash
    flet run
   
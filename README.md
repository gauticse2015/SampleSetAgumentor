# Augmented Image Generation Application

A Flask-based web application designed to generate augmented variations of images for training computer vision models. This tool allows users to upload images, apply various augmentation techniques (rotation, flipping, noise, blur, grayscale), preview the results, and download the generated datasets.

## Features

- **Multi-Image Upload**: Support for uploading multiple images (PNG, JPG, JPEG, BMP).
- **Augmentation Techniques**:
    - **Rotation**: Generates versions rotated by 90°, 180°, and 270°.
    - **Flipping**: Generates horizontally and vertically flipped versions.
    - **Noise**: Adds Gaussian noise to images.
    - **Blur**: Applies blurring filters.
    - **Grayscale**: Converts images to grayscale.
- **Interactive Preview**: View generated images in a grid layout.
- **Selective Save**: Select specific augmented images to save to a user-specified output folder.
- **Responsive UI**: Built with Bootstrap 5 for a clean and modern interface.

## Project Structure

```
.
├── app/
│   ├── __init__.py         # Application factory
│   ├── config.py           # Configuration settings
│   ├── views.py            # Routes and view logic
│   ├── static/
│   │   └── css/
│   │       └── style.css   # Custom styling
│   ├── templates/
│   │   ├── base.html       # Base template with common layout
│   │   ├── index.html      # Upload and configuration page
│   │   └── results.html    # Results preview and download page
│   └── utils/
│       └── augmentor.py    # Image processing logic
├── generated/              # Directory for storing generated images
├── uploads/                # Temporary directory for uploaded files
├── run.py                  # Entry point script
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

## Setup and Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Install dependencies**:
    Ensure you have Python 3.x installed.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Prepare NLTK Data (Offline Usage)**:
    The application uses NLTK for synonym replacement. For offline environments (like Docker containers), you must download the data during the build process.
    
    Run this command to download the required corpora to the `nltk_data` directory within the project:
    ```bash
    python -m nltk.downloader -d nltk_data wordnet omw-1.4
    ```
    
    **For Dockerfile:**
    Add the following lines to your `Dockerfile` after installing requirements:
    ```dockerfile
    # Download NLTK data to project directory
    RUN python -m nltk.downloader -d /app/nltk_data wordnet omw-1.4
    ```

4.  **Run the application**:
    ```bash
    python run.py
    ```

5.  **Access the application**:
    Open your web browser and navigate to `http://localhost:5000`.

## Usage Guide

1.  **Upload Images**: On the home page, click "Choose Files" to select one or more images from your computer.
2.  **Select Augmentations**: Check the boxes for the augmentation types you want to apply (Rotate, Flip, Noise, etc.).
3.  **Generate**: Click "Generate Augmented Images".
4.  **Preview**: The application will process the images and display the results on the next page.
5.  **Save to Folder**: Enter the desired output folder path (absolute or relative), select the images you wish to keep, and click the "Save Selected to Folder" button. The images will be saved directly to the specified location.

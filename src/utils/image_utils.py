from PIL import Image
import os
from threading import Thread
from ..utils.logger import logger

def analyze_image(image_path):
    # Placeholder for image analysis logic
    # For example, you could use an image recognition API or a pre-trained model
    return f"Analysis of {os.path.basename(image_path)}"

def view_images_in_folder(folder_path, analyze=False):
    def display_image(image_path):
        try:
            image = Image.open(image_path)
            image.show()
            if analyze:
                analysis = analyze_image(image_path)
                logger.info(analysis)
                return analysis
        except Exception as e:
            logger.error(f"An error occurred while displaying image {image_path}: {e}")
            return None

    try:
        image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'bmp'))]
        if not image_files:
            logger.info("No images found in the specified folder.")
            return []

        analyses = []
        for image_file in image_files:
            image_path = os.path.join(folder_path, image_file)
            logger.info(f"Displaying image: {image_path}")
            thread = Thread(target=display_image, args=(image_path,))
            thread.start()
            thread.join()  # Wait for the thread to finish to get the analysis
            if analyze:
                analysis = display_image(image_path)
                if analysis:
                    analyses.append(analysis)

        return analyses

    except Exception as e:
        logger.error(f"An error occurred while viewing images: {e}")
        return []
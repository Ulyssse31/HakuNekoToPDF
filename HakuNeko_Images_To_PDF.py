"""
    Code created by Ulysse31
"""

import os
from PIL import Image, ImageFile
import PyPDF2
import re
import shutil  # Import shutil for moving files

# Handle truncated images by allowing them to load partially
ImageFile.LOAD_TRUNCATED_IMAGES = True

def natural_sort_key(s):
    # Helper function to turn text into a list of strings and numbers
    return [float(text) if text.isdigit() else text for text in re.split('([0-9]+?[0-9]*)', s)]

def create_pdf_from_images(folder_path):
    pdf_files = []

    # Get sorted list of directories by numerical order if applicable
    chapters = sorted(os.listdir(folder_path), key=natural_sort_key)

    for chapter in chapters:
        chapter_path = os.path.join(folder_path, chapter)
        if os.path.isdir(chapter_path):
            # Collect all image files in the chapter directory, sorted by name
            images = [os.path.join(chapter_path, img) for img in sorted(os.listdir(chapter_path), key=natural_sort_key) if img.lower().endswith(('.png', '.jpg', '.jpeg'))]
            if not images:
                continue  # Skip chapters with no images

            image_list = []
            for img in images:
                try:
                    # Attempt to open and convert each image to RGB
                    loaded_image = Image.open(img).convert('RGB')
                    image_list.append(loaded_image)
                except (IOError, OSError) as e:
                    print(f"Warning: Could not process image {img}: {e}")

            if not image_list:
                print(f"No valid images found in {chapter}. Skipping...")
                continue

            # Check if chapter is a whole number and modify it if so
            modified_chapter = f"{chapter}.0" if chapter.isdigit() else chapter

            # Define the PDF path with the modified chapter name
            pdf_path = os.path.join(folder_path, f"{modified_chapter}.pdf")
            pdf_files.append(pdf_path)

            # Save the images as a PDF file
            image_list[0].save(pdf_path, save_all=True, append_images=image_list[1:])
            print(f"Created PDF for {modified_chapter} at {pdf_path}")
    
    # Merge all PDF files into one and then move it to the parent directory
    merge_pdfs(folder_path, pdf_files)

def merge_pdfs(folder_path, pdf_files):
    merger = PyPDF2.PdfMerger()
    
    for pdf_file in sorted(pdf_files, key=natural_sort_key):
        merger.append(pdf_file)
    
    # Name the final PDF after the folder name
    final_pdf_name = os.path.basename(folder_path) + ".pdf"
    final_pdf_path = os.path.join(folder_path, final_pdf_name)
    merger.write(final_pdf_path)
    merger.close()
    print(f"All chapters have been merged into {final_pdf_path}")

    # Move the final PDF to the parent directory
    parent_folder = os.path.dirname(folder_path)
    final_destination = os.path.join(parent_folder, final_pdf_name)
    shutil.move(final_pdf_path, final_destination)
    print(f"Moved final PDF to {final_destination}")

if __name__ == "__main__":
    base_folder = input("Enter the name of the base directory containing the chapter folders: ")
    create_pdf_from_images(base_folder)

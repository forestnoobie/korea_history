import pytesseract
from PIL import Image
import os
import urllib.request
import ssl
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import fitz  # PyMuPDF

def pdf_to_images(pdf_path, output_dir=None, dpi=300):
    """
    Convert PDF pages to PNG images
    
    Args:
        pdf_path (str): Path to the PDF file
        output_dir (str, optional): Directory to save PNG files. If None, uses same directory as PDF
        dpi (int, optional): DPI for the output images. Higher DPI = better quality but larger files
    
    Returns:
        list: Paths to the generated PNG files
    """
    # If no output directory specified, use the PDF's directory
    if output_dir is None:
        output_dir = os.path.dirname(pdf_path)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get the PDF filename without extension
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    
    # Open the PDF
    pdf_document = fitz.open(pdf_path)
    generated_images = []

    # Calculate the zoom factor based on DPI (default PDF DPI is 72)
    zoom = dpi / 72

    # Iterate through each page
    for page_number in range(pdf_document.page_count):
        # Get the page
        page = pdf_document[page_number]
        
        # Create a matrix for rendering with the zoom factor
        mat = fitz.Matrix(zoom, zoom)
        
        # Get the pixmap (rendered page)
        pix = page.get_pixmap(matrix=mat)
        
        # Generate output path for this page
        output_path = os.path.join(output_dir, f"{pdf_name}_page_{page_number + 1}.png")
        
        # Save the image
        pix.save(output_path)
        generated_images.append(output_path)
    
    pdf_document.close()
    return generated_images

# Create tessdata directory in the current folder if it doesn't exist
tessdata_dir = os.path.join(os.path.dirname(__file__), "tessdata")
os.makedirs(tessdata_dir, exist_ok=True)

# Download Korean language data if not exists
kor_traineddata = os.path.join(tessdata_dir, "kor.traineddata")
if not os.path.exists(kor_traineddata):
    print("Downloading Korean language data...")
    # Disable SSL verification for the download
    ssl._create_default_https_context = ssl._create_unverified_context
    url = "https://github.com/tesseract-ocr/tessdata/raw/main/kor.traineddata"
    urllib.request.urlretrieve(url, kor_traineddata)
    print("Download complete!")

# Set the TESSDATA_PREFIX environment variable to our local tessdata directory
os.environ['TESSDATA_PREFIX'] = tessdata_dir

# Open the image file
image = Image.open("../temp/output_images/74_workbook_page_1.png")

# Perform OCR with Korean language support and get bounding boxes
custom_config = r'--oem 3 --psm 6 -l kor'  # Use Korean language pack
data = pytesseract.image_to_data(image, config=custom_config, output_type=pytesseract.Output.DATAFRAME)

# Filter out empty text and low confidence results
data = data[data.conf != -1]  # Remove rows with confidence -1
data = data.dropna(subset=['text'])  # Remove rows with empty text
data = data[data['text'].str.strip() != '']  # Remove rows with only whitespace
data = data[data['text'].str.contains(r'[\?\[\]]', regex=True)]  # text containing ? or [

# Save both text and bounding box information
with open("output.txt", "w", encoding="utf-8") as out:
    # Write the full text first
    full_text = ' '.join(data['text'].tolist())
    out.write("Full Text:\n")
    out.write(full_text)
    out.write("\n\nDetailed Information (Text with Bounding Boxes):\n")
    
    # Write detailed information for each text block
    for index, row in data.iterrows():
        text_info = f"Text: {row['text']}\n"
        text_info += f"Bounding Box: x={row['left']}, y={row['top']}, width={row['width']}, height={row['height']}\n"
        text_info += f"Confidence: {row['conf']}%\n"
        text_info += "-" * 50 + "\n"
        out.write(text_info)
        print(text_info)

# Save the detailed data to CSV for further analysis if needed
data.to_csv("ocr_results.csv", index=False, encoding="utf-8")

# Plot the image with bounding boxes
plt.figure(figsize=(15,15))
plt.imshow(image)

# Draw rectangles for each detected text area
for index, row in data.iterrows():
    x, y = row['left'], row['top']
    w, h = row['width'], row['height']
    
    # Create a Rectangle patch
    rect = patches.Rectangle((x,y), w, h, linewidth=2, edgecolor='r', facecolor='none')
    
    # Add the rectangle to the plot
    plt.gca().add_patch(rect)
    
    # Add text annotation
    plt.text(x, y-5, row['text'] + "+ " + str(round(row['conf'], 2)), color='red', fontsize=8)

import pdb; pdb.set_trace() 
# No.1 x : left, y : top
x,y = 10, 640
w,h = 1500, 1900  # h = top - prev_top
text = "No.1"

# Create a Rectangle patch
rect = patches.Rectangle((x,y), w, h, linewidth=2, edgecolor='b', facecolor='none')

# Add the rectangle to the plot
plt.gca().add_patch(rect)

# Add text annotation
plt.text(x, y-5, "No.1", color='red', fontsize=8)


# No.1 x : left, y : top
x,y = 10, 2540
w,h = 1500, 1500  # h = top - prev_top
text = "No.2"

# Create a Rectangle patch
rect = patches.Rectangle((x,y), w, h, linewidth=2, edgecolor='g', facecolor='none')

# Add the rectangle to the plot
plt.gca().add_patch(rect)

# Add text annotation
plt.text(x, y-5, "No.2", color='red', fontsize=8)



plt.axis('off')
plt.savefig('output_with_boxes.png', bbox_inches='tight', dpi=300)
plt.close()




# if __name__ == "__main__":
#     # Example usage for PDF processing
#     pdf_path = "../data/74_workbook.pdf"  # Replace with your PDF path
#     output_dir = "output_images"
    
#     # Convert PDF to images
#     image_paths = pdf_to_images(pdf_path, output_dir, dpi=300)
#     print(f"Generated {len(image_paths)} images from PDF:")
#     for path in image_paths:
#         print(f"- {path}")

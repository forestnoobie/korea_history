# Standard library imports
import os
import fitz
import matplotlib.pyplot as plt
import matplotlib.patches as patches




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

def draw_rect(x,y,w,h,text,color):
    # Convert color to string with 'C' prefix for matplotlib color cycle
    if isinstance(color, (int, float)):
        color = f'C{int(color)}'
    
    rect = patches.Rectangle((x,y), w, h, linewidth=2, edgecolor=color, facecolor='none')
    plt.gca().add_patch(rect)
    plt.text(x, y-5, text, color=color, fontsize=8)

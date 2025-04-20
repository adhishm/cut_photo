from PIL import Image, ImageDraw
import glob
import os
import math
    
def check_image_sizes(
        file_pattern: str
) -> bool:
    # Find all files matching the pattern
    files = glob.glob(file_pattern)
    if not files:
        print("No files found matching the pattern.")
        return False

    # Get the aspect ratio of the first image
    with Image.open(files[0]) as img:
        width, height = img.size
        aspect_ratio = width / height

    # Check if all other images have the same aspect ratio
    for file in files[1:]:
        with Image.open(file) as img:
            width, height = img.size
            if width / height != aspect_ratio:
                print(f"Image {file} has a different aspect ratio.")
                return False

    return True


# Define paper sizes in mm
PAPER_SIZES = {
    'a4': (210, 297),
    'a3': (297, 420),
    'a2': (420, 594)
}

def create_printable_images(
        file_pattern: str,
        paper_size: str,
        image_size_mm: int,
        size_type: str = 'height',
        spacing_mm: int = 5,
        output_dir: str = './print_ready/'
):
    if paper_size not in PAPER_SIZES:
        raise ValueError(f"Invalid paper size '{paper_size}'. Choose from {list(PAPER_SIZES.keys())}.")

    # Get paper dimensions in pixels (assuming 300 DPI)
    dpi = 300
    mm_to_pixels = lambda mm: int(mm * dpi / 25.4)
    paper_width_px, paper_height_px = map(mm_to_pixels, PAPER_SIZES[paper_size])
    spacing_px = mm_to_pixels(spacing_mm)

    # Find all files matching the pattern
    files = glob.glob(file_pattern)
    if not files:
        print("No files found matching the pattern.")
        return

    # Resize images and calculate grid layout
    resized_images = []
    for file in files:
        with Image.open(file) as img:
            width, height = img.size
            aspect_ratio = width / height

            # Calculate new dimensions based on the size type
            if size_type == 'height':
                new_height_px = mm_to_pixels(image_size_mm)
                new_width_px = int(new_height_px * aspect_ratio)
            elif size_type == 'width':
                new_width_px = mm_to_pixels(image_size_mm)
                new_height_px = int(new_width_px / aspect_ratio)
            else:
                raise ValueError("Invalid size type. Choose 'height' or 'width'.")

            # Resize the image
            resized_img = img.resize((new_width_px, new_height_px))
            resized_images.append(resized_img)

    # Calculate grid dimensions
    max_cols = paper_width_px // (resized_images[0].width + spacing_px)
    max_rows = paper_height_px // (resized_images[0].height + spacing_px)
    max_images_per_page = max_cols * max_rows

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Generate pages
    for page_num in range(math.ceil(len(resized_images) / max_images_per_page)):
        # Create a blank canvas for the current page
        canvas = Image.new("RGB", (paper_width_px, paper_height_px), "white")
        draw = ImageDraw.Draw(canvas)

        # Arrange images on the canvas
        x_offset, y_offset = spacing_px, spacing_px
        start_index = page_num * max_images_per_page
        end_index = min(start_index + max_images_per_page, len(resized_images))
        for img in resized_images[start_index:end_index]:
            canvas.paste(img, (x_offset, y_offset))
            x_offset += img.width + spacing_px

            # Move to the next row if the current row is full
            if x_offset + img.width > paper_width_px:
                x_offset = spacing_px
                y_offset += img.height + spacing_px

            # Stop if the canvas is full
            if y_offset + img.height > paper_height_px:
                break

        # Save the current page
        output_path = os.path.join(output_dir, f"printable_page_{page_num + 1}.jpg")
        canvas.save(output_path, "JPEG")
        print(f"Page {page_num + 1} saved to {output_path}")

    print("All pages created.")

from PIL import Image
import io


def generate_gradient_bitmap(width: int = 600, height: int = 448) -> bytes:
    """Generate a gradient bitmap pattern using Pillow with proper 1-bit BMP formatting."""
    image = Image.new('1', (width, height), 0)
    
    for x in range(width):
        for y in range(height):
            gradient_pos = x / width
            pattern = (x + y) % 4
            threshold = gradient_pos + (pattern * 0.1)
            
            if threshold < 0.5:
                image.putpixel((x, y), 1)
    
    buffer = io.BytesIO()
    image.save(buffer, format='BMP', bits=1)
    
    return buffer.getvalue()

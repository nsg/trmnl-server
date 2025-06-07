import struct
from datetime import datetime


def generate_monochrome_bmp(width: int = 800, height: int = 480) -> bytes:
    """Generate a monochrome BMP file with dynamic content."""
    
    # Calculate row size (must be multiple of 4 bytes)
    bits_per_pixel = 1
    row_size = ((width * bits_per_pixel + 31) // 32) * 4
    
    # BMP file structure
    file_header_size = 14
    info_header_size = 40
    color_table_size = 8  # 2 colors * 4 bytes each
    pixel_data_size = row_size * height
    file_size = file_header_size + info_header_size + color_table_size + pixel_data_size
    
    # Create BMP file header
    bmp_data = bytearray()
    
    # File header (14 bytes)
    bmp_data.extend(b'BM')  # Signature
    bmp_data.extend(struct.pack('<I', file_size))  # File size
    bmp_data.extend(struct.pack('<HH', 0, 0))  # Reserved
    bmp_data.extend(struct.pack('<I', file_header_size + info_header_size + color_table_size))  # Offset to pixel data
    
    # Info header (40 bytes)
    bmp_data.extend(struct.pack('<I', info_header_size))  # Header size
    bmp_data.extend(struct.pack('<I', width))  # Width
    bmp_data.extend(struct.pack('<I', height))  # Height
    bmp_data.extend(struct.pack('<H', 1))  # Planes
    bmp_data.extend(struct.pack('<H', bits_per_pixel))  # Bits per pixel
    bmp_data.extend(struct.pack('<I', 0))  # Compression
    bmp_data.extend(struct.pack('<I', pixel_data_size))  # Image size
    bmp_data.extend(struct.pack('<I', 2835))  # X pixels per meter
    bmp_data.extend(struct.pack('<I', 2835))  # Y pixels per meter
    bmp_data.extend(struct.pack('<I', 2))  # Colors used
    bmp_data.extend(struct.pack('<I', 2))  # Important colors
    
    # Color table (8 bytes) - black and white
    bmp_data.extend(b'\x00\x00\x00\x00')  # Black
    bmp_data.extend(b'\xFF\xFF\xFF\x00')  # White
    
    # Generate pixel data
    current_time = datetime.now()
    
    for y in range(height):
        row_data = bytearray(row_size)
        for x in range(0, width, 8):  # Process 8 pixels at a time (1 byte)
            byte_val = 0
            for bit in range(8):
                if x + bit < width:
                    pixel_x = x + bit
                    pixel_y = height - 1 - y  # BMP is bottom-up
                    
                    is_white = _get_pixel_value(pixel_x, pixel_y, width, height, current_time)
                    
                    if is_white:
                        byte_val |= (1 << (7 - bit))
            
            row_data[x // 8] = byte_val
        
        bmp_data.extend(row_data)
    
    return bytes(bmp_data)


def _get_pixel_value(pixel_x: int, pixel_y: int, width: int, height: int, current_time: datetime) -> bool:
    """Determine if a pixel should be white (True) or black (False)."""
    
    # Border
    if pixel_x < 10 or pixel_x >= width - 10 or pixel_y < 10 or pixel_y >= height - 10:
        return True
    
    # Title area
    elif 50 <= pixel_y < 100 and 50 <= pixel_x < 750:
        # Simple text pattern for "TRMNL Server"
        if (pixel_x // 10 + pixel_y // 10) % 2 == 0:
            return True
    
    # Time display area
    elif 150 <= pixel_y < 200 and 100 <= pixel_x < 700:
        # Pattern based on current time
        if (pixel_x + current_time.second) % 20 < 10:
            return True
    
    # Status area
    elif 250 <= pixel_y < 300 and 100 <= pixel_x < 700:
        # Simple status pattern
        if pixel_x % 50 < 25:
            return True
    
    return False


def generate_setup_cube_bmp(width: int = 800, height: int = 480) -> bytes:
    """Generate a monochrome BMP file with a centered cube."""
    
    bits_per_pixel = 1
    row_size = ((width * bits_per_pixel + 31) // 32) * 4
    
    file_header_size = 14
    info_header_size = 40
    color_table_size = 8 
    pixel_data_size = row_size * height
    file_size = file_header_size + info_header_size + color_table_size + pixel_data_size
    
    bmp_data = bytearray()
    
    # File header
    bmp_data.extend(b'BM')
    bmp_data.extend(struct.pack('<I', file_size))
    bmp_data.extend(struct.pack('<HH', 0, 0))
    bmp_data.extend(struct.pack('<I', file_header_size + info_header_size + color_table_size))
    
    # Info header
    bmp_data.extend(struct.pack('<I', info_header_size))
    bmp_data.extend(struct.pack('<I', width))
    bmp_data.extend(struct.pack('<I', height))
    bmp_data.extend(struct.pack('<H', 1))
    bmp_data.extend(struct.pack('<H', bits_per_pixel))
    bmp_data.extend(struct.pack('<I', 0))
    bmp_data.extend(struct.pack('<I', pixel_data_size))
    bmp_data.extend(struct.pack('<I', 2835)) # X pixels per meter (72 DPI)
    bmp_data.extend(struct.pack('<I', 2835)) # Y pixels per meter (72 DPI)
    bmp_data.extend(struct.pack('<I', 2))    # Colors used
    bmp_data.extend(struct.pack('<I', 2))    # Important colors
    
    # Color table (black and white)
    bmp_data.extend(b'\x00\x00\x00\x00')  # Black
    bmp_data.extend(b'\xFF\xFF\xFF\x00')  # White
    
    # Pixel data generation for the cube
    cube_w = width // 4
    cube_h = height // 4
    cube_x_start = (width - cube_w) // 2
    cube_x_end = cube_x_start + cube_w
    # Image coordinates for cube (top-down)
    cube_y_start_img = (height - cube_h) // 2 
    cube_y_end_img = cube_y_start_img + cube_h

    for y_bmp in range(height):  # BMP rows are bottom-up
        row_data_bytes = bytearray(row_size)
        img_y = height - 1 - y_bmp  # Current image row (top-down)
        
        for x_pixel_start in range(0, width, 8): # Process 8 pixels (1 byte)
            byte_val = 0
            for bit_in_byte in range(8):
                img_x = x_pixel_start + bit_in_byte
                
                if img_x < width:
                    # Default to white background (pixel bit = 1)
                    is_pixel_white = True
                    
                    # Check if pixel is within the cube (black, pixel bit = 0)
                    if cube_x_start <= img_x < cube_x_end and \
                       cube_y_start_img <= img_y < cube_y_end_img:
                        is_pixel_white = False 
                    
                    if is_pixel_white:
                        byte_val |= (1 << (7 - bit_in_byte))
            
            row_data_bytes[x_pixel_start // 8] = byte_val
        bmp_data.extend(row_data_bytes)
        
    return bytes(bmp_data)

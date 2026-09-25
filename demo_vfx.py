from PIL import Image, ImageDraw, ImageFont

# Create a 400x400 dark navy image
img = Image.new("RGB", (400, 400), color=(10, 20, 60))  # dark navy

draw = ImageDraw.Draw(img)

# Text to render
text = "VELTRA AI ACTIVE"

# Try to load a larger font; fall back to default if unavailable
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
except Exception:
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

# Compute text bbox for centering
if font is not None:
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
    except Exception:
        text_w, text_h = 0, 0
    if text_w <= 0 or text_h <= 0:
        text_w, text_h = draw.textsize(text, font=font)

    x = (400 - text_w) // 2
    y = (400 - text_h) // 2

    draw.text((x, y), text, fill="white", font=font)
else:
    # absolute fallback using textsize
    text_w, text_h = draw.textsize(text)
    x = (400 - text_w) // 2
    y = (400 - text_h) // 2
    draw.text((x, y), text, fill="white")

# Save as PNG
img.save("vfx_demo.png", "PNG")
print("vfx_demo.png created")

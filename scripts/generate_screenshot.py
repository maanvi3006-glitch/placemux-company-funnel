from PIL import Image, ImageDraw, ImageFont
import os
out = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dashboard', 'screenshots', 'dashboard_preview.png')
os.makedirs(os.path.dirname(out), exist_ok=True)
img = Image.new('RGB', (1200, 700), color=(255,255,255))
d = ImageDraw.Draw(img)
try:
    f = ImageFont.truetype('arial.ttf', 36)
except:
    f = ImageFont.load_default()
d.text((50,50), 'PlaceMux Dashboard Preview', fill=(0,0,0), font=f)
d.text((50,120), 'Open http://localhost:8501 to view the live dashboard', fill=(80,80,80), font=f)
img.save(out)
print('Wrote', out)

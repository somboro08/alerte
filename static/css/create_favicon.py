# create_favicon.py
from PIL import Image, ImageDraw

# Créer une image 64x64
img = Image.new('RGB', (64, 64), color='#2563eb')
draw = ImageDraw.Draw(img)

# Dessiner un symbole de main
draw.ellipse([16, 16, 48, 48], fill='white')
draw.ellipse([20, 20, 44, 44], fill='#2563eb')

# Sauvegarder
img.save('static/images/favicon.ico', format='ICO')

print("Favicon créé avec succès !")
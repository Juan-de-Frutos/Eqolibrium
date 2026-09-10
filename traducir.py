from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import os
import shutil
import time # Añadimos time para poder hacer pausas

# 1. Crear carpeta de salida
os.makedirs('output', exist_ok=True)

# 2. Leer tu archivo HTML (asegúrate de que el nombre coincide exactamente)
nombre_archivo = 'Eqolibrium.html' # Cambia esto si tu archivo se llama distinto

with open(nombre_archivo, 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')

# 3. Traducir los textos con pausas antibloqueo
translator = GoogleTranslator(source='es', target='en')
etiquetas_a_traducir = soup.find_all(['p', 'h1', 'h2', 'h3', 'span', 'li'])

for tag in etiquetas_a_traducir:
    if tag.string and tag.string.strip():
        texto_original = tag.string.strip()
        try:
            texto_traducido = translator.translate(texto_original)
            tag.string.replace_with(texto_traducido)
            # Pausa de 1 segundo para que Google no nos bloquee
            time.sleep(1)
        except Exception as e:
            print(f"⚠️ Aviso: No se pudo traducir: '{texto_original}'.")

# 4. Guardar el HTML traducido
with open(f'output/{nombre_archivo}', 'w', encoding='utf-8') as f:
    f.write(str(soup))
    
# 5. Copiar la carpeta de imágenes (cambia 'images' si tu carpeta se llama distinto)
if os.path.exists('images'):
    shutil.copytree('images', 'output/images', dirs_exist_ok=True)

print("¡Traducción completada con éxito!")

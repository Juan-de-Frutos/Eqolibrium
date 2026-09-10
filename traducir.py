from bs4 import BeautifulSoup
from deep_translator import MyMemoryTranslator
import os
import shutil
import time

os.makedirs('output', exist_ok=True)

nombre_archivo = 'index.html' 

with open(nombre_archivo, 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')

translator = MyMemoryTranslator(source='es', target='en')
etiquetas_a_traducir = soup.find_all(['p', 'h1', 'h2', 'h3', 'span', 'li'])

for tag in etiquetas_a_traducir:
    if tag.string and tag.string.strip():
        texto_original = tag.string.strip()
        try:
            texto_traducido = translator.translate(texto_original)
            tag.string.replace_with(texto_traducido)
            time.sleep(1)
        except Exception as e:
            print(f"Aviso: No se pudo traducir: '{texto_original}'.")

with open(f'output/{nombre_archivo}', 'w', encoding='utf-8') as f:
    f.write(str(soup))

if os.path.exists('images'):
    shutil.copytree('images', 'output/images', dirs_exist_ok=True)

if os.path.exists('assets'):
    shutil.copytree('assets', 'output/assets', dirs_exist_ok=True)

print("¡Traducción completada con éxito!")

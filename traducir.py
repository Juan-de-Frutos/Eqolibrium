from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import os
import shutil

os.makedirs('output', exist_ok=True)

#BeautifulSoup librería para no cargarse el formato HTML de la web original
with open('index.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')

#Uso el traductor de Google para la prueba de concepto
translator = GoogleTranslator(source='es', target='en')
etiquetas_a_traducir = soup.find_all(['p', 'h1', 'h2', 'h3', 'span', 'li'])

for tag in etiquetas_a_traducir:
    if tag.string and tag.string.strip():
        texto_original = tag.string.strip()
        try:
            # Intentamos traducir
            texto_traducido = translator.translate(texto_original)
            tag.string.replace_with(texto_traducido)
        except Exception as e:
            # Si falla, avisamos pero NO detenemos el programa
            print(f"AVISO: Saltando frase problemática: '{texto_original}'.")

for tag in etiquetas_a_traducir:
    if tag.string and tag.string.strip(): # Solo traducir si hay texto
        texto_traducido = translator.translate(tag.string.strip())
        tag.string.replace_with(texto_traducido)

with open('output/index.html', 'w', encoding='utf-8') as f:
    f.write(str(soup))
    
if os.path.exists('images'): # Cambia 'images' por el nombre real de tu carpeta
    shutil.copytree('images', 'output/images', dirs_exist_ok=True)

print("Traducción completada y archivos preparados en la carpeta 'output'.")

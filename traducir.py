#!/usr/bin/env python3
"""
Traduce automáticamente los ficheros .html del repositorio (ES -> EN)
y deja el resultado en la carpeta 'output', listo para publicarse.

Ideas clave:
  * Se recorren los NODOS DE TEXTO, no las etiquetas. Así se traduce
    también el texto que convive con <strong>, <a>, <br>, <font>...
  * Caché en disco: las cadenas repetidas ("Fundamental", "Continuar",
    las opciones de los <select>...) se traducen una sola vez.
  * Motor principal Google (sin clave); si falla, cae a MyMemory.
  * Los errores se imprimen con su causa y se resumen al final.

Uso local:   python traducir.py
Prueba sin red (solo comprueba el recorrido del HTML):
             TRADUCTOR_OFFLINE=1 python traducir.py
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

from bs4 import BeautifulSoup, Comment, Doctype, NavigableString
from deep_translator import GoogleTranslator, MyMemoryTranslator

# --------------------------------------------------------------------------
# Configuración
# --------------------------------------------------------------------------

RAIZ = Path(".")
SALIDA = Path("output")
CACHE_PATH = Path(".cache_traduccion.json")

IDIOMA_ORIGEN = "es"
IDIOMA_DESTINO = "en"

CARPETAS_A_COPIAR = ("images", "assets")
DIRECTORIOS_IGNORADOS = {"output", ".git", ".github", "node_modules", "__pycache__"}

# Contenido que no es texto visible para el usuario
PADRES_IGNORADOS = {"script", "style", "code", "pre", "kbd", "samp"}

# Atributos visibles que también conviene traducir
ATRIBUTOS_TRADUCIBLES = ("placeholder", "alt", "title", "aria-label")

INTENTOS_POR_MOTOR = 3
PAUSA_ENTRE_LLAMADAS = 0.4   # segundos, para no saturar el servicio
ESPERA_BASE_REINTENTO = 2.0

OFFLINE = os.environ.get("TRADUCTOR_OFFLINE") == "1"

# Cadenas que deben quedarse tal cual (marca, nombres propios, correos...)
# La comparación es en minúsculas y sobre el texto ya recortado.
NO_TRADUCIR = {
    "eqolibrium",
    "olibrium",
    "gigas for schools",
    "colegio san josé",
    "team seas",
    "national geographic",
    "gmail: eqolibriumvall@gmail.com",
    "twitter",
    "facebook",
    "instagram",
    "youtube",
    "a+++", "a++", "a+", "a", "b", "c", "d",
}

# Traducciones fijadas a mano. Son imprescindibles cuando una frase está
# partida por etiquetas: el <font color="lime"> del eslogan hace que el
# traductor reciba trozos sueltos ("La mano amiga del e" / "c" / "ologismo")
# y devuelva basura. Aquí se controla el resultado y se conserva el juego
# visual de la letra verde: The friendly hand of e[c]ologism.
TRADUCCIONES_MANUALES = {
    "La mano amiga del e": "The friendly hand of e",
    "ologismo": "ologism",
    "OLIBRIUM": "OLIBRIUM",
    "Piensa globalmente, actúa localmente": "Think globally, act locally",
    "CLICA AQUÍ": "CLICK HERE",
    "Continuar": "Continue",
    "Volver": "Back",
    "Mandar": "Send",
    "Resetear": "Reset",
    "Ver Resultados": "See results",
    "Iniciar Sesión": "Log in",
    "Registrase": "Sign up",
    "Fundamental": "Essential",
    "PUEDES DONAR AQUÍ": "YOU CAN DONATE HERE",
    "Regístrate aquí": "Sign up here",
    "Nombre": "Name",
    "Correo Electrónico": "Email address",
    "Mensaje": "Message",
    "Contraseña": "Password",
    "Confirmar contraseña": "Confirm password",
    "Nombre de Usuario": "Username",
}

TIENE_LETRAS = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]")


# --------------------------------------------------------------------------
# Traductor con caché, reintentos y motor de reserva
# --------------------------------------------------------------------------

class Traductor:
    def __init__(self) -> None:
        self.motores = [
            ("google", lambda: GoogleTranslator(source=IDIOMA_ORIGEN, target=IDIOMA_DESTINO)),
            ("mymemory", lambda: MyMemoryTranslator(source="es-ES", target="en-GB")),
        ]
        self.indice = 0
        self.nombre, constructor = self.motores[0]
        self.motor = None if OFFLINE else constructor()
        self.cache: dict[str, str] = self._cargar_cache()
        self.fallos: list[str] = []
        self.llamadas = 0

    # -- caché -------------------------------------------------------------
    @staticmethod
    def _cargar_cache() -> dict[str, str]:
        if CACHE_PATH.exists():
            try:
                return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                print("Aviso: caché corrupta, se empieza de cero.")
        return {}

    def guardar_cache(self) -> None:
        CACHE_PATH.write_text(
            json.dumps(self.cache, ensure_ascii=False, indent=1, sort_keys=True),
            encoding="utf-8",
        )

    # -- motores -----------------------------------------------------------
    def _cambiar_de_motor(self) -> bool:
        if self.indice + 1 >= len(self.motores):
            return False
        self.indice += 1
        self.nombre, constructor = self.motores[self.indice]
        self.motor = constructor()
        print(f"  -> cambiando al motor de reserva: {self.nombre}")
        return True

    # -- API pública -------------------------------------------------------
    def traducir(self, texto: str) -> str:
        if texto in TRADUCCIONES_MANUALES:
            return TRADUCCIONES_MANUALES[texto]
        if texto.lower() in NO_TRADUCIR:
            return texto
        if texto in self.cache:
            return self.cache[texto]
        if OFFLINE:
            return f"[EN] {texto}"

        while True:
            for intento in range(1, INTENTOS_POR_MOTOR + 1):
                error: Exception | None = None
                try:
                    resultado = self.motor.translate(texto)
                except Exception as exc:          # noqa: BLE001 - queremos la causa
                    error = exc
                else:
                    if resultado and resultado.strip():
                        self.llamadas += 1
                        self.cache[texto] = resultado
                        time.sleep(PAUSA_ENTRE_LLAMADAS)
                        return resultado
                    error = ValueError("el servicio devolvió una cadena vacía")

                print(f"  [{self.nombre}] intento {intento}/{INTENTOS_POR_MOTOR} "
                      f"falló con «{texto[:60]}»: {error}")
                time.sleep(ESPERA_BASE_REINTENTO * intento)

            if not self._cambiar_de_motor():
                self.fallos.append(texto)
                return texto  # se deja el original antes que romper la web


# --------------------------------------------------------------------------
# Recorrido del HTML
# --------------------------------------------------------------------------

def nodos_de_texto(soup: BeautifulSoup):
    """Todos los nodos de texto visibles del documento."""
    for nodo in soup.find_all(string=True):
        if isinstance(nodo, (Comment, Doctype)):
            continue
        padre = nodo.parent
        if padre is not None and padre.name in PADRES_IGNORADOS:
            continue
        yield nodo


def merece_traduccion(texto: str) -> bool:
    if len(texto) < 2:
        return False
    if not TIENE_LETRAS.search(texto):
        return False
    if texto.lower() in NO_TRADUCIR:
        return False
    return True


def traducir_documento(ruta: Path, traductor: Traductor) -> str:
    bruto = ruta.read_text(encoding="utf-8")

    # El HTML original escribe «&nbsp» sin punto y coma. Si no se arregla
    # antes de parsear, BeautifulSoup lo reserializa como «&amp;nbsp» y
    # aparece literalmente en la web traducida.
    bruto = re.sub(r"&nbsp(?!;)", "&nbsp;", bruto)

    # Algunas versiones de bs4 tratan «<br>» como etiqueta con apertura y
    # cierre y ensucian la salida con «</br>».
    bruto = re.sub(r"<br\s*>", "<br/>", bruto, flags=re.IGNORECASE)

    soup = BeautifulSoup(bruto, "html.parser")

    # 1) Texto visible
    for nodo in list(nodos_de_texto(soup)):
        original = str(nodo)
        nucleo = original.strip()
        if not merece_traduccion(nucleo):
            continue

        izquierda = original[: len(original) - len(original.lstrip())]
        derecha = original[len(original.rstrip()):]
        traducido = traductor.traducir(nucleo)
        nodo.replace_with(NavigableString(izquierda + traducido + derecha))

    # 2) Atributos visibles
    for tag in soup.find_all(True):
        for attr in ATRIBUTOS_TRADUCIBLES:
            valor = tag.get(attr)
            if isinstance(valor, str) and merece_traduccion(valor.strip()):
                tag[attr] = traductor.traducir(valor.strip())

        if tag.name == "input" and tag.get("type") in {"submit", "reset", "button"}:
            valor = tag.get("value")
            if isinstance(valor, str) and merece_traduccion(valor.strip()):
                tag["value"] = traductor.traducir(valor.strip())

    # 3) Idioma del documento
    html = soup.find("html")
    if html is not None:
        html["lang"] = IDIOMA_DESTINO

    return str(soup).replace("</br>", "")


def ficheros_html() -> list[Path]:
    encontrados = []
    for ruta in RAIZ.rglob("*.html"):
        if any(parte in DIRECTORIOS_IGNORADOS for parte in ruta.parts):
            continue
        encontrados.append(ruta)
    return sorted(encontrados)


# --------------------------------------------------------------------------
# Programa principal
# --------------------------------------------------------------------------

def main() -> int:
    if SALIDA.exists():
        shutil.rmtree(SALIDA)
    SALIDA.mkdir(parents=True, exist_ok=True)

    rutas = ficheros_html()
    if not rutas:
        print("ERROR: no se ha encontrado ningún .html en el repositorio.")
        return 1

    traductor = Traductor()
    print(f"Ficheros a traducir: {', '.join(str(r) for r in rutas)}")
    if OFFLINE:
        print("MODO OFFLINE: no se llama a ningún servicio de traducción.")

    try:
        for ruta in rutas:
            print(f"\n== {ruta} ==")
            html = traducir_documento(ruta, traductor)
            destino = SALIDA / ruta.relative_to(RAIZ)
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_text(html, encoding="utf-8")
            print(f"   guardado en {destino}")
    finally:
        traductor.guardar_cache()

    for carpeta in CARPETAS_A_COPIAR:
        origen = RAIZ / carpeta
        if origen.is_dir():
            shutil.copytree(origen, SALIDA / carpeta, dirs_exist_ok=True)
            print(f"Copiada la carpeta '{carpeta}'.")

    print(f"\nCadenas traducidas mediante servicio: {traductor.llamadas}")
    print(f"Cadenas servidas desde la caché o fijadas a mano: "
          f"{len(traductor.cache) - traductor.llamadas}")

    if traductor.fallos:
        print(f"\nNo se pudieron traducir {len(traductor.fallos)} cadenas "
              f"(se han dejado en español):")
        for texto in traductor.fallos[:20]:
            print(f"  - {texto[:80]}")
        # Se sale con 0 para no romper el despliegue de la demo; si prefieres
        # que el workflow falle cuando algo no se traduce, devuelve 1 aquí.

    print("\n¡Traducción completada!")
    return 0


if __name__ == "__main__":
    sys.exit(main())

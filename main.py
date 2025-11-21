import sys 
from aSintactico import parser
from aLexico import lexer

def validar_programa(nombre_archivo):
    print(f"Iniciando compilación de: {nombre_archivo}")

    try:
        with open(nombre_archivo, 'r', encoding='utf-8') as f:
            data = f.read()
    except FileNotFoundError:
        print(f"Error: No se pudo abrir el archivo '{nombre_archivo}'")
        return
    
    #1. Primero haremos la validación léxica.
    print("Realizando Análisis Léxico...")
    lexer.input(data)
    error_lexico = False
    while True:
        token = lexer.token()
        if not token:
            break

    #2. Ahora continuaremos con la validación sintáctica.
    print("Realizando Análisis Sintáctico...")
    lexer.lineno = 1
    resultado = parser.parse(data)
    if resultado:
        print("EL CÓDIGO ES CORRECTO (Léxica y Sintácticamente)")
    else:
        print("PROGRAMA FINALIZADO CON ERRORES")

if __name__ == '__main__':
    archivo = 'pruebas/caso_exito.txt'
    if len(sys.argv) > 1:
        archivo = sys.argv[1]

    validar_programa(archivo) 
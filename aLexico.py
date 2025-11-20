
import ply.lex as lex
import re # Necesario para la función t_ID

# ===============================================
# 1. DECLARACIÓN DE TOKENS
# ===============================================

# Lista completa de Tokens Terminales para el Analizador Sintáctico
tokens = [
    # Palabras Reservadas
    'SELECT', 'WHERE', 'CREATE', 'TABLE', 'INT', 'VARCHAR', 'DECIMAL',
    'MIN', 'MAX', 'COUNT', 'AND', 'OR', 'NOT',
    # Operadores y Símbolos
    'MAS', 'MENOS', 'POR', 'DIV', 'IGUAL', 'MAYOR', 'MENOR',
    'MAYOR_IGUAL', 'MENOR_IGUAL', 'PARENT_IZQ', 'PARENT_DER',
    'COMA', 'PUNTO_COMA',
    # Identificadores y Constantes
    'ID', 'NUM_ENTERO', 'NUM_REAL', 'CADENA'
]

# Diccionario de Palabras Reservadas (para manejar insensibilidad)
# Usaremos esto en la función t_ID
reserved = {
    'select': 'SELECT', 'where': 'WHERE', 'create': 'CREATE', 'table': 'TABLE',
    'int': 'INT', 'varchar': 'VARCHAR', 'decimal': 'DECIMAL',
    'min': 'MIN', 'max': 'MAX', 'count': 'COUNT',
    'and': 'AND', 'or': 'OR', 'not': 'NOT'
}

# 2. SECCIÓN DE EXPRESIONES REGULARES (ER)
# ===============================================

# 2.1 Expresiones Regulares para Símbolos Simples (se pueden definir con t_TOKEN)
t_MAS            = r'\+'
t_MENOS          = r'-'
t_POR            = r'\*' # El asterisco debe escaparse
t_DIV            = r'/'
t_IGUAL          = r'='
t_MAYOR          = r'>'
t_MENOR          = r'<'
t_PARENT_IZQ     = r'\(' # El paréntesis debe escaparse
t_PARENT_DER     = r'\)'
t_COMA           = r','
t_PUNTO_COMA     = r';'

# 2.2 Expresiones Regulares para Símbolos Compuestos (deben ir antes para Preanálisis)
# El analizador léxico de PLY prioriza las ER definidas como funciones.
# Se definen de mayor longitud a menor para resolver el conflicto de '>' vs '>='
t_MAYOR_IGUAL    = r'>='
t_MENOR_IGUAL    = r'<='

# 2.3 Expresiones Regulares para Constantes
t_CADENA         = r"'[^']*'"

# 2.4 Expresiones Regulares para Componentes a Descartar (t_ignore_...)
# Descarte de espacios en blanco, tabulaciones y retornos de carro.
t_ignore = ' \t' 

# ===============================================
# 3. DEFINICIÓN DE TOKENS COMPLEJOS Y FUNCIONES
# ===============================================

# Identificadores y Palabras Reservadas (ID)
def t_ID(t):
    # Expresión Regular para ID: letra(letra | dígito | _)*
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    # Convierte a minúsculas para buscar en el diccionario de reservadas
    t.type = reserved.get(t.value.lower(), 'ID') 
    return t

# Números Reales (debe ir antes que NUM_ENTERO)
def t_NUM_REAL(t):
    # ER: digito+.digito+ | .digito+
    r'(\d+\.\d*|\.\d+)'
    t.value = float(t.value)
    return t

# Números Enteros
def t_NUM_ENTERO(t):
    # ER: digito+
    r'\d+'
    t.value = int(t.value)
    return t

# Comentarios (Descartar)
def t_COMENTARIO(t):
    # ER: --.* (dos guiones seguidos de cualquier cosa hasta el fin de línea)
    r'--[^\n]*'
    # No retorna nada, por lo que el token se descarta 
    pass

# Saltos de Línea (para conteo de línea)
def t_newline(t):
    # ER: \n (un salto de línea)
    r'\n+'
    t.lexer.lineno += t.value.count('\n') # Incrementa el contador de línea 
    pass

# Tratamiento de Errores Léxicos
def t_error(t):
    # El lexema (t.value) contiene la secuencia no reconocida [cite: 160]
    print(f"Error Léxico en línea {t.lineno}: Carácter ilegal '{t.value[0]}'")
    t.lexer.skip(1) # Ignora el carácter y sigue analizando [cite: 1]

# ===============================================
# 4. CONSTRUCCIÓN Y PRUEBA
# ===============================================

# Construcción del Analizador Léxico (Scanner)
lexer = lex.lex(reflags=re.IGNORECASE) # Usar re.IGNORECASE para hacer el t_ID más flexible

# --- Bloque de Prueba (Adaptado de Ejemplo 2) ---
if __name__ == '__main__':
    filename='prueba_sql.txt' # Nombre de archivo de prueba (A ser creado)
    
    # Intenta leer el archivo
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = f.read()
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{filename}'. Creando datos de prueba por defecto.")
        data = "CREATE TABLE Clientes (ID INT, Nombre VARCHAR(50), Saldo DECIMAL(10,2));\n"
        data += "SELECT Nombre, MIN(Saldo) FROM Clientes WHERE Saldo >= 100.00 -- Fin de consulta\n"
        data += "SELECT * FROM Productos;"
        
    lexer.input(data)

    print('====================================================')
    print('Token         | Lexema                | Línea')
    print('====================================================')
    while True:
        tok = lexer.token()
        if not tok: break
        # Formato de salida para la prueba
        print(f"{tok.type:13} | {tok.value!s:21} | {tok.lineno}")
    print('====================================================')
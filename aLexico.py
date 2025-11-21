
import ply.lex as lex
import re # Necesario para la función t_ID


lex.error_list = [] 
lex.error_count = 0
# ===============================================
# 1. DECLARACIÓN DE TOKENS
# ===============================================

# Lista completa de Tokens Terminales para el Analizador Sintáctico
tokens = [
    # Palabras Reservadas
    'SELECT', 'FROM', 'WHERE', 'CREATE', 'TABLE', 'INT', 'VARCHAR', 'DECIMAL',
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
    'select': 'SELECT', 'from': 'FROM', 'where': 'WHERE', 'create': 'CREATE', 'table': 'TABLE',
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
    # Almacenar el error en la lista en lugar de imprimirlo
    error_msg = f"Error Léxico en línea {t.lineno}: Carácter ilegal '{t.value[0]}'"
    # Añadir al listado de errores que será consumido por main.py
    t.lexer.error_list.append(error_msg) 
    t.lexer.skip(1)

def reset_lexer():
    lexer.lineno = 1
    lexer.error_list = []

# ===============================================
# 4. CONSTRUCCIÓN Y PRUEBA
# ===============================================

# Construcción del Analizador Léxico (Scanner)
lexer = lex.lex(reflags=re.IGNORECASE)
lexer.reset_lexer = reset_lexer


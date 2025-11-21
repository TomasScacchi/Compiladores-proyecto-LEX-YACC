import ply.yacc as yacc
from aLexico import tokens
import sys


# Mapeo de tokens técnicos a nombres amigables para el usuario
nombres_amigables = {
    'PUNTO_COMA': '";"',
    'COMA': '","',
    'PARENT_IZQ': '"("',
    'PARENT_DER': '")"',
    'IGUAL': '"="',
    'MAS': '"+"',
    'MENOS': '"-"',
    'POR': '"*"',
    'DIV': '"/"',
    'ID': 'Identificador',
    'NUM_ENTERO': 'Número Entero',
    'NUM_REAL': 'Número Real',
    'CADENA': 'Cadena de texto',
    'SELECT': 'SELECT',
    'FROM': 'FROM',
    'WHERE': 'WHERE',
    'CREATE': 'CREATE',
    'TABLE': 'TABLE',
}
# ===============================================
# 1. DEFINICIÓN DE LA GRAMÁTICA 
# ===============================================

#REGLAS DE PRODUCCIÓN EN BASE AL AVANCE DEL PROYECTO:

# Símbolo inicial S = {programa}
def p_programa(p):
    '''programa : sentencia
                | programa sentencia
                | programa error PUNTO_COMA'''  
    p[0] = "Programa compilado correctamente!"

def p_sentencia(p):
    '''sentencia : sentencia_select PUNTO_COMA
                 | sentencia_create PUNTO_COMA'''
    pass

def p_sentencia_error(p):
    '''sentencia : error PUNTO_COMA'''
    global parser
    parser.errok()

def p_sentencia_create(p):
    '''sentencia_create : CREATE TABLE ID PARENT_IZQ lista_columna PARENT_DER'''
    pass

def p_lista_columna(p):
    '''lista_columna : def_columna COMA lista_columna
                     | def_columna'''
    pass

def p_def_columna(p):
    '''def_columna : ID tipo_dato'''
    pass

def p_tipo_dato(p):
    '''tipo_dato : INT
                 | VARCHAR PARENT_IZQ NUM_ENTERO PARENT_DER
                 | DECIMAL PARENT_IZQ NUM_ENTERO COMA NUM_ENTERO PARENT_DER'''
    pass

def p_sentencia_select(p):
    '''sentencia_select : SELECT lista_campos FROM ID where_opcional'''
    pass

def p_where_opcional(p):
    '''where_opcional : WHERE condicion
                      | empty'''
    pass

def p_lista_campos(p):
    '''lista_campos : elemento COMA lista_campos
                    | elemento
                    | POR'''
    pass

def p_elemento(p):
    '''elemento : ID
                | funcion_agr'''
    pass

def p_funcion_agr(p):
    '''funcion_agr : MIN PARENT_IZQ ID PARENT_DER
                   | MAX PARENT_IZQ ID PARENT_DER
                   | COUNT PARENT_IZQ ID PARENT_DER'''
    pass

def p_condicion(p):
    '''condicion : expr_logica'''
    pass

def p_expr_logica(p):
    '''expr_logica : expr_logica OR term_logico
                   | term_logico'''
    pass

def p_term_logico(p):
    '''term_logico : term_logico AND factor_logico
                   | factor_logico'''
    pass

def p_factor_logico(p):
    '''factor_logico : NOT factor_logico
                     | predicado'''
    pass

def p_predicado(p):
    '''predicado : expresion op_comparacion expresion
                 | PARENT_IZQ condicion PARENT_DER'''
    pass

def p_op_comparacion(p):
    '''op_comparacion : IGUAL
                      | MAYOR
                      | MENOR
                      | MAYOR_IGUAL
                      | MENOR_IGUAL'''
    pass

def p_expresion(p):
    ''' expresion : expresion MAS termino
                  | expresion MENOS termino
                  | termino'''
    pass

def p_termino(p):
    '''termino : termino POR factor
               | termino DIV factor
               | factor'''
    pass

def p_factor(p):
    '''factor : ID
              | NUM_ENTERO
              | NUM_REAL
              | CADENA
              | PARENT_IZQ expresion PARENT_DER'''
    pass

def p_empty(p):
    '''empty :'''
    pass

# ===============================================
# 2. MANEJO DE ERRORES SINTÁCTICOS 
# ===============================================

def p_error(p):
    # Traemos el parser global para inspeccionar su estado actual
    global parser
    
    if p:
        # Obtenemos el estado actual de la pila del parser
        # (El estado antes de que ocurriera el error)
        estado_actual = parser.state
        
        # Buscamos en la tabla de acciones qué tokens eran válidos en este estado
        acciones_validas = parser.action[estado_actual].keys()
        
        # Filtramos tokens internos de PLY (como $end o error)
        esperados = []
        for token in acciones_validas:
            if token not in ('$end', 'error'):
                # Usamos el nombre amigable si existe, sino el nombre técnico
                nombre = nombres_amigables.get(token, token)
                esperados.append(nombre)
        
        # Formateamos la lista de esperados (ej: "';', ','")
        mensaje_esperado = " o ".join(esperados)
        
        print(f"Error de sintaxis en la línea {p.lineno}: Se encontró '{p.value}' pero se esperaba {mensaje_esperado}.")
    else:
        print("Error de sintaxis: Final inesperado del archivo (quizás falta un ';' o cerrar paréntesis).")

#Para construir el parser, usamos la función específicada en la lección 13: PLY YACC (yacc.yacc):
if getattr(sys, 'frozen', False):
    # MODO EXE
    parser = yacc.yacc(debug=False, write_tables=False, errorlog=yacc.NullLogger())
else:
    # MODO NORMAL 
    parser = yacc.yacc()

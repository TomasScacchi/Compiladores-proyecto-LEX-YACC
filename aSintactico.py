import ply.yacc as yacc
from aLexico import tokens

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
                 | sentencia_create PUNTO_COMA
                 | error PUNTO_COMA         
                 | error'''
    pass

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
    if p:
        print (f"Error de sintaxis en la línea {p.lineno}: Se encontró '{p.value}' inesperado.")
    else:
        print ("Error de sintaxis al final del archivo.")

#Para construir el parser, usamos la función específicada en la lección 13: PLY YACC (yacc.yacc):
parser = yacc.yacc()

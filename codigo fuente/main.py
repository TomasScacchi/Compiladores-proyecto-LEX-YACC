import sys
import tkinter as tk
from tkinter import filedialog, scrolledtext
import io
import contextlib
import os
# Importamos el parser y el lexer definidos
from aSintactico import parser 
from aLexico import lexer 


# --- COLORES ---
BG_DARK = '#2e2e2e'      
FG_LIGHT = '#cccccc'      
BG_CONSOLE = '#1e1e1e'    
COLOR_SUCCESS = '#70c770' 
COLOR_ERROR = '#ff6b6b'   

# 1. LÓGICA DE COMPILACIÓN
def compilar_programa(data, output_widget, code_widget):
    """Realiza el análisis léxico y sintáctico del código fuente y reporta."""
    output_widget.delete(1.0, tk.END)
    output_widget.insert(tk.END, "Iniciando compilación...\n")
    
    # 1. Análisis Léxico (Pasada completa)
    output_widget.insert(tk.END, "Realizando Análisis Léxico...\n")
    
    # Resetear el lexer y sus contadores de error antes de cada análisis
    lexer.reset_lexer() 
    lexer.input(data)
 
    try:
        while True:
            token = lexer.token()
            if not token:
                break
    except Exception as e:
        output_widget.insert(tk.END, f"Error interno durante el Análisis Léxico: {e}\n", 'error')
        return

    lex_errors = "\n".join(lexer.error_list)
    lex_error_count = len(lexer.error_list)
    
    # 2. Análisis Sintáctico
    output_widget.insert(tk.END, "Realizando Análisis Sintáctico...\n")
    
    # Resetear de nuevo para el parser
    lexer.reset_lexer()
    lexer.input(data) 
    
    syn_output = io.StringIO()
    with contextlib.redirect_stdout(syn_output):
        parser.parse(data, lexer=lexer)
    
    syn_errors_raw = syn_output.getvalue().strip()
    
    syn_error_lines = [line for line in syn_errors_raw.split('\n') if "Error de sintaxis" in line]
    syn_errors = "\n".join(syn_error_lines)
    syn_error_count = len(syn_error_lines)
    

    # --- 3. REPORTE DE RESULTADOS (LIMPIO) ---
    
    is_correct = (lex_error_count == 0) and (syn_error_count == 0)

    output_widget.insert(tk.END, "\n--- RESULTADO DEL ANÁLISIS ---\n", 'header')

    # 3.1 Reporte de Errores Léxicos
    output_widget.insert(tk.END, "Errores léxicos:\n", 'error')
    if lex_errors:
        for line in lex_errors.split('\n'):
             output_widget.insert(tk.END, f" - {line}\n", 'error')
    else:
        output_widget.insert(tk.END, " - Ninguno\n", 'success')

    # 3.2 Reporte de Errores Sintácticos
    output_widget.insert(tk.END, "\n Errores sintácticos:\n", 'error')
    if syn_errors:
        for line in syn_errors.split('\n'):
             output_widget.insert(tk.END, f" - {line}\n", 'error')
    else:
        output_widget.insert(tk.END, " - Ninguno\n", 'success')
    
    # 3.3 Resumen Final
    output_widget.insert(tk.END, "\n-----------------------------\n")
    output_widget.insert(tk.END, f"Errores léxicos: {lex_error_count}\n")
    output_widget.insert(tk.END, f"Errores sintácticos: {syn_error_count}\n")
    
    if is_correct:
        output_widget.insert(tk.END, "COMPILACIÓN EXITOSA: CÓDIGO CORRECTO\n", 'success')
    else:
        output_widget.insert(tk.END, "PROGRAMA FINALIZADO CON ERRORES\n", 'error')
        
    output_widget.insert(tk.END, "-----------------------------\n")

    code_widget.delete(1.0, tk.END)
    code_widget.insert(tk.END, data)



class CompilerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Compilador SQL - Grupo N° 23")
        
        # --- APLICAR TEMA OSCURO A LA VENTANA PRINCIPAL ---
        master.config(bg=BG_DARK) 
        
        # 2.1 Configuración de Frames
        self.code_frame = tk.Frame(master, bg=BG_DARK)
        self.code_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.console_frame = tk.Frame(master, bg=BG_DARK)
        self.console_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 2.2 Visor de Código Fuente
        tk.Label(self.code_frame, text="Contenido del Archivo (.txt):", bg=BG_DARK, fg=FG_LIGHT).pack(pady=5)
        self.code_viewer = scrolledtext.ScrolledText(
            self.code_frame, wrap=tk.NONE, width=80, height=12, font=('Consolas', 10), 
            state=tk.DISABLED, bg=BG_CONSOLE, fg=FG_LIGHT, insertbackground=FG_LIGHT # Colores de consola
        )
        self.code_viewer.pack(fill=tk.BOTH, expand=True)

        # 2.3 Consola de Resultados
        tk.Label(self.console_frame, text="Resultados del Análisis (Consola):", bg=BG_DARK, fg=FG_LIGHT).pack(pady=5)
        self.console = scrolledtext.ScrolledText(
            self.console_frame, wrap=tk.WORD, width=80, height=12, font=('Consolas', 10),
            bg=BG_CONSOLE, fg=FG_LIGHT, insertbackground=FG_LIGHT # Colores de consola
        )
        self.console.pack(fill=tk.BOTH, expand=True)
        
        # Configuración de Tags (errores y éxito)
        self.console.tag_config('header', foreground='yellow', font=('Consolas', 10, 'bold'))
        self.console.tag_config('error', foreground=COLOR_ERROR, font=('Consolas', 10, 'bold'))
        self.console.tag_config('success', foreground=COLOR_SUCCESS, font=('Consolas', 10, 'bold'))
        
        # 2.4 Panel de Control (Botones)
        self.control_frame = tk.Frame(master, bg=BG_DARK)
        self.control_frame.pack(pady=10)
        
        self.file_path = tk.StringVar(value="Ningún archivo seleccionado...")
        tk.Label(self.control_frame, textvariable=self.file_path, width=40, bg=BG_DARK, fg=FG_LIGHT).pack(side=tk.LEFT, padx=5)

        # Estilo de botones para tema oscuro
        button_style = {'bg': '#555555', 'fg': FG_LIGHT, 'activebackground': '#777777', 'activeforeground': FG_LIGHT, 'relief': tk.RAISED}
        
        tk.Button(self.control_frame, text="Cargar Archivo", command=self.load_file, **button_style).pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_frame, text="Analizar Contenido", command=self.run_analysis, bg='#007acc', fg='white', activebackground='#0095ff').pack(side=tk.LEFT, padx=5) # Botón principal
        tk.Button(self.control_frame, text="Limpiar Todo", command=self.clear_all, **button_style).pack(side=tk.LEFT, padx=5)

    def load_file(self):
        """Abre el diálogo para seleccionar archivos .txt y muestra el contenido."""
        file_selected = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_selected:
            self.file_path.set(file_selected)
            self.console.delete(1.0, tk.END)
            
            try:
                with open(file_selected, 'r', encoding='utf-8') as f:
                    data = f.read()
                
                self.code_viewer.config(state=tk.NORMAL)
                self.code_viewer.delete(1.0, tk.END)
                self.code_viewer.insert(tk.END, data)
                self.code_viewer.config(state=tk.DISABLED)
                
                self.console.insert(tk.END, f"Archivo cargado correctamente: {os.path.basename(file_selected)}\n")
            except Exception as e:
                self.console.insert(tk.END, f"Error al leer el archivo: {e}\n", 'error')
                self.file_path.set("Error de lectura...")

    def run_analysis(self):
        """Inicia el proceso de compilación con el contenido actual del visor."""
        self.console.delete(1.0, tk.END)
        
        self.code_viewer.config(state=tk.NORMAL)
        data = self.code_viewer.get(1.0, tk.END)
        self.code_viewer.config(state=tk.DISABLED)
        
        if not data.strip():
            self.console.insert(tk.END, "Error: No hay contenido para analizar. Cargue un archivo.\n", 'error')
            return

        compilar_programa(data, self.console, self.code_viewer)

    def clear_all(self):
        """Limpia el visor de código y la consola de resultados."""
        self.code_viewer.config(state=tk.NORMAL)
        self.code_viewer.delete(1.0, tk.END)
        self.code_viewer.config(state=tk.DISABLED)
        self.console.delete(1.0, tk.END)
        self.file_path.set("Ningún archivo seleccionado...")


if __name__ == '__main__':
    root = tk.Tk()
    gui = CompilerGUI(root)
    root.mainloop()
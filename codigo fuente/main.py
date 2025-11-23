import sys
import tkinter as tk
from tkinter import filedialog, scrolledtext
import io
import contextlib
import os
import re

# Importamos el parser y el lexer definidos
from aSintactico import parser 
from aLexico import lexer 

# --- COLORES ---
BG_DARK = '#2e2e2e'      
FG_LIGHT = '#cccccc'      
BG_CONSOLE = '#1e1e1e'    
COLOR_SUCCESS = '#70c770' 
COLOR_ERROR = '#ff6b6b'
COLOR_HIGHLIGHT_ERROR = '#5e2a2a' 
SASH_COLOR = '#444444'

# 1. LÓGICA DE COMPILACIÓN
def compilar_programa(data, output_widget, code_widget):
    """Realiza el análisis léxico y sintáctico del código fuente y reporta."""
    
    output_widget.delete(1.0, tk.END)
    code_widget.tag_remove('error_line', '1.0', tk.END)
    
    output_widget.insert(tk.END, "Iniciando compilación...\n")
    
    lineas_con_error = set()

    # 1. Análisis Léxico
    output_widget.insert(tk.END, "Realizando Análisis Léxico...\n")
    lexer.reset_lexer() 
    lexer.input(data)
 
    try:
        while True:
            token = lexer.token()
            if not token: break
    except Exception as e:
        output_widget.insert(tk.END, f"Error interno: {e}\n", 'error')
        return

    lex_errors = "\n".join(lexer.error_list)
    lex_error_count = len(lexer.error_list)
    
    for err in lexer.error_list:
        match = re.search(r'línea\s+(\d+)', err)
        if match: lineas_con_error.add(int(match.group(1)))

    # 2. Análisis Sintáctico
    output_widget.insert(tk.END, "Realizando Análisis Sintáctico...\n")
    lexer.reset_lexer()
    lexer.input(data) 
    
    syn_output = io.StringIO()
    with contextlib.redirect_stdout(syn_output):
        parser.parse(data, lexer=lexer)
    
    syn_errors_raw = syn_output.getvalue().strip()
    syn_error_lines = [line for line in syn_errors_raw.split('\n') if "Error de sintaxis" in line]
    syn_errors = "\n".join(syn_error_lines)
    syn_error_count = len(syn_error_lines)
    
    for err in syn_error_lines:
        match = re.search(r'línea\s+(\d+)', err)
        if match: lineas_con_error.add(int(match.group(1)))

    # 3. Reporte
    is_correct = (lex_error_count == 0) and (syn_error_count == 0)
    output_widget.insert(tk.END, "\n--- RESULTADO DEL ANÁLISIS ---\n", 'header')

    output_widget.insert(tk.END, "Errores léxicos:\n", 'error')
    if lex_errors:
        for line in lex_errors.split('\n'): output_widget.insert(tk.END, f" - {line}\n", 'error')
    else:
        output_widget.insert(tk.END, " - Ninguno\n", 'success')

    output_widget.insert(tk.END, "\nErrores sintácticos:\n", 'error')
    if syn_errors:
        for line in syn_errors.split('\n'): output_widget.insert(tk.END, f" - {line}\n", 'error')
    else:
        output_widget.insert(tk.END, " - Ninguno\n", 'success')
    
    output_widget.insert(tk.END, "\n-----------------------------\n")
    output_widget.insert(tk.END, f"Errores léxicos: {lex_error_count}\n")
    output_widget.insert(tk.END, f"Errores sintácticos: {syn_error_count}\n")
    
    if is_correct:
        output_widget.insert(tk.END, "COMPILACIÓN EXITOSA: CÓDIGO CORRECTO\n", 'success')
    else:
        output_widget.insert(tk.END, "PROGRAMA FINALIZADO CON ERRORES\n", 'error')
        for num_linea in lineas_con_error:
            code_widget.tag_add('error_line', f"{num_linea}.0", f"{num_linea}.end")

    output_widget.insert(tk.END, "-----------------------------\n")


class CompilerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Compilador SQL - Grupo N° 23")
        master.geometry("1300x700") 
        master.config(bg=BG_DARK) 

        self.paned_window = tk.PanedWindow(master, orient=tk.HORIZONTAL, bg=BG_DARK, sashwidth=6, sashrelief=tk.RAISED)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # ------------------------------------------------------------
        # 1. PANEL IZQUIERDO: EDITOR 
        # ------------------------------------------------------------
        self.frame_editor = tk.Frame(self.paned_window, bg=BG_DARK)
        
        tk.Label(self.frame_editor, text="Editor de Código SQL:", bg=BG_DARK, fg=FG_LIGHT, font=('Arial', 10, 'bold')).pack(anchor='w')
        
        
        self.editor_container = tk.Frame(self.frame_editor, bg=BG_DARK)
        self.editor_container.pack(fill=tk.BOTH, expand=True)

        
        self.h_scroll_editor = tk.Scrollbar(self.editor_container, orient='horizontal')
        
        
        self.code_viewer = scrolledtext.ScrolledText(
            self.editor_container, wrap=tk.NONE, font=('Consolas', 11), 
            bg=BG_CONSOLE, fg=FG_LIGHT, insertbackground=FG_LIGHT
        )
        
        
        self.code_viewer.config(xscrollcommand=self.h_scroll_editor.set)
        self.h_scroll_editor.config(command=self.code_viewer.xview)

        
        self.h_scroll_editor.pack(side=tk.BOTTOM, fill=tk.X)
        self.code_viewer.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.code_viewer.tag_config('error_line', background=COLOR_HIGHLIGHT_ERROR)
        
        
        self.paned_window.add(self.frame_editor, minsize=400, stretch="always")

        # ------------------------------------------------------------
        # 2. PANEL CENTRAL: BOTONES
        # ------------------------------------------------------------
        self.frame_controls = tk.Frame(self.paned_window, bg=BG_DARK)
        
       
        tk.Frame(self.frame_controls, bg=BG_DARK, height=80).pack()
        
        btn_opts = {'width': 14, 'font': ('Arial', 9, 'bold'), 'relief': tk.RAISED, 'bd': 3, 'cursor': 'hand2'}
        
        self.btn_load = tk.Button(self.frame_controls, text="Cargar", command=self.load_file, bg='#555555', fg=FG_LIGHT, **btn_opts)
        self.btn_load.pack(pady=10, padx=10)

        self.btn_run = tk.Button(self.frame_controls, text="COMPILAR", command=self.run_analysis, bg='#007acc', fg='white', activebackground='#0095ff', **btn_opts)
        self.btn_run.pack(pady=20, padx=10)

        self.btn_clear = tk.Button(self.frame_controls, text="Limpiar", command=self.clear_all, bg='#555555', fg=FG_LIGHT, **btn_opts)
        self.btn_clear.pack(pady=10, padx=10)
        
        self.file_path_var = tk.StringVar(value="")
        tk.Label(self.frame_controls, textvariable=self.file_path_var, wraplength=120, bg=BG_DARK, fg='#888888', font=('Arial', 8)).pack(pady=20)

        self.paned_window.add(self.frame_controls, minsize=150, stretch="never")

        # ------------------------------------------------------------
        # 3. PANEL DERECHO: CONSOLA (Con Scroll Horizontal y Vertical)
        # ------------------------------------------------------------
        self.frame_console = tk.Frame(self.paned_window, bg=BG_DARK)
        
        tk.Label(self.frame_console, text="Reporte de Compilación:", bg=BG_DARK, fg=FG_LIGHT, font=('Arial', 10, 'bold')).pack(anchor='w')

        self.console_container = tk.Frame(self.frame_console, bg=BG_DARK)
        self.console_container.pack(fill=tk.BOTH, expand=True)

        self.h_scroll_console = tk.Scrollbar(self.console_container, orient='horizontal')

        self.console = scrolledtext.ScrolledText(
            self.console_container, wrap=tk.NONE, font=('Consolas', 10), 
            bg=BG_CONSOLE, fg=FG_LIGHT
        )
        
        self.console.config(xscrollcommand=self.h_scroll_console.set)
        self.h_scroll_console.config(command=self.console.xview)

        self.h_scroll_console.pack(side=tk.BOTTOM, fill=tk.X)
        self.console.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        
        self.console.tag_config('header', foreground='yellow', font=('Consolas', 10, 'bold'))
        self.console.tag_config('error', foreground=COLOR_ERROR, font=('Consolas', 10, 'bold'))
        self.console.tag_config('success', foreground=COLOR_SUCCESS, font=('Consolas', 10, 'bold'))

        
        self.paned_window.add(self.frame_console, minsize=400, stretch="always")

    def load_file(self):
        file_selected = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_selected:
            self.file_path_var.set(os.path.basename(file_selected))
            self.console.delete(1.0, tk.END)
            self.code_viewer.tag_remove('error_line', '1.0', tk.END)
            try:
                with open(file_selected, 'r', encoding='utf-8') as f:
                    data = f.read()
                self.code_viewer.delete(1.0, tk.END)
                self.code_viewer.insert(tk.END, data)
                self.console.insert(tk.END, f"Archivo cargado: {os.path.basename(file_selected)}\nListo para analizar.\n")
            except Exception as e:
                self.console.insert(tk.END, f"Error al leer el archivo: {e}\n", 'error')

    def run_analysis(self):
        data = self.code_viewer.get(1.0, tk.END)
        if not data.strip():
            self.console.delete(1.0, tk.END)
            self.console.insert(tk.END, "Error: El editor está vacío.\n", 'error')
            return
        compilar_programa(data, self.console, self.code_viewer)

    def clear_all(self):
        self.code_viewer.delete(1.0, tk.END)
        self.code_viewer.tag_remove('error_line', '1.0', tk.END)
        self.console.delete(1.0, tk.END)
        self.file_path_var.set("")

if __name__ == '__main__':
    root = tk.Tk()
    gui = CompilerGUI(root)
    root.mainloop()
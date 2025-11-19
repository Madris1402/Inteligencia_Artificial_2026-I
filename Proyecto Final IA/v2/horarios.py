import tkinter as tk
from layout.interfaz import GeneradorHorariosGUI

def main():
    """Función principal que lanza la interfaz gráfica"""
    root = tk.Tk()
    app = GeneradorHorariosGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()  
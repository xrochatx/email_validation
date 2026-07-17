import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from email_validation_core import read_emails_from_csv, save_results_to_csv, validate_emails_in_batches

# --- Interfaz gráfica con Tkinter ---
class EmailValidatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Validador de Correos Electrónicos")
        self.root.geometry("720x560")

        self.status_var = tk.StringVar(value="Listo")
        self.smtp_var = tk.BooleanVar(value=False)

        self.btn_csv = tk.Button(root, text="Seleccionar archivo CSV", command=self.select_csv)
        self.btn_csv.pack(pady=5)

        self.smtp_check = tk.Checkbutton(
            root,
            text="Incluir verificación SMTP, más lenta y menos confiable",
            variable=self.smtp_var,
        )
        self.smtp_check.pack(pady=2)

        self.label_manual = tk.Label(root, text="Ingrese correos separados por comas:")
        self.label_manual.pack()

        self.entry_manual = tk.Entry(root, width=50)
        self.entry_manual.pack(pady=5)

        self.btn_manual = tk.Button(root, text="Validar Correos", command=self.validate_manual)
        self.btn_manual.pack(pady=5)

        self.status_label = tk.Label(root, textvariable=self.status_var, anchor="w")
        self.status_label.pack(fill="x", padx=10, pady=(4, 0))

        self.result_text = scrolledtext.ScrolledText(root, width=70, height=15)
        self.result_text.pack(pady=5)

        self.btn_save = tk.Button(root, text="Guardar Resultados", command=self.save_results)
        self.btn_save.pack(pady=5)

        self.results = []
        self.processing = False

    def set_processing(self, is_processing, message):
        self.processing = is_processing
        state = tk.DISABLED if is_processing else tk.NORMAL
        self.btn_csv.config(state=state)
        self.btn_manual.config(state=state)
        self.btn_save.config(state=state)
        self.smtp_check.config(state=state)
        self.status_var.set(message)

    def schedule_ui_update(self, callback, *args):
        self.root.after(0, lambda: callback(*args))

    def select_csv(self):
        """Selecciona y valida correos desde un archivo CSV."""
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            self.result_text.insert(tk.END, "Validando correos desde CSV...\n")
            self.set_processing(True, "Validando archivo CSV...")
            threading.Thread(target=self.process_csv, args=(file_path,), daemon=True).start()

    def process_csv(self, file_path):
        """Procesa la validación del CSV en un hilo separado."""
        emails = read_emails_from_csv(file_path)
        self.results = validate_emails_in_batches(emails, check_smtp=self.smtp_var.get())
        self.schedule_ui_update(self.display_results)
        self.schedule_ui_update(self.set_processing, False, f"Archivo procesado: {len(self.results)} correos")

    def validate_manual(self):
        """Valida los correos ingresados manualmente."""
        emails = self.entry_manual.get().split(",")
        emails = [email.strip() for email in emails if email.strip()]
        
        if not emails:
            messagebox.showwarning("Entrada vacía", "Ingrese al menos un correo.")
            return

        self.result_text.insert(tk.END, "Validando correos manualmente...\n")
        self.set_processing(True, "Validando entrada manual...")
        threading.Thread(target=self.process_manual, args=(emails,), daemon=True).start()

    def process_manual(self, emails):
        """Procesa la validación manual en un hilo separado."""
        self.results = validate_emails_in_batches(emails, check_smtp=self.smtp_var.get())
        self.schedule_ui_update(self.display_results)
        self.schedule_ui_update(self.set_processing, False, f"Validación completada: {len(self.results)} correos")

    def display_results(self):
        """Muestra los resultados en la interfaz."""
        self.result_text.delete("1.0", tk.END)
        for result in self.results:
            status = "Válido" if result.is_valid else "Inválido"
            self.result_text.insert(tk.END, f"{result.email}: {status} ({result.message})\n")

    def save_results(self):
        """Guarda los resultados en un archivo CSV."""
        if not self.results:
            messagebox.showwarning("Sin resultados", "No hay resultados para guardar.")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if save_path:
            output_path = save_results_to_csv(self.results, save_path)
            messagebox.showinfo("Guardado", f"Resultados guardados en {output_path}")

# --- Inicialización del programa ---
if __name__ == "__main__":
    root = tk.Tk()
    app = EmailValidatorApp(root)
    root.mainloop()

import csv
import concurrent.futures
import smtplib
import dns.resolver
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from email_validator import validate_email, EmailNotValidError

def validate_email_address(email):
    """Valida un correo electrónico utilizando email-validator."""
    try:
        valid = validate_email(email, check_deliverability=False)
        return email, True, "Valid"
    except EmailNotValidError as e:
        return email, False, str(e)

def check_mx_records(email):
    """Verifica si el dominio del correo tiene registros MX válidos."""
    domain = email.split('@')[-1]
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        return True if mx_records else False
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.Timeout):
        return False

def verify_smtp(email):
    """Verifica si un correo existe mediante conexión SMTP."""
    domain = email.split('@')[-1]
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        mx_record = str(mx_records[0].exchange)

        with smtplib.SMTP(mx_record) as server:
            server.set_debuglevel(0)
            server.helo()
            server.mail('test@example.com')
            code, _ = server.rcpt(email)
            return code == 250  # Código 250 indica que el correo existe
    except Exception:
        return False

def validate_email_full(email):
    """Valida el correo con reglas sintácticas, MX y SMTP."""
    is_valid, message = validate_email_address(email)[1:]
    if is_valid:
        has_mx = check_mx_records(email)
        if has_mx:
            exists = verify_smtp(email)
            return email, exists, "SMTP Verificado" if exists else "No encontrado en SMTP"
        else:
            return email, False, "Dominio sin registros MX"
    return email, False, message

def validate_emails_in_batches(emails, batch_size=100):
    """Divide y valida correos en lotes para optimizar el rendimiento."""
    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for i in range(0, len(emails), batch_size):
            batch = emails[i:i+batch_size]
            future_results = list(executor.map(validate_email_full, batch))
            results.extend(future_results)
    return results

def validate_from_csv(file_path):
    """Lee y valida correos desde un archivo CSV."""
    emails = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row:  # Evita filas vacías
                emails.append(row[0].strip())
    return validate_emails_in_batches(emails)

def save_results_to_csv(results, output_file="email_validation_results.csv"):
    """Guarda los resultados de validación en un archivo CSV."""
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Email", "Valid", "Message"])
        writer.writerows(results)
    messagebox.showinfo("Guardado", f"Resultados guardados en {output_file}")

# --- Interfaz gráfica con Tkinter ---
class EmailValidatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Validador de Correos Electrónicos")
        self.root.geometry("600x500")

        # Botón para seleccionar archivo CSV
        self.btn_csv = tk.Button(root, text="Seleccionar archivo CSV", command=self.select_csv)
        self.btn_csv.pack(pady=5)

        # Entrada manual de correos
        self.label_manual = tk.Label(root, text="Ingrese correos separados por comas:")
        self.label_manual.pack()

        self.entry_manual = tk.Entry(root, width=50)
        self.entry_manual.pack(pady=5)

        self.btn_manual = tk.Button(root, text="Validar Correos", command=self.validate_manual)
        self.btn_manual.pack(pady=5)

        # Área de texto para mostrar resultados
        self.result_text = scrolledtext.ScrolledText(root, width=70, height=15)
        self.result_text.pack(pady=5)

        # Botón para guardar resultados
        self.btn_save = tk.Button(root, text="Guardar Resultados", command=self.save_results)
        self.btn_save.pack(pady=5)

        self.results = []

    def select_csv(self):
        """Selecciona y valida correos desde un archivo CSV."""
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            self.result_text.insert(tk.END, "Validando correos desde CSV...\n")
            threading.Thread(target=self.process_csv, args=(file_path,)).start()

    def process_csv(self, file_path):
        """Procesa la validación del CSV en un hilo separado."""
        self.results = validate_from_csv(file_path)
        self.display_results()

    def validate_manual(self):
        """Valida los correos ingresados manualmente."""
        emails = self.entry_manual.get().split(",")
        emails = [email.strip() for email in emails if email.strip()]
        
        if not emails:
            messagebox.showwarning("Entrada vacía", "Ingrese al menos un correo.")
            return

        self.result_text.insert(tk.END, "Validando correos manualmente...\n")
        threading.Thread(target=self.process_manual, args=(emails,)).start()

    def process_manual(self, emails):
        """Procesa la validación manual en un hilo separado."""
        self.results = validate_emails_in_batches(emails)
        self.display_results()

    def display_results(self):
        """Muestra los resultados en la interfaz."""
        self.result_text.delete("1.0", tk.END)  # Limpia el área de texto
        for email, is_valid, message in self.results:
            status = "Válido" if is_valid else "Inválido"
            self.result_text.insert(tk.END, f"{email}: {status} ({message})\n")

    def save_results(self):
        """Guarda los resultados en un archivo CSV."""
        if not self.results:
            messagebox.showwarning("Sin resultados", "No hay resultados para guardar.")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if save_path:
            save_results_to_csv(self.results, save_path)

# --- Inicialización del programa ---
if __name__ == "__main__":
    root = tk.Tk()
    app = EmailValidatorApp(root)
    root.mainloop()

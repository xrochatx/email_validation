# email_validation

[![CI](https://github.com/xrochatx/email_validation/actions/workflows/ci.yml/badge.svg)](https://github.com/xrochatx/email_validation/actions/workflows/ci.yml)

Sistema en Python para validar direcciones de correo electrónico desde consola o mediante una interfaz gráfica de escritorio.

El proyecto está pensado para portafolio público: prioriza claridad, separación de responsabilidades, validación reproducible y un enfoque prudente de seguridad.

## Propósito

Este sistema permite analizar listas de correos y clasificar cada entrada según tres niveles de verificación:

1. Validez sintáctica.
2. Existencia de registros MX en el dominio.
3. Verificación SMTP opcional, sujeta a restricciones de los servidores remotos.

La verificación SMTP no garantiza que un buzón exista de forma absoluta. Muchos proveedores la bloquean o responden de manera genérica, por lo que debe tratarse solo como una señal adicional.

## Arquitectura

El proyecto está separado en capas para mantenerlo mantenible y fácil de auditar:

- [email_validation_core.py](email_validation_core.py): lógica de validación, lectura de CSV y guardado de resultados.
- [ValidarCorreo.py](ValidarCorreo.py): interfaz de consola.
- [ConexionCorreo.py](ConexionCorreo.py): interfaz gráfica con Tkinter.
- [tests/](tests): pruebas unitarias del núcleo.
- [\.github/workflows/ci.yml](.github/workflows/ci.yml): integración continua con GitHub Actions.

## Requisitos

- Python 3.13 o superior.
- Dependencias listadas en [requirements.txt](requirements.txt).

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

### Consola interactiva

```bash
python ValidarCorreo.py
```

El modo interactivo ofrece tres opciones:

- Ingreso manual de correos.
- Lectura desde archivo CSV.
- Modo de prueba con datos predefinidos.

### Consola con argumentos

```bash
python ValidarCorreo.py --input correos.csv --output correos_resultados.csv
python ValidarCorreo.py --input correos.csv --smtp
python ValidarCorreo.py --test
```

Parámetros disponibles:

- --input: ruta del archivo CSV de entrada.
- --output: ruta del archivo CSV de salida.
- --smtp: activa la verificación SMTP opcional.
- --test: ejecuta un conjunto de correos de demostración.

### Interfaz gráfica

```bash
python ConexionCorreo.py
```

La interfaz permite:

- Cargar un archivo CSV.
- Escribir correos separados por comas.
- Activar o desactivar la verificación SMTP.
- Guardar resultados en CSV.

## Flujo del sistema

1. El sistema normaliza la entrada.
2. Valida la sintaxis del correo.
3. Comprueba la existencia de registros MX.
4. Opcionalmente consulta el servidor SMTP del dominio.
5. Genera resultados y, si se solicita, los exporta a CSV.

## Formato de entrada

El CSV de entrada toma la primera columna como dirección de correo.

Ejemplo:

```csv
Email
user@example.com
admin@company.com
```

## Formato de salida

El archivo generado incluye estas columnas:

- Email
- Estado
- Mensaje

## Seguridad y uso responsable

Este proyecto se diseñó con una postura conservadora de seguridad:

- No requiere credenciales, tokens ni claves API.
- No persiste datos sensibles fuera de los archivos CSV que el usuario proporciona o exporta.
- Las validaciones SMTP se ejecutan sobre dominios externos y pueden ser bloqueadas por políticas del servidor.
- Los resultados deben interpretarse como apoyo técnico, no como prueba definitiva de que un buzón exista o esté activo.

Recomendaciones de uso:

- Usa listas de correos obtenidas con consentimiento o con base legal válida.
- Evita exponer archivos de entrada o salida que contengan datos personales.
- No automatices consultas agresivas a servidores externos; respeta límites y políticas de uso.

## Pruebas

Para ejecutar las pruebas locales:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

## Integración continua

El repositorio incluye GitHub Actions para ejecutar las pruebas en cada push y pull request sobre main.

## Limitaciones conocidas

- La verificación SMTP puede devolver falsos negativos.
- Algunos dominios no publican MX de forma estándar o aplican políticas antiabuso.
- El análisis se limita a la primera columna del CSV.

## Licencia

No se ha definido una licencia pública en este repositorio. Si el proyecto va a ser distribuido, conviene añadir una licencia explícita.

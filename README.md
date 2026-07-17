# email_validation

[![CI](https://github.com/xrochatx/email_validation/actions/workflows/ci.yml/badge.svg)](https://github.com/xrochatx/email_validation/actions/workflows/ci.yml)

Proyecto en Python para validar correos desde consola o con interfaz gráfica.

## Funciones

- Validación sintáctica del correo.
- Verificación de registros MX.
- Verificación SMTP opcional.
- Lectura y guardado de resultados en CSV.

## Instalación

```bash
pip install -r requirements.txt
```

## Uso por consola

```bash
python ValidarCorreo.py
```

También puedes usar argumentos:

```bash
python ValidarCorreo.py --input correos.csv --output correos_resultados.csv
python ValidarCorreo.py --input correos.csv --smtp
python ValidarCorreo.py --test
```

## Uso con interfaz gráfica

```bash
python ConexionCorreo.py
```

## Notas

- La verificación SMTP puede fallar aunque el correo exista, porque muchos servidores bloquean este tipo de consultas.
- El archivo CSV toma la primera columna como correo.

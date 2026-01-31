# Explorador de Volatilidad

"""
Volatility explorer – prices vs. rolling-returns σ
"""

Una herramienta interactiva construida con Dash que permite explorar la volatilidad de cualquier activo financiero disponible en Yahoo Finance.

-----

## 💡 Propósito y Características

La finalidad de esta aplicación es ofrecer una visualización clara y personalizable de la volatilidad histórica de los activos. Mide la volatilidad de dos maneras clave:

  * **Desviación Estándar (Std Dev):** Mide la dispersión de los retornos de un activo. Una desviación alta indica mayor volatilidad.
  * **Rango Intercuartil (IQR):** Mide la diferencia entre el 75% y 25% de los retornos. Es una medida robusta que es menos sensible a valores extremos (outliers).

Puedes personalizar la ventana de tiempo móvil y el rango de fechas para analizar cómo la volatilidad de un activo cambia con el tiempo.

-----

## 🛠️ Tecnologías Utilizadas

Este proyecto fue construido con las siguientes tecnologías:

  * **[Python](https://www.python.org/)**: Lenguaje de programación principal.
  * **[Dash](https://plotly.com/dash/)**: Framework para construir aplicaciones web analíticas sin necesidad de JavaScript.
  * **[Plotly](https://plotly.com/python/)**: Biblioteca de visualización de datos utilizada por Dash.
  * **[Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/)**: Componentes de Dash que implementan el popular framework CSS Bootstrap.
  * **[Pandas](https://pandas.pydata.org/)**: Para la manipulación y análisis de datos.
  * **[yfinance](https://pypi.org/project/yfinance/)**: Para descargar datos históricos de Yahoo Finance de manera confiable.

-----

## Demo

Les dejo la demo en render en la capa gratuita para que vean el funcionamiento

[Volatility Explorer](https://volatility-explorer.onrender.com/)

-----

## 🏃 ¿Cómo Correrlo en Local?

Para ejecutar esta aplicación en tu máquina local, sigue estos pasos:

1.  Clona el repositorio:

    ```bash
    git clone https://github.com/davichuder/volatility_explorer.git
    cd volatility_explorer
    ```

2.  Instala las dependencias:

    ```bash
    pip install -r requirements.txt
    ```

    (Asegúrate de tener un archivo `requirements.txt` con todas las librerías del proyecto).

3.  Corre el archivo `app.py`. Para esto, es necesario cambiar una línea en el código.

    Busca esta línea al final del archivo:

    ```python
    server = app.server
    ```

    Coméntala y agrega la línea para correr la aplicación localmente:

    ```python
    # server = app.server
    if __name__ == '__main__':
        app.run(debug=True)
    ```

4.  Ejecuta la aplicación desde la terminal:

    ```bash
    python app.py
    ```

    Abre tu navegador y ve a `http://127.0.0.1:8050/`.

-----

## ☁️ Despliegue

La aplicación está desplegada en [Render](https://render.com/). Debido a las limitaciones de la capa gratuita, el rendimiento puede verse afectado con rangos de fechas muy amplios (se recomienda no seleccionar más de 1 año).

-----

## 🐛 Problemas Conocidos y Mejoras Futuras

  * **Rendimiento en Render:** El servicio gratuito de Render puede tardar en cargar datos y generar los gráficos, especialmente con rangos de fechas largos.
  * **Opciones de Medidas:** Se podría agregar más medidas de volatilidad o distribuciones de los retornos para un análisis más profundo.
  * **Optimización del Código:** La función `build_figure` se puede optimizar para reducir el tiempo de cálculo, especialmente para grandes cantidades de datos.

-----

## 🧑‍💻 Autor

  * **David Rolón**

-----

## 🌐 Enlaces

  * [**Mi Portfolio**](https://rolondavid.pythonanywhere.com/)
  * [**Mi Linkedin**](https://github.com/davichuder)

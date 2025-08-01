"""
Volatility explorer – prices vs. rolling-returns σ
"""

from datetime import datetime, timedelta
from time import time

import yfinance as yf

import pandas as pd
import plotly.graph_objects as go
import numpy as np
import dash
from dash import dcc, Input, Output, State, callback, no_update
from dash.html import Div, H2, Hr, Label, Strong, P
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from plotly.subplots import make_subplots

DEFAULT_WINDOW = 21
DEFAULT_TICKER = "SPY"
DEFAULT_END_DATE = datetime.now()
DEFAULT_START_DATE = DEFAULT_END_DATE - timedelta(days=365)


def fetch_data(ticker: str, start_date: str, end_date: str):
    """Fetch historical data for a given ticker."""
    data = yf.Ticker(ticker).history(start=start_date, end=end_date, interval="1d")[
        "Close"
    ]
    if data.empty:
        return None
    return data


def build_figure(ticker: str, prices, window: int) -> go.Figure:
    """Precio arriba + 4 σ abajo con eje X compartido."""
    start_time = time()

    # Retornos diarios
    rets = prices.pct_change().dropna()

    # Desviaciones sobre la ventana móvil
    window_std = rets.rolling(window).std()
    window_std_pos = rets.rolling(window).apply(
        lambda x: x[x > 0].std() if len(x[x > 0]) else np.nan
    )
    window_std_neg = rets.rolling(window).apply(
        lambda x: x[x < 0].std() if len(x[x < 0]) else np.nan
    )

    # Desviaciones acumuladas
    acum_std = rets.expanding().std()
    acum_std_pos = rets.expanding().apply(
        lambda x: x[x > 0].std() if len(x[x > 0]) else np.nan
    )
    acum_std_neg = rets.expanding().apply(
        lambda x: x[x < 0].std() if len(x[x < 0]) else np.nan
    )

    # Desviaciones globales
    global_std = rets.std()
    global_std_pos = rets[rets > 0].std()
    global_std_neg = rets[rets < 0].std()

    # IQR sobre ventana movil
    window_iqr = rets.rolling(window).quantile(0.75) - rets.rolling(window).quantile(
        0.25
    )
    window_iqr_pos = rets.rolling(window).apply(
        lambda x: (
            x[x > 0].quantile(0.75) - x[x > 0].quantile(0.25)
            if len(x[x > 0])
            else np.nan
        )
    )
    window_iqr_neg = rets.rolling(window).apply(
        lambda x: (
            x[x < 0].quantile(0.75) - x[x < 0].quantile(0.25)
            if len(x[x < 0])
            else np.nan
        )
    )

    # IQR acumuladas
    acum_iqr_all = rets.expanding().quantile(0.75) - rets.expanding().quantile(0.25)
    acum_iqr_pos = rets.expanding().apply(
        lambda x: (
            x[x > 0].quantile(0.75) - x[x > 0].quantile(0.25)
            if len(x[x > 0])
            else np.nan
        )
    )
    acum_iqr_neg = rets.expanding().apply(
        lambda x: (
            x[x < 0].quantile(0.75) - x[x < 0].quantile(0.25)
            if len(x[x < 0])
            else np.nan
        )
    )

    # IQR Globales
    global_iqr = rets.quantile(0.75) - rets.quantile(0.25)
    global_iqr_pos = rets[rets > 0].quantile(0.75) - rets[rets > 0].quantile(0.25)
    global_iqr_neg = rets[rets < 0].quantile(0.75) - rets[rets < 0].quantile(0.25)

    # DataFrame único para compartir eje
    df = pd.DataFrame(
        {
            "date": prices[1:].index,
            "price": prices[1:],
            "rets": rets,
            "window_std": window_std,
            "window_std_pos": window_std_pos,
            "window_std_neg": window_std_neg,
            "global_std": global_std,
            "global_std_pos": global_std_pos,
            "global_std_neg": global_std_neg,
            "acum_std": acum_std,
            "acum_std_pos": acum_std_pos,
            "acum_std_neg": acum_std_neg,
            "window_iqr": window_iqr,
            "window_iqr_pos": window_iqr_pos,
            "window_iqr_neg": window_iqr_neg,
            "global_iqr": global_iqr,
            "global_iqr_pos": global_iqr_pos,
            "global_iqr_neg": global_iqr_neg,
            "acum_iqr_all": acum_iqr_all,
            "acum_iqr_pos": acum_iqr_pos,
            "acum_iqr_neg": acum_iqr_neg,
        }
    )

    # Sub-plots con eje X compartido
    fig = make_subplots(
        rows=4,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=[
            f"**{ticker}** – Precio de Cierre",
            "Retornos Diarios",
            "Desviación Estándar (Volatilidad)",
            "Rango Intercuartil (IQR)",
        ],
        row_heights=[0.4, 0.4, 0.4, 0.4],
    )

    # Precio
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["price"],
            name="Precio de Cierre",
            legendgroup="price",
            legendgrouptitle_text="Precio",
            hovertemplate="Precio: %{y:.2f}<br>Fecha: %{x}<extra></extra>",
        ),
        row=1,
        col=1,
    )

    # Retornos
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["rets"],
            name="Retorno %",
            legendgroup="returns",
            legendgrouptitle_text="Retornos",
            hovertemplate="Retorno: %{y:.2f}%<br>Fecha: %{x}<extra></extra>",
        ),
        row=2,
        col=1,
    )

    # Desviaciones
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["window_std"],
            name=f"Std Todos (Ventana Móvil de {window} días)",
            legendgroup="std",
            legendgrouptitle_text="Desviación Estándar",
            hovertemplate="Std Todos: %{y:.4f}<br>Fecha: %{x}<extra></extra>",
        ),
        row=3,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["window_std_pos"],
            name=f"Std Positivos (Ventana Móvil de {window} días)",
            line={"dash": "dash"},
            legendgroup="std",
            hovertemplate="Std Positivos: %{y:.4f}<br>Fecha: %{x}<extra></extra>",
        ),
        row=3,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["window_std_neg"],
            name=f"Std Negativos (Ventana Móvil de {window} días)",
            line={"dash": "dash"},
            legendgroup="std",
            hovertemplate="Std Negativos: %{y:.4f}<br>Fecha: %{x}<extra></extra>",
        ),
        row=3,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["global_std"],
            name="Std Global",
            line={"dash": "dot"},
            legendgroup="std",
            hovertemplate="Std Global: %{y:.4f}<br>Fecha: %{x}<extra></extra>",
        ),
        row=3,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["global_std_pos"],
            name="Std Global Positivos",
            line={"dash": "dot"},
            legendgroup="std",
            hovertemplate="Std Global Positivos: %{y:.4f}<br>Fecha: %{x}<extra></extra>",
        ),
        row=3,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["global_std_neg"],
            name="Std Global Negativos",
            line={"dash": "dot"},
            legendgroup="std",
            hovertemplate="Std Global Negativos: %{y:.4f}<br>Fecha: %{x}<extra></extra>",
        ),
        row=3,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["acum_std"],
            name="Std Acumulada",
            line={"dash": "longdash"},
            legendgroup="std",
            hovertemplate="Std Acumulada: %{y:.4f}<br>Fecha: %{x}<extra></extra>",
        ),
        row=3,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["acum_std_pos"],
            name="Std Acumulada Positivos",
            line={"dash": "longdash"},
            legendgroup="std",
            hovertemplate="Std Acumulada Positivos: %{y:.4f}<br>Fecha: %{x}<extra></extra>",
        ),
        row=3,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["acum_std_neg"],
            name="Std Acumulada Negativos",
            line={"dash": "longdash"},
            legendgroup="std",
            hovertemplate="Std Acumulada Negativos: %{y:.4f}<br>Fecha: %{x}<extra></extra>",
        ),
        row=3,
        col=1,
    )
    # IQR
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["window_iqr"],
            name=f"IQR Todos (Ventana Móvil de {window} días)",
            line={"dash": "dot"},
            legendgroup="iqr",
            legendgrouptitle_text="IQR",
            hovertemplate="IQR Todos: %{y:.4f}<br>Fecha: %{x}<extra></extra>",
        ),
        row=4,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["window_iqr_pos"],
            name=f"IQR Positivos (Ventana Móvil de {window} días)",
            line={"dash": "dash"},
            legendgroup="iqr",
            hovertemplate="IQR Positivos: %{y:.4f}<br>Fecha: %{x}<extra></extra>",
        ),
        row=4,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["window_iqr_neg"],
            name=f"IQR Negativos (Ventana Móvil de {window} días)",
            line={"dash": "dash"},
            legendgroup="iqr",
            hovertemplate="IQR Negativos: %{y:.4f}<br>Fecha: %{x}<extra></extra>",
        ),
        row=4,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["global_iqr"],
            name="IQR Global",
            line={"dash": "dot"},
            legendgroup="iqr",
            hovertemplate="IQR Global: %{y:.4f}<br>Fecha: %{x}<extra></extra>",
        ),
        row=4,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["global_iqr_pos"],
            name="IQR Global Positivos",
            line={"dash": "dot"},
            legendgroup="iqr",
            hovertemplate="IQR Global Positivos: %{y:.4f}<br>Fecha: %{x}<extra></extra>",
        ),
        row=4,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["global_iqr_neg"],
            name="IQR Global Negativos",
            line={"dash": "dot"},
            legendgroup="iqr",
            hovertemplate="IQR Global Negativos: %{y:.4f}<br>Fecha: %{x}<extra></extra>",
        ),
        row=4,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["acum_iqr_all"],
            name="IQR Acumulado",
            line={"dash": "longdash"},
            legendgroup="iqr",
            hovertemplate="IQR Acumulado: %{y:.4f}<br>Fecha: %{x}<extra></extra>",
        ),
        row=4,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["acum_iqr_pos"],
            name="IQR Acumulado Positivos",
            line={"dash": "longdash"},
            legendgroup="iqr",
            hovertemplate="IQR Acumulado Positivos: %{y:.4f}<br>Fecha: %{x}<extra></extra>",
        ),
        row=4,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["acum_iqr_neg"],
            name="IQR Acumulado Negativos",
            line={"dash": "longdash"},
            legendgroup="iqr",
            hovertemplate="IQR Acumulado Negativos: %{y:.4f}<br>Fecha: %{x}<extra></extra>",
        ),
        row=4,
        col=1,
    )

    fig.update_layout(
        height=1000,
        title_text=f"Explorador de Volatilidad – {ticker} - Tiempo de cálculo: {time() - start_time:.2f} segundos",
        template="plotly_dark",
        # Estas son las líneas clave que necesitas agregar
        legend={
            "orientation": "v",  # Orientación vertical para la leyenda
            "yanchor": "top",
            "y": 0.99,
            "xanchor": "left",
            "x": 1.02,  # Mueve la leyenda a la derecha
            "groupclick": "togglegroup",  # Opcional: permite ocultar grupos enteros
        },
        margin={"r": 250},  # Agrega un margen derecho para que quepa la leyenda
    )

    fig.update_yaxes(title_text="Precio", row=1, col=1)
    fig.update_yaxes(title_text="Retornos", row=2, col=1)
    fig.update_yaxes(title_text="Desviación Estándar", row=3, col=1)
    fig.update_yaxes(title_text="Rango Intercuartil", row=4, col=1)

    return fig


# ---------- Dash ----------
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Volatility Explorer"

app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                H2(
                    "Explorador de Volatilidad", className="text-center my-4 text-light"
                ),
                width=12,
            )
        ),
        dbc.Row(
            dbc.Col(
                dbc.Collapse(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                P(
                                    "Esta herramienta te permite explorar la volatilidad de cualquier activo financiero (ticker) disponible en Yahoo Finance. La volatilidad se mide de dos maneras:",
                                    className="text-light",
                                ),
                                Div(
                                    [
                                        Strong("Desviación Estándar (Std Dev):"),
                                        " Mide qué tan dispersos están los retornos de un activo respecto a su promedio. Una desviación alta significa más volatilidad.",
                                    ],
                                    className="text-light",
                                ),
                                Div(
                                    [
                                        Strong("Rango Intercuartil (IQR):"),
                                        " Mide la diferencia entre el 75% y el 25% de los retornos. Es una forma robusta de medir la volatilidad que no se ve tan afectada por valores extremos (outliers).",
                                    ],
                                    className="text-light",
                                ),
                                P(
                                    "Puedes ajustar la ventana de tiempo y el rango de fechas para ver cómo cambia la volatilidad.",
                                    className="text-light mt-3",
                                ),
                                P(
                                    " Se recomienda no seleccionar mas de 1 año debido a las limitaciones de la capa gratuita de Render.",
                                    className="text-light mt-3",
                                ),
                            ]
                        ),
                        className="bg-dark text-light my-3",
                    ),
                    id="info-collapse",
                    is_open=True,
                )
            )
        ),
        dbc.Row(
            dbc.Col(
                dbc.Button(
                    "Mostrar/Ocultar Información",
                    id="info-button",
                    className="mb-3 w-100",
                    color="secondary",
                )
            )
        ),
        Hr(style={"borderColor": "#444"}),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                "Selección de Datos y Rango",
                                className="text-light bg-secondary",
                            ),
                            dbc.CardBody(
                                [
                                    Div(
                                        [
                                            Label(
                                                "Ticker",
                                                className="form-label text-light",
                                            ),
                                            dbc.Input(
                                                id="ticker",
                                                type="text",
                                                value=DEFAULT_TICKER,
                                                debounce=True,
                                                className="bg-dark text-light border-secondary",
                                                placeholder="Ejemplo: SPY, AAPL, BTC-USD",
                                            ),
                                            dbc.Tooltip(
                                                "Ingresa el símbolo de un activo financiero (ticker). Por ejemplo: SPY para el S&P 500.",
                                                target="ticker",
                                                placement="right",
                                            ),
                                        ],
                                        className="mb-3",
                                    ),
                                    Div(
                                        [
                                            Label(
                                                "Rango de Fechas Histórico",
                                                className="form-label text-light",
                                            ),
                                            dcc.DatePickerRange(
                                                id="date-picker",
                                                start_date=DEFAULT_START_DATE,
                                                end_date=DEFAULT_END_DATE,
                                                display_format="YYYY-MM-DD",
                                                className="bg-dark text-light border-secondary w-100",
                                                calendar_orientation="vertical",
                                                style={
                                                    "colorScheme": "dark"
                                                },  # Estilo para modo oscuro
                                            ),
                                            dbc.Tooltip(
                                                "Selecciona un rango de fechas para cargar los datos del ticker. El rango por defecto son los últimos 10 años.",
                                                target="date-picker",
                                                placement="right",
                                            ),
                                        ],
                                        className="mb-3",
                                    ),
                                    dbc.Button(
                                        "Cargar Datos",
                                        id="load",
                                        color="primary",
                                        className="mt-4 w-100",
                                    ),
                                    dbc.Tooltip(
                                        "Haz clic aquí para cargar los datos históricos del ticker y el rango de fechas que elegiste.",
                                        target="load",
                                        placement="right",
                                    ),
                                    Div(
                                        dcc.Loading(
                                            type="default",
                                            children=P(
                                                Strong(id="loading-prices"),
                                                className="text-center mt-2",
                                            ),
                                        ),
                                    ),
                                ]
                            ),
                        ],
                        className="bg-dark text-light h-100",
                    ),
                    md=6,
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                "Configuración de Cálculo",
                                className="text-light bg-secondary",
                            ),
                            dbc.CardBody(
                                [
                                    Div(
                                        [
                                            Label(
                                                "Ventana Móvil (días)",
                                                className="form-label text-light",
                                            ),
                                            dbc.Input(
                                                id="window",
                                                type="number",
                                                value=DEFAULT_WINDOW,
                                                debounce=True,
                                                min=1,
                                                className="bg-dark text-light border-secondary",
                                            ),
                                            dbc.Tooltip(
                                                "Ingresa el número de días para la ventana móvil. Ej. 21 días es un mes de trading (aprox. 252 días hábiles en un año).",
                                                target="window",
                                                placement="right",
                                            ),
                                            Div(
                                                "La ventana móvil no puede ser más grande que el número de días cargados.",
                                                className="form-text text-muted",
                                            ),
                                        ],
                                        className="mb-3",
                                    ),
                                    dbc.Button(
                                        "Calcular Volatilidad",
                                        id="calculate",
                                        color="success",
                                        className="mt-4 w-100",
                                        disabled=True,
                                    ),
                                    dbc.Tooltip(
                                        "Haz clic aquí para calcular y mostrar los gráficos de volatilidad con la ventana elegida.",
                                        target="calculate",
                                        placement="right",
                                    ),
                                    Div(
                                        dcc.Loading(
                                            type="default",
                                            children=P(
                                                Strong(id="loading-calculate"),
                                                className="text-center mt-2",
                                            ),
                                        ),
                                    ),
                                ]
                            ),
                        ],
                        className="bg-dark text-light h-100",
                    ),
                    md=6,
                ),
            ],
            className="mb-4",
        ),
        Hr(style={"borderColor": "#444"}),
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        dcc.Loading(
                            id="full-loading",
                            type="default",
                            children=[
                                dcc.Graph(
                                    id="loading-graph",
                                    config={"responsive": True},
                                    figure=go.Figure(
                                        layout={
                                            "paper_bgcolor": "#222",
                                            "plot_bgcolor": "#222",
                                        }
                                    ),
                                )
                            ],
                        )
                    ),
                    className="bg-dark text-light",
                )
            ),
        ),
        dcc.Store(id="last_data", storage_type="memory"),
        dcc.Store(id="last_window", storage_type="memory"),
        dcc.Store(id="prices", storage_type="memory"),
        dcc.Store(id="last_ticker_calculate", storage_type="memory"),
    ],
    fluid=True,
    className="bg-dark text-light",
    style={"padding": "20px"},
)


# Callback para mostrar/ocultar la información
@callback(
    Output("info-collapse", "is_open"),
    [Input("info-button", "n_clicks")],
    [State("info-collapse", "is_open")],
)
def toggle_info_collapse(n, is_open):
    """Toggle the info collapse."""
    if n:
        return not is_open
    return is_open


# Callback para actualizar los datos
@callback(
    Output("last_data", "data"),
    Output("prices", "data"),
    Output("loading-prices", "children"),
    Output("calculate", "disabled"),
    Input("load", "n_clicks"),
    State("last_data", "data"),
    State("ticker", "value"),
    State("date-picker", "start_date"),
    State("date-picker", "end_date"),
)
def update_last_data(n, last_data, ticker, start_date, end_date):
    """Actualiza los valores de los últimos inputs."""
    if not n:
        raise PreventUpdate

    ticker_clean = ticker.upper().strip() if ticker else ""

    if not ticker_clean:
        return no_update, no_update, "Error: Por favor, ingresa un ticker válido.", True

    title = f"Ticker: {ticker_clean}, Fecha de Inicio: {start_date}, Fecha de Fin: {end_date}."

    if (
        last_data
        and last_data.get("ticker") == ticker_clean
        and last_data.get("start_date") == start_date
        and last_data.get("end_date") == end_date
    ):
        return no_update, no_update, f"Los datos ya están cargados.\n{title}", False

    start = start_date.split("T")[0]
    end = end_date.split("T")[0]

    updated_last_data = {
        "ticker": ticker_clean,
        "start_date": start,
        "end_date": end,
    }

    updated_prices = fetch_data(ticker_clean, start, end)

    if updated_prices is None:
        return (
            updated_last_data,  # Actualizamos el last_data para evitar intentos repetidos
            None,  # Establecemos prices a None para indicar que falló la carga
            "Error al cargar datos. El ticker no es válido o no hay datos disponibles.",
            True,
        )

    updated_prices = {
        "values": updated_prices.values.tolist(),
        "index": updated_prices.index.tolist(),
    }
    return (
        updated_last_data,
        updated_prices,
        f"Datos cargados con éxito.\n{title}",
        False,
    )


# Callback para actualizar el gráfico
@callback(
    Output("last_window", "data"),
    Output("loading-graph", "figure"),
    Output("loading-calculate", "children"),
    Output("last_ticker_calculate", "data"),
    Input("calculate", "n_clicks"),
    State("window", "value"),
    State("last_data", "data"),
    State("prices", "data"),
    State("last_window", "data"),
    State("last_ticker_calculate", "data"),
)
def update_graph(n, window, last_data, prices, last_window, last_ticker_calculate):
    """Actualiza el gráfico con los datos de precios y la ventana."""
    if not n or not last_data or not prices:
        raise PreventUpdate

    # Validar y convertir la ventana a un entero para evitar el error de tipo
    if not window or not isinstance(window, (int, float)) or int(window) < 1:
        return (
            no_update,
            no_update,
            "Error: Por favor, introduce un número entero válido (mínimo 1) para la ventana.",
            no_update,
        )

    window_int = int(window)

    df_prices = pd.Series(
        prices["values"],
        index=pd.to_datetime(prices["index"], errors="coerce"),
        dtype=float,
    )

    if window_int > len(df_prices):
        return (
            no_update,
            no_update,
            f"Error: La ventana móvil ({window_int} días) no puede ser más grande que el número de días cargados ({len(df_prices)}).",
            no_update,
        )

    title = f"Ticker: {last_data['ticker']}, Fecha de Inicio: {last_data['start_date']}, Fecha de Fin: {last_data['end_date']}. Ventana: {window_int}."

    if window_int == last_window and last_ticker_calculate == last_data["ticker"]:
        return (
            no_update,
            no_update,
            f"El gráfico ya está actualizado.\n{title}",
            no_update,
        )

    return (
        window_int,
        build_figure(
            last_data["ticker"],
            df_prices,
            window_int,
        ),
        f"Gráfico actualizado con éxito.\n{title}",
        last_data["ticker"],
    )


server = app.server

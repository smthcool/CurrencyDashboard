from urllib.request import urlopen
import xmltodict
import pandas as pd
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from datetime import date

def get_usd(start, stop): #функция, принимающая начальную и конечную дату, возвращает курс доллара
    currency_url = f'https://www.cbr.ru/scripts/XML_dynamic.asp?date_req1={start}&date_req2={stop}&VAL_NM_RQ=R01235'
    currency_data = xmltodict.parse(urlopen(currency_url))
    currencies = []
    currencies_map = {}
    dt = []
    vl = []
    for currency in currency_data['ValCurs']['Record']:
        currencies.append(currency['Value'])
        currencies_map[currency['Value']] = currency['@Date']
        dt.append(currency['@Date'])
        vl.append(float(currency['Value'].replace(',','.')))
    df = pd.DataFrame(list(zip(dt, vl)), columns =['Date', 'Val'])
    return df['Date'], df['Val']

lst_usd = get_usd('01/01/2022', '01/05/2022') #для начальной загрузки графика доллара

def get_eur(start, stop): #функция, принимающая начальную и конечную дату, возвращает курс евро
    currency_url2 = f'https://www.cbr.ru/scripts/XML_dynamic.asp?date_req1={start}&date_req2={stop}&VAL_NM_RQ=R01239'
    currency_data2 = xmltodict.parse(urlopen(currency_url2))
    currencies2 = []
    currencies_map2 = {}
    dt2 = []
    vl2 = []
    for currency in currency_data2['ValCurs']['Record']:
        currencies2.append(currency['Value'])
        currencies_map2[currency['Value']] = currency['@Date']
        dt2.append(currency['@Date'])
        vl2.append(float(currency['Value'].replace(',','.')))
    df2 = pd.DataFrame(list(zip(dt2, vl2)), columns =['Date', 'Val'])
    return df2['Date'], df2['Val']
lst_eur = get_eur('01/01/2022', '01/05/2022') #для начальной загрузки графика евро

app = dash.Dash(__name__)
app.layout = html.Div([
    dcc.Graph( #график
        id='clientside-graph'
    ),
    dcc.Store(
        id='clientside-figure-store',
        data=[{
            'x': lst_usd[0],
            'y': lst_usd[1],
        }]
    ),
    'Период',
    dcc.Slider( #слайдер
        step=None,
        marks={
            1: 'Текущий год',
            2: '3 года',
            3: '5 лет',
            4: '10 лет',
            5: '20 лет'
        },
        value=1,
        id='clientside-graph-period'
    ),
    'Валюта',
    dcc.Dropdown(['USD', 'EUR'], 'USD', id='clientside-graph-currency'),#выпадающий список
    'Тип графика',
    dcc.RadioItems( #радио кнопки
        ['line', 'markers'],
        'line',
        id='clientside-graph-scale'
    ),
    dcc.DatePickerRange( #выбор даты
        id='my-date-picker-range',
        min_date_allowed=date(2000, 1, 1),
        max_date_allowed=date(2022, 5, 2),
        initial_visible_month=date(2022, 5, 2),
        end_date=date(2022, 5, 2)
    ),
    html.Div(id='output-container-date-picker-range')
])

@app.callback( #входные и выходные данные
    Output('clientside-figure-store', 'data'),
    Input('clientside-graph-scale', 'value'),
    Input('clientside-graph-currency', 'value'),
    Input('clientside-graph-period', 'value'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')
)

def update_currency(type, currency, period, start_dt, end_dt): #обновление графика на основе динамических параметров
    if start_dt is not None and end_dt is not None: #на случай, если дата установлена через выборщик дат
        start_date_obj = date.fromisoformat(start_dt)
        start_date_str = start_date_obj.strftime('%d/%m/%Y')
        end_date_obj = date.fromisoformat(end_dt)
        end_date_str = end_date_obj.strftime('%d/%m/%Y')
        if currency == 'USD':
            lsst = get_usd(start_date_str, end_date_str)
            return [{
                'x': lsst[0],
                'y': lsst[1],
                'mode': type #тип графика
            }]
        elif currency == 'EUR':
            lssst = get_eur(start_date_str, end_date_str)
            return [{
                'x': lssst[0],
                'y': lssst[1],
                'mode': type #тип графика
            }]
    else: #на случай, если не используем выборщик дат
        if currency == 'USD':
            #обрабатываем разные значения слайдера
            if period == 1:
                lsst = get_usd('01/01/2022', '01/05/2022')
            if period == 2:
                lsst = get_usd('01/05/2019', '01/05/2022')
            if period == 3:
                lsst = get_usd('01/05/2017', '01/05/2022')
            if period == 4:
                lsst = get_usd('01/05/2012', '01/05/2022')
            if period == 5:
                lsst = get_usd('01/05/2002', '01/05/2022')
            return [{
                'x': lsst[0],
                'y': lsst[1],
                'mode': type #тип графика
            }]
        elif currency == 'EUR':
            #обрабатываем разные значения слайдера
            if period == 1:
                lssst = get_eur('01/01/2022', '01/05/2022')
            if period == 2:
                lssst = get_eur('01/05/2019', '01/05/2022')
            if period == 3:
                lssst = get_eur('01/05/2017', '01/05/2022')
            if period == 4:
                lssst = get_eur('01/05/2012', '01/05/2022')
            if period == 5:
                lssst = get_eur('01/05/2002', '01/05/2022')
            return [{
                'x': lssst[0],
                'y': lssst[1],
                'mode': type
            }]
app.clientside_callback( #клиентский вызов для отрисовки графика после изменения параметров
    """
    function(data, scale) {
        return {
            'data': data,
            'layout': {
                 'yaxis': {'type': scale},
             }
        }
    }
    """,
    Output('clientside-graph', 'figure'),
    Input('clientside-figure-store', 'data')
)
if __name__ == '__main__':
    app.run_server(debug=True)






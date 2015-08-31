from flask import Flask, render_template, request, redirect
import flask
import requests
import datetime
import pandas as pd
import numpy as np

from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.templates import RESOURCES
from bokeh.util.string import encode_utf8

app = Flask(__name__)

colors = {
    'Black': '#000000',
    'Red': '#FF0000',
    'Green': '#00FF00',
    'Blue': '#00FF00'
}

dates = 0
closing_prices = 0

# stock ticker
st = ''

def getitem(obj, item, default):
    if item not in obj:
        return default
    else:
        return obj[item]

@app.route('/')
def main():
  return redirect('/index')

@app.route('/index')
def index():
  return render_template('index.html')

@app.route('/close_price_chart', methods=['POST'])
def close_price_chart():
    global st, dates, closing_prices

    # receiving data
    st = request.form['stock_ticker']

    today = datetime.datetime.now()
    end_date = today.strftime("%Y-%m-%d")
    month_ago = today - datetime.timedelta(days=30)
    start_date = month_ago.strftime("%Y-%m-%d")

    request_str = 'https://www.quandl.com/api/v3/datasets/WIKI/%s.json/?start_date=%s&end_date=%s' % (st,start_date,end_date)

    r = requests.get(request_str)
    response_json = r.json()
    col_names = response_json['dataset']['column_names']
    all_data = pd.DataFrame(response_json['dataset']['data'], columns=col_names)
    #all_data.set_index('Date', inplace=True)

    #all_data.Close

    # constructing plot
    color = 'Black'

    dates = np.array(all_data['Date'], dtype=np.datetime64)
    closing_prices = np.array(all_data['Close'])

    fig = figure(width=800, height=350,x_axis_type='datetime', title='%s closing prices for last 30 days' % st)
    fig.line(dates, closing_prices, line_width=2, color=color, alpha=0.2, legend='close')
    fig.xaxis.axis_label = 'Date'
    fig.yaxis.axis_label = 'Price'

    # Configure resources to include BokehJS inline in the document.
    plot_resources = RESOURCES.render(
        js_raw = INLINE.js_raw,
        css_raw = INLINE.css_raw,
        js_files = INLINE.js_files,
        css_files = INLINE.css_files
    )

    script, div = components(fig, INLINE)
    html = flask.render_template(
        'embed.html',
        plot_script = script, plot_div=div, plot_resources=plot_resources,
        color=color
    )
    return encode_utf8(html)

@app.route('/close_price_chart', methods=['GET'])
def polynomial():
    """ Very simple embeding of a polynomial chart """
    # Grab input arguments from the URL
    # This is automated by the button
    args = flask.request.args

    # Get all the form arguments in their url with defaults
    color = colors[getitem(args,'color','Black')]

    fig = figure(width=800, height=350,x_axis_type='datetime', title='%s closing prices for last 30 days' % st)
    fig.line(dates, closing_prices, line_width=2, color=color, alpha=0.2, legend='close')
    fig.xaxis.axis_label = 'Date'
    fig.yaxis.axis_label = 'Price'

    # Configure resources to include BokehJS inline in the document.
    plot_resources = RESOURCES.render(
        js_raw = INLINE.js_raw,
        css_raw = INLINE.css_raw,
        js_files = INLINE.js_files,
        css_files = INLINE.css_files
    )

    script, div = components(fig, INLINE)

    html = flask.render_template(
        'embed.html',
        plot_script = script, plot_div=div, plot_resources=plot_resources,
        color=color
    )
    return encode_utf8(html)

if __name__ == '__main__':
  app.run(port=33507, debug=True)
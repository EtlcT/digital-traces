from flask import Flask, render_template, request
from logging.config import dictConfig
import requests
import os
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)

from pytrends.request import TrendReq
import plotly
import plotly.express as px
import json

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})


# oAuth
VIEW_ID = "407503035"
credentials=os.getenv('GOOGLE_APPLICATION_CREDENTIALS')


app = Flask(__name__)


@app.route("/", methods=['GET','POST'])

def hello_world():
    ## insert google analytics tag to get insights
    prefix_google = """
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-QFMSBHD3XT"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-QFMSBHD3XT');
</script>
"""
## access number of visitors from the creation of our website
    ##instantiate the client to request google analytics
    client = BetaAnalyticsDataClient()

    request_api = RunReportRequest(
    property=f"properties/{VIEW_ID}",
    dimensions=[
        Dimension(name="landingPagePlusQueryString")
        ],
        metrics=[
            Metric(name="newUsers") ## specify that we want the number of visitors
        ],
        date_ranges=[DateRange(start_date="2023-09-01", end_date="today")], # from the publication until today
    )
    response = client.run_report(request_api) # get response drom google_analytics

    nbvisits = response.rows[0].metric_values[0].value  # access the value

    return  prefix_google + render_template('index.html', cookies=None, response_text=None, status_code=None, nbvisits=nbvisits)

@app.route('/logger/')
def logger():
  app.logger.info('This is an info message to test logs')

  return '<p>Log page</p>'

## displaying google cookies
@app.route('/google_request', methods=['GET','POST'])
def google_request():
    ## try to access google.com
    try:
        req = requests.get("https://www.google.com/")
        if req.status_code == 200 : ## if success
            google_cookies = req.cookies.get_dict() ## access cookies 
            return render_template('index.html', cookies=google_cookies, status_code=None, response_text=None, nbvisits=None) # add cookies to html
        else: ## if an error occured
            app.logger.error('Error while trying to access Google')
    except Exception as e: # inform user
        return str(e)
    
## accessing google_analytics
@app.route('/gAnalytics_request', methods=['GET'])
def gAnalytics_request():
    try:
        req2 = requests.get("https://analytics.google.com/analytics/web/#/p407503035/reports/reportinghub?params=_u..nav%3Dmaui")
        if req2.status_code == 200:
            return render_template('index.html', cookies=None , status_code=req2.status_code, response_text=req2.text, nbvisits=None)
        else:
            app.logger.error('Error while trying to access GAnalytics')
    except Exception as e:
        return str(e)

## access /gTrends
@app.route('/gTrends', methods=['GET','POST'])
def gTrends_request():
    pytrends = TrendReq(hl='en-US', tz=360) # initialize parameter value for trend request
    user_search = request.form.get('searchTrends').split() # access user request from html form
    pytrends.build_payload(kw_list=user_search, timeframe='today 3-m') # prepare request
    result = pytrends.interest_over_time() # request google trends
    total_interest = result[user_search].sum() # sum along column to get the total interest (for pie chart)
    fig_line = px.line(result, x=result.index, y=user_search, title='Interest during last 3 months') # creating line plot with plotly express
    line_graph_json = json.dumps(fig_line, cls=plotly.utils.PlotlyJSONEncoder) # convert plotly plot into json
    fig_pie = px.pie(result, values=total_interest, names=total_interest.index, title='% of requests during last 3 months') # creating pie chart with plotly express
    pie_graph_json = json.dumps(fig_pie, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('graph.html', line_graph_json=line_graph_json, pie_graph_json=pie_graph_json, user_search=user_search)
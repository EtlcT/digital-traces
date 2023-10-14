from flask import Flask, render_template
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
SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
SERVICE_ACCOUNT_FILE = 'service.json'
VIEW_ID = "407503035"

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'service.json'


app = Flask(__name__)


@app.route("/", methods=['GET','POST'])

def hello_world():
    
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
## to get number of visitors from the beginning :
    client = BetaAnalyticsDataClient()

    request_api = RunReportRequest(
    property=f"properties/{VIEW_ID}",
    dimensions=[
        Dimension(name="landingPagePlusQueryString")
        ],
        metrics=[
            Metric(name="newUsers")
        ],
        date_ranges=[DateRange(start_date="2023-09-01", end_date="today")],
    )
    response = client.run_report(request_api)

    nbvisits = response.rows[0].metric_values[0].value

    return  prefix_google + render_template('index.html', cookies=None, response_text=None, status_code=None, nbvisits=nbvisits)

@app.route('/logger/')
def logger():
  app.logger.info('This is an info message to test logs')

  return '<p>Log page</p>'

@app.route('/google_request', methods=['GET','POST'])
def google_request():
    try:
        req = requests.get("https://www.google.com/")
        if req.status_code == 200 :
            google_cookies = req.cookies.get_dict()
            return render_template('index.html', cookies=google_cookies, status_code=None, response_text=None, nbvisits=None)
        else:
            app.logger.error('Error while trying to access Google')
            return 'Failed to retrieve data from Google.'
    except Exception as e:
        return str(e)
    
@app.route('/gAnalytics_request', methods=['GET'])
def gAnalytics_request():
    try:
        req2 = requests.get("https://analytics.google.com/analytics/web/#/p407503035/reports/reportinghub?params=_u..nav%3Dmaui")
        if req2.status_code == 200:
            return render_template('index.html', cookies=None , status_code=req2.status_code, response_text=req2.text, nbvisits=None)
        else:
            app.logger.error('Error while trying to access GAnalytics')
            return 'Failed to retrieve data from GAnalytics.'
    except Exception as e:
        return str(e)
    
    
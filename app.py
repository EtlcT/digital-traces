from flask import Flask, render_template
from logging.config import dictConfig
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build

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
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
analytics = build('analyticsreporting', 'v4', credentials=credentials)


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
    response = analytics.reports().batchGet(
        body={
            'reportRequests': [
                {
                    'viewId': VIEW_ID,
                    'dateRanges': [{'startDate': '2023-09-01', 'endDate': 'today'}],
                    'metrics': [{'expression': 'ga:sessions'}]
                }
            ]
        }
    ).execute()

    nbvisits = response['reports'][0]['data']['totals'][0]['values'][0]

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
            return render_template('index.html', cookies=google_cookies, status_code=None, response_text=None)
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
            return render_template('index.html', cookies=None , status_code=req2.status_code, response_text=req2.text)
        else:
            app.logger.error('Error while trying to access GAnalytics')
            return 'Failed to retrieve data from GAnalytics.'
    except Exception as e:
        return str(e)
    
    
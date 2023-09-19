from flask import Flask


app = Flask(__name__)

@app.route("/")
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

    return prefix_google + "<p>Hello, World!</p>"
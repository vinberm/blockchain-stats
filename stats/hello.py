from flask import Flask
from report import BasicInfo
app = Flask(__name__)


@app.route('/')
def hello_world():
    base_url = "http://127.0.0.1:9888"
    info = BasicInfo(base_url)
    status = info.all_chain_status()
    if status is None:
        return 'Waiting for synchronizing to newest'
    return status.__str__()

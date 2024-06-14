# TODO: Python web server that serves as Paranoia dashboard

from flask import Flask, render_template
import datetime

app = Flask(__name__)

@app.route('/')
def index(): 
    
    # Key = display_name, Value = [ timestamp, summary, host/ip ]
    changes = { 

    }

    # Key = display_name, Value = [ ping_response | down, ports_open[:5], geo_loc, ip_info ]
    hosts = {

    }

    # Key = display_name, Value = [ request_response | down, vulns[:5], icann_info ]
    websites = {

    }

    return render_template("index.html", changes=changes, hosts=hosts, websites=websites)

if __name__ == "__main__": 
    app.run(debug=True)
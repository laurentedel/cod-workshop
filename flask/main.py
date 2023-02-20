import datetime
import sys
# sys.path.insert(0, '/home/shameed/.local/lib/python3.6/site-packages') --> (if you face issues accessing Python 3 packages post installation, add the path to python3 libraries as shown at left)
from flask import Flask, render_template, request, redirect
import os
import json
import phoenixdb
import phoenixdb.cursor

app = Flask(__name__)
app.template_folder = "template"

@app.route("/")
def index():
    return render_template("index.html",)

#--------------------------------------------------------
#-                     REQUESTDETAILS                     -
#- Retrieving the MSISDN submitted on the webpage           -
#--------------------------------------------------------
@app.route('/requestdetails', methods=['POST'])
def requestdetails():
    calling_msisdn = request.form["CALLING_MSISDN"]
    seven_days_ago = datetime.datetime.now() - datetime.timedelta(days=7)
    seven_days_ago_str = seven_days_ago.strftime("%Y-%m-%d %H:%M:%S")
   
    # connect to database (Update database_url, user, password - This database_url is phoenix url copied from COD DB, and followed by CDP Workload Credentials)
    database_url = "DATABASE_URL"
    conn = phoenixdb.connect(database_url, autocommit=True, user='WORKLOADUSER', password='WORKLOADPASSWORD')
    cur = conn.cursor()
    
    cur.execute(f"SELECT CALLING_MSISDN, CALL_TYPE, CALL_RESULT, COUNT(CALLING_MSISDN) FROM cdr.cdr WHERE CALLING_MSISDN = '{str(calling_msisdn)}' AND DATE_BEG < '{seven_days_ago_str}' AND CALL_TYPE = 'Voice' AND CALL_RESULT = 'SUCCESS' GROUP BY CALLING_MSISDN, CALL_TYPE, CALL_RESULT LIMIT 100 ")
    
    cur.execute(f"SELECT CALLING_MSISDN, CALL_TYPE, CALL_RESULT, COUNT(CALLING_MSISDN), SUM(DURATION), AVG(DURATION) FROM cdr.cdr WHERE CALLING_MSISDN = '{str(calling_msisdn)}' AND DATE_BEG < '{seven_days_ago_str}' AND CALL_TYPE = 'Voice' AND CALL_RESULT = 'SUCCESS' GROUP BY CALLING_MSISDN, CALL_TYPE, CALL_RESULT LIMIT 100")
    calls = cur.fetchall()
    
    cur.execute(f"SELECT CALLING_MSISDN, CALL_TYPE, CALL_RESULT, COUNT(CALLING_MSISDN) FROM cdr.cdr WHERE CALLING_MSISDN = '{str(calling_msisdn)}' AND DATE_BEG < '{seven_days_ago_str}' AND CALL_TYPE = 'SMS' AND CALL_RESULT = 'SUCCESS' GROUP BY CALLING_MSISDN, CALL_TYPE, CALL_RESULT LIMIT 100 ")
    sms = cur.fetchall()

    cur.execute(f"SELECT CALLING_MSISDN, CALL_TYPE, CALL_RESULT, AVG(DURATION) as avg_duration, SUM(DURATION) as total_duration FROM cdr.cdr WHERE CALLING_MSISDN = '{str(calling_msisdn)}' AND DATE_BEG < '{seven_days_ago_str}' AND CALL_TYPE = 'Voice' AND CALL_RESULT = 'SUCCESS' GROUP BY CALLING_MSISDN, CALL_TYPE, CALL_RESULT LIMIT 100")
    avg = cur.fetchall()

    cur.execute(f"SELECT called_msisdn, date_beg, date_end, duration, call_type, call_result FROM cdr.cdr WHERE CALLING_MSISDN = '{str(calling_msisdn)}' AND DATE_BEG < '{seven_days_ago_str}' ORDER BY call_type")
    results1 = cur.fetchall()

    # Rendering query results back to the webpage:
    conn.close()
    return render_template("index.html",calls=calls,sms=sms,avg=avg,results1=results1)
    #conn.close()
#--------------------------------------------------------
#-                          MAIN                        -
#--------------------------------------------------------

if __name__ == '__main__':
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print("ERROR: unable to run application:\n {str(e)}")
                                                             

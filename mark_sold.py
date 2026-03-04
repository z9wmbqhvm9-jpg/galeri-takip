import requests, json, sys
ad_no = "1301754916"
try:
    resp = requests.post("http://localhost:5000/api/mark-sold", json={"adNo": ad_no})
    print("Status:", resp.status_code)
    print("Response:", resp.text)
except Exception as e:
    print("Error:", e)
    sys.exit(1)

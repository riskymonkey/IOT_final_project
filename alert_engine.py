from flask import Flask, request
import requests
from config import OM2M_CSE_URL, HEADERS, THRESHOLD

app = Flask(__name__)

def setup_subscription():
    """設置溫度數據訂閱"""
    sub_data = {
        "m2m:sub": {
            "nu": ["http://localhost:5002/alert"],
            "nct": 2
        }
    }
    requests.post(
        f"{OM2M_CSE_URL}/TempSensor/data",
        json=sub_data,
        headers={**HEADERS, "Content-Type": "application/json;ty=23"}
    )

@app.route('/alert', methods=['POST'])
def handle_alert():
    """處理OM2M通知"""
    data = request.json["m2m:sgn"]["nev"]["rep"]["m2m:cin"]
    temperature = float(data["con"])
    
    if temperature > THRESHOLD:
        send_light_command("ON")
    else:
        send_light_command("OFF")
    return "", 204

def send_light_command(command):
    """發送燈泡控制命令"""
    cin_data = {
        "m2m:cin": {
            "con": command,
            "cnf": "text/plain"
        }
    }
    requests.post(
        f"{OM2M_CSE_URL}/LightActuator/command",
        json=cin_data,
        headers=HEADERS
    )

if __name__ == "__main__":
    setup_subscription()
    app.run(port=5002, debug=False)


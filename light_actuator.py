import threading
import time
import requests
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
light_status = False
current_temperature = 0.0

class LightActuator:
    def __init__(self, ae_name="LightActuator", threshold=30):
        self.ae_name = ae_name
        self.threshold = threshold
        self.cse_url = "http://127.0.0.1:8282/~/mn-cse/mn-name"
        self.create_ae()
        
    def create_ae(self):
        """註冊AE到OM2M平台"""
        # 註冊AE
        ae_data = {
            "m2m:ae": {
                "api": "Nlight.actuator",
                "rn": self.ae_name,
                "rr": True
            }
        }
        
        headers_ae = {
            'Content-Type': 'application/json;ty=2',
            'X-M2M-Origin': 'admin:admin'
        }
        
        try:
            response = requests.post(self.cse_url, json=ae_data, headers=headers_ae)
            if response.status_code == 201:
                print('燈泡AE註冊成功')
            elif response.status_code == 409:
                print('燈泡AE已存在')
            else:
                print(f'燈泡AE註冊失敗: {response.status_code}')
        except Exception as e:
            print(f'註冊AE時發生錯誤: {e}')
        
        # 創建狀態容器（用於回報燈泡狀態）
        container_data = {"m2m:cnt": {"rn": "status", "mni": 10}}
        headers_cnt = {
            'Content-Type': 'application/json;ty=3',
            'X-M2M-Origin': 'admin:admin'
        }
        
        try:
            response = requests.post(
                f"{self.cse_url}/{self.ae_name}", 
                json=container_data, 
                headers=headers_cnt
            )
            if response.status_code in [201, 409]:
                print('狀態容器創建成功')
        except Exception as e:
            print(f'創建容器時發生錯誤: {e}')
    
    def get_temperature_from_om2m(self):
        """從OM2M平台抓取最新溫度數據"""
        global current_temperature
        
        headers_get = {
            'X-M2M-Origin': 'admin:admin',
            'Accept': 'application/json'
        }
        
        try:
            # 獲取TempSensor的最新數據
            response = requests.get(
                f"{self.cse_url}/TempSensor/data/la",  # la = latest
                headers=headers_get
            )
            
            if response.status_code == 200:
                data = response.json()
                temp_str = data["m2m:cin"]["con"]
                current_temperature = float(temp_str)
                print(f"從OM2M獲取溫度: {current_temperature}°C")
                return current_temperature
            else:
                print(f"無法獲取溫度數據: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"獲取溫度時發生錯誤: {e}")
            return None
    
    def control_light(self, should_be_on):
        """控制燈泡開關並回報狀態到OM2M"""
        global light_status
        
        if light_status != should_be_on:
            light_status = should_be_on
            status_text = "ON" if should_be_on else "OFF"
            print(f"燈泡狀態變更為: {status_text}")
            
            # 回報狀態到OM2M
            self.report_status_to_om2m(status_text)
    
    def report_status_to_om2m(self, status):
        """將燈泡狀態回報到OM2M平台"""
        headers_cin = {
            'Content-Type': 'application/json;ty=4',
            'X-M2M-Origin': 'admin:admin'
        }
        
        cin_data = {
            "m2m:cin": {
                "con": status,
                "cnf": "text/plain"
            }
        }
        
        try:
            response = requests.post(
                f"{self.cse_url}/{self.ae_name}/status",
                json=cin_data,
                headers=headers_cin
            )
            if response.status_code == 201:
                print(f"狀態已回報到OM2M: {status}")
        except Exception as e:
            print(f"回報狀態時發生錯誤: {e}")
    
    def monitor_temperature(self):
        """持續監控溫度並自動控制燈泡"""
        while True:
            try:
                temperature = self.get_temperature_from_om2m()
                
                if temperature is not None:
                    # 根據溫度閾值自動控制燈泡
                    should_light_be_on = temperature > self.threshold
                    
                    if should_light_be_on and not light_status:
                        print(f"溫度 {temperature}°C 超過閾值 {self.threshold}°C，開啟燈泡")
                        self.control_light(True)
                    elif not should_light_be_on and light_status:
                        print(f"溫度 {temperature}°C 低於閾值 {self.threshold}°C，關閉燈泡")
                        self.control_light(False)
                
                time.sleep(5)  # 每5秒檢查一次
                
            except Exception as e:
                print(f"監控溫度時發生錯誤: {e}")
                time.sleep(5)

@app.route('/status')
def get_status():
    return jsonify({
        "light_status": "ON" if light_status else "OFF",
        "current_temperature": current_temperature,
        "threshold": actuator.threshold,
        "timestamp": time.time()
    })

@app.route('/set_threshold/<float:new_threshold>')
def set_threshold(new_threshold):
    actuator.threshold = new_threshold
    return jsonify({
        "message": f"閾值已設定為 {new_threshold}°C",
        "threshold": new_threshold
    })

def run_flask():
    """在單獨線程中運行Flask"""
    app.run(host='127.0.0.1', port=5001, debug=False)

def run_temperature_monitor(actuator):
    """在單獨線程中監控溫度"""
    actuator.monitor_temperature()

if __name__ == "__main__":
    # 創建燈泡執行器實例
    actuator = LightActuator(threshold=30)
    
    # 使用多線程同時運行Flask和溫度監控
    flask_thread = threading.Thread(target=run_flask)
    monitor_thread = threading.Thread(target=run_temperature_monitor, args=(actuator,))
    
    # 設為daemon線程
    flask_thread.daemon = True
    monitor_thread.daemon = True
    
    # 啟動線程
    flask_thread.start()
    monitor_thread.start()
    
    print("智慧燈泡執行器已啟動")
    print("功能:")
    print("- 自動從OM2M獲取溫度數據")
    print(f"- 溫度超過 {actuator.threshold}°C 時自動開啟")
    print("- Flask API: http://127.0.0.1:5001/status")
    print("- 設定閾值: http://127.0.0.1:5001/set_threshold/25")
    print("按Ctrl+C停止程式")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在停止燈泡執行器...")


import time
import random
import requests
from config import OM2M_CSE_URL

class TemperatureSensor:
    def __init__(self, ae_name="TempSensor"):
        self.ae_name = ae_name
        self.create_ae()
        
    def create_ae(self):
        """註冊AE到OM2M平台"""
        # 註冊AE
        ae_data = {
            "m2m:ae": {
                "api": "Ntemperature.sensor",
                "rn": self.ae_name,
                "rr": True
            }
        }
        
        headers_ae = {
            'Content-Type': 'application/json;ty=2',
            'X-M2M-Origin': 'admin:admin'
        }
        
        response = requests.post(OM2M_CSE_URL, json=ae_data, headers=headers_ae)
        if response.status_code == 201:
            print('AE註冊成功')
        elif response.status_code == 409:
            print('AE已存在')
        else:
            print(f'AE註冊失敗: {response.text}')
        
        # 創建數據容器
        container_data = {"m2m:cnt": {"rn": "data", "mni": 10}}
        headers_cnt = {
            'Content-Type': 'application/json;ty=3',  # ty=3代表容器
            'X-M2M-Origin': 'admin:admin'
        }
        
        response = requests.post(
            f"{OM2M_CSE_URL}/{self.ae_name}", 
            json=container_data, 
            headers=headers_cnt
        )
        if response.status_code == 201:
            print('容器創建成功')
        elif response.status_code == 409:
            print('容器已存在')
        else:
            print(f'容器創建失敗: {response.text}')
    
    def send_data(self):
        """隨機生成溫度數據並上傳"""
        headers_cin = {
            'Content-Type': 'application/json;ty=4',  # ty=4代表contentInstance
            'X-M2M-Origin': 'admin:admin'
        }
        
        while True:
            temp = round(random.uniform(20, 35), 1)
            cin_data = {
                "m2m:cin": {
                    "con": str(temp),
                    "cnf": "text/plain"
                }
            }
            
            response = requests.post(
                f"{OM2M_CSE_URL}/{self.ae_name}/data",
                json=cin_data,
                headers=headers_cin
            )
            
            if response.status_code == 201:
                print(f"溫度數據已發送: {temp}°C")
            else:
                print(f"數據發送失敗: {response.text}")
                
            time.sleep(5)

if __name__ == "__main__":
    sensor = TemperatureSensor()
    sensor.send_data()


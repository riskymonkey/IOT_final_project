import requests

def clear_temperature_history():
    cse_url = "http://127.0.0.1:8282/~/mn-cse/mn-name"
    headers = {
        'X-M2M-Origin': 'admin:admin',
        'Accept': 'application/json'
    }
    
    try:
        # 獲取data容器下的所有contentInstance
        response = requests.get(f"{cse_url}/TempSensor/data", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            children = data.get('m2m:cnt', {}).get('ch', [])
            print(f"找到 {len(children)} 個contentInstance")
            
            # 遍歷並刪除所有contentInstance
            for child in children:
                if child['nm'].startswith('cin_'):
                    delete_url = f"{cse_url}/TempSensor/data/{child['nm']}"
                    delete_response = requests.delete(delete_url, headers=headers)
                    if delete_response.status_code == 200:
                        print(f"已刪除: {child['nm']}")
                    else:
                        print(f"刪除失敗: {child['nm']} - {delete_response.status_code}")
        else:
            print(f"無法取得容器資料: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("錯誤: 無法連接到OM2M伺服器，請確認OM2M是否正在運行")

if __name__ == "__main__":
    clear_temperature_history()


# IOT_final_project
環境是用之前實驗的ovf檔:
~/Documents/org.eclipse.om2m/org.eclipse.om2m.site.in-cse/target/products/in-cse/linux/gtk/x86_64: sh start.sh
~/Documents/org.eclipse.om2m/org.eclipse.om2m.site.mn-cse/target/products/mn-cse/linux/gtk/x86_64: sh start.sh

本地端模擬溫度sensor，不斷上傳溫度到om2m，每隔5秒，就從om2m上抓取溫度資訊檢查是否超過閥值，若超過閥值，燈泡(前端網頁)則會亮起，若低於閥值，則會暗掉

python temperature_sensor.py
python light_actuator.py
cd templates -> python -m http.server 8000 -> http://127.0.0.1:8000/dashboard.html

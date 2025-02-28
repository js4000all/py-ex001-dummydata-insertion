from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# InfluxDBの設定
url = "http://influxdb:8086"
token = "hTug2JwvOCCp4tYVZiDgoyRIfFZP-bjWjJrKcVJTbiPvQREQ7jUch00CQvRkyzH8WObup1JtNyxTfmYryZA9WQ=="
org = "u1org"
bucket = "u1db"

# InfluxDBクライアントの初期化
def create_bucket():
    client = InfluxDBClient(url=url, token=token, org=org)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    # ダミーデータ投入ループ
    for i in range(1000):
        temperature = random.uniform(20.0, 30.0)  # 温度データ
        humidity = random.uniform(40.0, 60.0)     # 湿度データ

        point = Point("sensor_data") \
            .tag("sensor_name", f"sensor_{i % 10}") \
            .field("temperature", temperature) \
            .field("humidity", humidity) \
            .time(time.time_ns())

        write_api.write(bucket=bucket, record=point)
        print(f"Inserted: Temperature={temperature}, Humidity={humidity}")
        time.sleep(5)  # 1秒ごとにデータ投入

    client.close()


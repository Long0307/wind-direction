# __init__.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import pymysql
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import json
from matplotlib.colors import LinearSegmentedColormap
from math import radians, sin, cos, sqrt, atan2

import setting_script
import test_script

app = Flask(__name__)
CORS(app)


file_location = "C:/Users/phung/OneDrive/Desktop/prediction/"

# input 데이터 받아옴
param1 = "User Parameter.txt"
param2 = "Developer Parameter.txt"
param3 = "DB Parameter.txt"

user_setfile = open(file_location + param1, 'r')  # input 파일 위치
developer_setfile = open(file_location + param2, 'r')
DB_setfile = open(file_location + param3, 'r')

lines1 = user_setfile.readlines()
lines2 = developer_setfile.readlines()
lines3 = DB_setfile.readlines()

upper_left1 = [float(s) for s in lines1[0].rstrip().split(",")]  # 좌상단 위도,경도
lower_right1 = [float(s) for s in lines1[1].rstrip().split(",")]  # 우하단위도,경도
grid_size1 = int(lines1[2].rstrip())  # m 단위
start_time1 = lines1[3].rstrip()  # 년-월-일 시:분:초
sensor_method1 = int(lines1[4].rstrip())  # 센서 선택 방식(개수{0}, 반경{1})
sensor_count1 = int(lines1[5].rstrip())  # 데이터를 가져올 주변 센서 갯수 ex) 3개
sensor_radius1 = int(lines1[6].rstrip())
start_point1 = [float(s) for s in lines1[7].rstrip().split(",")]
prediction_start_time1 = lines1[8].rstrip()
m_before1 = int(lines1[9].rstrip())  # 대략적 몇 분 전 예측

interval1 = int(lines2[0].rstrip())  # 센서별 데이터 n개 모이면
sensor_num1 = int(lines2[1].rstrip())  # 마지막 센서 번호
interval_time1 = float(lines2[2].rstrip())  # 13.2초
normal_distribution1 = int(lines2[3].rstrip())  # 정규 분포 횟수
cluster_method1 = int(lines2[4].rstrip())  # 1: 클러스터링 o, 0: x

db_ip1 = lines3[0].rstrip()
db_port1 = int(lines3[1].rstrip())
db_user1 = lines3[2].rstrip()
db_password1 = lines3[3].rstrip()
db_name1 = lines3[4].rstrip()
table11 = lines3[5].rstrip()  # 센서 DB
table21 = lines3[6].rstrip()  # 격자 DB
table31 = lines3[7].rstrip()  # 예측 DB

upper_left, lower_right, grid_size, start_time, sensor_method, sensor_count, sensor_radius, start_point, prediction_start_time, m_before = [], [], [], [], [], [], [], [], [], []
interval, sensor_num, interval_time, normal_distribution, cluster_method = [], [], [], [], []
db_ip, db_port, db_user, db_password, db_name, table1, table2, table3 = [], [], [], [], [], [], [], []

upper_left.append(upper_left1)
lower_right.append(lower_right1)
grid_size.append(grid_size1)
start_time.append(start_time1)
sensor_method.append(sensor_method1)
sensor_count.append(sensor_count1)
sensor_radius.append(sensor_radius1)
start_point.append(start_point1)
prediction_start_time.append(prediction_start_time1)
m_before.append(m_before1)

interval.append(interval1)
sensor_num.append(sensor_num1)
interval_time.append(interval_time1)
normal_distribution.append(normal_distribution1)
cluster_method.append(cluster_method1)

db_ip.append(db_ip1)
db_port.append(db_port1)
db_user.append(db_user1)
db_password.append(db_password1)
db_name.append(db_name1)
table1.append(table11)
table2.append(table21)
table3.append(table31)

setting_script.upper_left.append(upper_left[-1])
setting_script.lower_right.append(lower_right[-1])
setting_script.grid_size.append(grid_size[-1])
setting_script.start_time.append(start_time[-1])
setting_script.sensor_method.append(sensor_method[-1])
setting_script.sensor_count.append(sensor_count[-1])
setting_script.sensor_radius.append(sensor_radius[-1])
setting_script.prediction_start_time.append(prediction_start_time[-1])
setting_script.m_before.append(m_before[-1])
setting_script.interval.append(interval[-1])
setting_script.sensor_num.append(sensor_num[-1])
setting_script.interval_time.append(interval_time[-1])
setting_script.normal_distribution.append(normal_distribution[-1])
setting_script.cluster_method.append(cluster_method[-1])
setting_script.db_ip.append(db_ip[-1])
setting_script.db_port.append(db_port[-1])
setting_script.db_user.append(db_user[-1])
setting_script.db_password.append(db_password[-1])
setting_script.db_name.append(db_name[-1])
setting_script.table1.append(table1[-1])
setting_script.table2.append(table2[-1])
setting_script.table3.append(table3[-1])


@app.route('/run_flask')
def run_python_code():
    result = test_script.return_variable()  # 여기에 파이썬 코드 함수 실행
    # return jsonify(result=result)  # 결과를 JSON 형태로 반환 - 변수 하나
    # return jsonify({"result": result})
    return '플라스크 정상작동 확인'

# Long check
@app.route('/sensor_grid', methods=['GET', 'POST'])
def sensor_grid():
    try:
        con = pymysql.connect(host=db_ip[-1], port=db_port[-1], user=db_user[-1], password=db_password[-1],
                              db=db_name[-1], charset='utf8')

        query1 = """
           SELECT * FROM sensor_grid
         """

        data1 = pd.read_sql_query(query1, con)
        con.close()

        lat_list = [row['lat'] for _, row in data1.iterrows()]

        result = {
            "01lat_list": lat_list,
        }

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'})


@app.route('/setting_code', methods=['POST'])
def setting_code():
    result = setting_script.return_setting()  # 여기에 파이썬 코드 함수 실행
    return jsonify(result)


@app.route('/setting_grid_code', methods=['POST'])
def setting_grid_code():
    result = setting_script.draw_grid()
    return jsonify(result)


@app.route('/windpath_predict_code', methods=['POST'])
def windpath_predict_code():
    data = request.get_json()
    predictDateTime = data['predictDateTime']
    predictCoordinates = data['predictCoordinates']
    result = setting_script.windpath_predict(predictDateTime, predictCoordinates)
    return jsonify(result)

@app.route('/wind_speed_direction', methods=['POST'])
def wind_speed_direction():
    data = request.get_json()
    predictDateTime = data['predictDateTime']

    result = setting_script.speed_direction(predictDateTime)
    return jsonify(result)


@app.route('/get_sensor_data1', methods=['GET', 'POST'])
def get_sensor_data1():
    try:
        con = pymysql.connect(host=db_ip[-1], port=db_port[-1], user=db_user[-1], password=db_password[-1],
                              db=db_name[-1], charset='utf8')
        query1 = """
            SELECT lat
            FROM (
                SELECT DISTINCT ROUND(lower_left_lat, 10) AS lat FROM sensor_grid
                UNION
                SELECT DISTINCT ROUND(upper_right_lat, 10) AS lat FROM sensor_grid
            ) AS Combined
            ORDER BY lat ASC;
         """
        query2 = """
            SELECT lot
            FROM (
                SELECT DISTINCT ROUND(lower_left_lot, 10) AS lot FROM sensor_grid
                UNION
                SELECT DISTINCT ROUND(upper_right_lot, 10) AS lot FROM sensor_grid
            ) AS Combined
            ORDER BY lot ASC;
        """
        data1 = pd.read_sql_query(query1, con)
        data2 = pd.read_sql_query(query2, con)
        con.close()

        lat_list = [row['lat'] for _, row in data1.iterrows()]
        lot_list = [row['lot'] for _, row in data2.iterrows()]

        result = {
            "01lat_list": lat_list,
            "02lot_list": lot_list,
        }

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'})


@app.route('/get_sensor_data2', methods=['GET', 'POST'])
def get_sensor_data2():
    try:
        con = pymysql.connect(host=db_ip[-1], port=db_port[-1], user=db_user[-1], password=db_password[-1],
                              db=db_name[-1], charset='utf8')
        query = "SELECT COUNT(*) as grid_num FROM sensor_grid"
        data = pd.read_sql_query(query, con)
        con.close()

        result = int(data['grid_num'][0])

        result2 = {"01grid_num": result}
        return jsonify(result2)
    except Exception as e:
        print(e)
        return jsonify({'error': 'Internal Server Error'})


@app.route('/get_sensor_data3', methods=['GET', 'POST'])
def get_sensor_data3():
    try:
        con = pymysql.connect(host=db_ip[-1], port=db_port[-1], user=db_user[-1], password=db_password[-1],
                              db=db_name[-1], charset='utf8')
        query = "SELECT * FROM sensor_grid order by grid_num asc"
        data = pd.read_sql_query(query, con)
        con.close()

        grid_num = [row[0] for _, row in data.iterrows()]
        gen_time = [row[1] for _, row in data.iterrows()]
        upper_left_lot = [row[2] for _, row in data.iterrows()]
        upper_left_lat = [row[3] for _, row in data.iterrows()]
        upper_right_lot = [row[4] for _, row in data.iterrows()]
        upper_right_lat = [row[5] for _, row in data.iterrows()]
        lower_right_lot = [row[6] for _, row in data.iterrows()]
        lower_right_lat = [row[7] for _, row in data.iterrows()]
        lower_left_lot = [row[8] for _, row in data.iterrows()]
        lower_left_lat = [row[9] for _, row in data.iterrows()]
        center_lot = [row[10] for _, row in data.iterrows()]
        center_lat = [row[11] for _, row in data.iterrows()]
        section = [row[12] for _, row in data.iterrows()]

        result = {
            "01grid_num": grid_num,
            "02gen_time": gen_time,
            "03upper_left_lot": upper_left_lot,
            "04upper_left_lat": upper_left_lat,
            "05upper_right_lot": upper_right_lot,
            "06upper_right_lat": upper_right_lat,
            "07lower_right_lot": lower_right_lot,
            "08lower_right_lat": lower_right_lat,
            "09lower_left_lot": lower_left_lot,
            "10lower_left_lat": lower_left_lat,
            "11center_lot": center_lot,
            "12center_lat": center_lat,
            "13section": section,
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'})


@app.route('/get_cmap_data1', methods=['GET', 'POST'])
def get_cmap_data1():
    try:
        con = pymysql.connect(host=db_ip[-1], port=db_port[-1], user=db_user[-1], password=db_password[-1],
                              db=db_name[-1], charset='utf8')
        query = f"SELECT MAX(t_n) as max_t FROM '{table3[-1]}'"
        data = pd.read_sql_query(query, con)
        con.close()

        result = data['max_t'][0]

        result2 = {"01max_t": result}
        return jsonify(result2)
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'})


@app.route('/get_cmap_data2', methods=['POST'])
def get_cmap_data2():
    data = request.get_json()
    n1 = int(data["predict_t_n"])
    id1 = int(data["exist_id"])

    try:
        con = pymysql.connect(host=db_ip[-1], port=db_port[-1], user=db_user[-1], password=db_password[-1],
                              db=db_name[-1], charset='utf8')
        query = f"SELECT * FROM `{table3[-1]}` WHERE `t_n` = {n1} AND id = {id1} order by normal_num DESC"
        data2 = pd.read_sql_query(query, con)
        con.close()

        grid_num = [row[0] for _, row in data2.iterrows()]
        normal_num = [row[1] for _, row in data2.iterrows()]
        date = [row[2] for _, row in data2.iterrows()]
        t_n = [row[3] for _, row in data2.iterrows()]
        id2 = [row[4] for _, row in data2.iterrows()]

        result = {
            "01grid_num": grid_num,
            "02normal_num": normal_num,
            "03date": date,
            "04t_n": t_n,
            "05id": id2,
        }

        return jsonify(result)
    except Exception as e:
        print(e)
        return jsonify({'error': 'Internal Server Error'})


@app.route('/get_estimate_data1', methods=['POST'])
def get_estimate_data1():
    data = request.get_json()
    grid_date = str(data["grid_date"])
    try:
        con = pymysql.connect(host=db_ip[-1], port=db_port[-1], user=db_user[-1], password=db_password[-1],
                              db=db_name[-1], charset='utf8')
        # SELECT * FROM `estimate_grid_sensor_data` WHERE `date` BETWEEN DATE_SUB('2023-04-11 11:26:57', INTERVAL 5 SECOND) AND DATE_ADD('2023-04-11 11:26:57', INTERVAL 5 SECOND) order by m_name asc
        query = f"SELECT * FROM `{table2[-1]}` WHERE `date` BETWEEN DATE_SUB('{grid_date}', INTERVAL 5 SECOND) AND DATE_ADD('{grid_date}', INTERVAL 5 SECOND) order by m_name asc"
        # query = f"SELECT * FROM `estimate_grid_sensor_data_test` WHERE `date` BETWEEN DATE_SUB('{grid_date}', INTERVAL 5 SECOND) AND DATE_ADD('{grid_date}', INTERVAL 5 SECOND) order by m_name asc"
        data = pd.read_sql_query(query, con)
        con.close()

        m_id = [row[0] for _, row in data.iterrows()]
        m_name = [row[1] for _, row in data.iterrows()]
        center_lot = [row[2] for _, row in data.iterrows()]
        center_lat = [row[3] for _, row in data.iterrows()]
        wd = [row[4] for _, row in data.iterrows()]
        ws = [row[5] for _, row in data.iterrows()]
        vec_x = [row[6] for _, row in data.iterrows()]
        vec_y = [row[7] for _, row in data.iterrows()]
        date = [row[8] for _, row in data.iterrows()]

        result = {
            "01m_id": m_id,
            "02m_name": m_name,
            "03center_lot": center_lot,
            "04center_lat": center_lat,
            "05wd": wd,
            "06ws": ws,
            "07vec_x": vec_x,
            "08vec_y": vec_y,
            "09date": date,
        }

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'})


@app.route('/get_colormap', methods=['POST'])
def get_colormap():
    data = request.get_json()
    p_grid_num1 = data["p_grid_num1"]
    p_normal_num1 = data["p_normal_num1"]

    try:
        cmap1 = plt.cm.rainbow  # jet  # 사용할 cmap 선택
        max_num = normal_distribution[-1] # max(p_normal_num1)
        # norm = colors.Normalize(vmin=0, vmax=normal_distribution[-1])

        color_list = []
        for i in range(len(p_grid_num1)):
            num = p_grid_num1[i]
            color_index = p_grid_num1.index(num)
            color_num = p_normal_num1[color_index]
            normalized_color_num = 0.25 + (color_num / max_num) * 0.75
            color_values = colors.rgb2hex(cmap1(normalized_color_num))
            color_list.append(color_values)

        result = {
            "01color_list": color_list,
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'})


@app.route('/get_sensor_location', methods=['POST'])
def get_sensor_location():
    try:
        con = pymysql.connect(host=db_ip[-1], port=db_port[-1], user=db_user[-1], password=db_password[-1],
                              db=db_name[-1], charset='utf8')
        query = f"""
            WITH RankedData AS (
                SELECT 
                    m_name, 
                    lat,
                    lot,
                    ROW_NUMBER() OVER(PARTITION BY m_name ORDER BY m_date DESC) as rnk
                FROM 
                    `{table1[-1]}`
                WHERE 
                    m_date BETWEEN (SELECT MAX(m_date) - INTERVAL 10 MINUTE FROM `{table1[-1]}`) 
                            AND (SELECT MAX(m_date) FROM `{table1[-1]}`)
            )

            SELECT m_name, lat, lot
            FROM RankedData
            WHERE rnk = 1
        """
        data = pd.read_sql_query(query, con)
        data["m_name"] = data["m_name"].str.extract('(\d+)').astype(int)

        sensor_name = [row[0] for _, row in data.iterrows()]
        sensor_lat = [row[1] for _, row in data.iterrows()]
        sensor_lot = [row[2] for _, row in data.iterrows()]
        con.close()

        result = {
            "01sensor_name": sensor_name,
            "02sensor_lat": sensor_lat,
            "03sensor_lot": sensor_lot,
        }
        # print(sensor_name)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'})


@app.route('/get_exist_dateTime', methods=['POST'])
def get_exist_dateTime():
    data1 = request.get_json()
    predictDateTime = data1["predictDateTime"]

    # print(predictDateTime)
    try:
        con = pymysql.connect(host=db_ip[-1], port=db_port[-1], user=db_user[-1], password=db_password[-1],
                              db=db_name[-1], charset='utf8')
        m = get_m()
        # print(f"m: {m}, p_time: {m}")

        query = f"""
            SELECT 
                EXISTS(
                    SELECT 1 FROM `{table2[-1]}` WHERE date >= '{predictDateTime}'
                ) as exist_after,
                
                EXISTS(
                    SELECT 1 FROM `{table2[-1]}` WHERE date < DATE_SUB('{predictDateTime}', INTERVAL {m + 2} MINUTE)
                ) as exist_before;
        """

        print(query)
        
        data = pd.read_sql_query(query, con)
        con.close()

        exist_dateTime = int(data["exist_after"][0])
        exist_before = int(data["exist_before"][0])
        # print(exist_before)

        result = {
            "01existDateTime": exist_dateTime,
            "02existBefore": exist_before,
        }

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'})


def get_m():
    m = (m_before[-1] * 60) // (interval_time[-1] * interval[-1])
    return m


@app.route('/get_first_cmap', methods=['POST'])
def get_first_cmap():
    try:
        con = pymysql.connect(host=db_ip[-1], port=db_port[-1], user=db_user[-1], password=db_password[-1],
                              db=db_name[-1], charset='utf8')
        query = f"""
            WITH MaxID AS (
                SELECT MAX(id) as max_id FROM `{table3[-1]}`
            ),
            
            MaxTn AS (
                SELECT MAX(t_n) as max_tn
                FROM `{table3[-1]}`
                WHERE id IN (SELECT max_id FROM MaxID)
            ),
            
            RankedRows AS (
                SELECT *, 
                       ROW_NUMBER() OVER(PARTITION BY t_n ORDER BY normal_num DESC, grid_num ASC) as row_num
                FROM `{table3[-1]}`
                WHERE id IN (SELECT max_id FROM MaxID) AND t_n BETWEEN 0 AND (SELECT max_tn FROM MaxTn)
            )
            
            SELECT *
            FROM RankedRows
            WHERE row_num = 1
        """

        query2 = f"""
                WITH MaxID AS (
                    SELECT MAX(id) as max_id FROM `{table3[-1]}`
                )
            
                SELECT MAX(t_n) as max_tn
                FROM `{table3[-1]}`
                WHERE id IN (SELECT max_id FROM MaxID)"""

        print(query2)

        data = pd.read_sql_query(query, con)

        

        con.close()

        print(data)

        first_grid_num = [row[0] for _, row in data.iterrows()]
        first_normal_num = [row[1] for _, row in data.iterrows()]
        first_date = [row[2] for _, row in data.iterrows()]
        first_t_n = [row[3] for _, row in data.iterrows()]
        first_id = [row[4] for _, row in data.iterrows()]

      

        result = {
            "01first_grid_num": first_grid_num,
            "02first_normal_num": first_normal_num,
            "03first_date": first_date,
            "04first_t_n": first_t_n,
            "05first_id": first_id,
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': 'Internal Server Error'})


@app.route('/get_predict_line', methods=['POST'])
def get_predict_line():
    data1 = request.get_json()
    d_date = data1["d_date"]
    d_grid_num = data1["d_grid_num"]

    try:
        con = pymysql.connect(host=db_ip[-1], port=db_port[-1], user=db_user[-1], password=db_password[-1],
                              db=db_name[-1],
                              charset='utf8')
        m = get_m()
        # print(f"m: {m}, p_time: {m}")

        query = f"""
            SELECT center_lot, center_lat 
            FROM `{table2[-1]}`
            WHERE date = '{d_date}' AND m_name = {d_grid_num}
        """
        data = pd.read_sql_query(query, con)
        con.close()

        center_lat = data["center_lat"][0]
        center_lot = data["center_lot"][0]

        result = {
            "01center_lat": center_lat,
            "02center_lot": center_lot,
        }

        # print("result: ",result)

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'})


@app.route('/edit_settings', methods=['POST'])
def edit_settings():
    data1 = request.get_json()
    sensor_method.append(data1["sensor_method"])
    sensor_count.append(data1["sensor_count"])
    sensor_radius.append(data1["sensor_radius"])
    normal_distribution.append(data1["normal_distribution"])
    m_before.append(data1["n_minute"])
    cluster_method.append(data1["cluster_method"])

    try:
        setting_script.upper_left.append(upper_left[-1])
        setting_script.lower_right.append(lower_right[-1])
        setting_script.grid_size.append(grid_size[-1])
        setting_script.start_time.append(start_time[-1])
        setting_script.sensor_method.append(sensor_method[-1])
        setting_script.sensor_count.append(sensor_count[-1])
        setting_script.sensor_radius.append(sensor_radius[-1])
        setting_script.prediction_start_time.append(prediction_start_time[-1])
        setting_script.m_before.append(m_before[-1])
        setting_script.interval.append(interval[-1])
        setting_script.sensor_num.append(sensor_num[-1])
        setting_script.interval_time.append(interval_time[-1])
        setting_script.normal_distribution.append(normal_distribution[-1])
        setting_script.cluster_method.append(cluster_method[-1])
        setting_script.db_ip.append(db_ip[-1])
        setting_script.db_port.append(db_port[-1])
        setting_script.db_user.append(db_user[-1])
        setting_script.db_password.append(db_password[-1])
        setting_script.db_name.append(db_name[-1])
        setting_script.table1.append(table1[-1])
        setting_script.table2.append(table2[-1])
        setting_script.table3.append(table3[-1])

        result = {
            "01result": 0
        }

        # print("-- normal_distribution: ", normal_distribution[-1])
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'})

# Long code calculate_virtual_sensor
# @app.route('/calculate_vitual_sensor', methods=['POST'])
# def calculate_vitual_sensor():
#     data = request.get_json()
#     formatted_data = json.dumps(data, indent=4)
#     for ele in data['data']['NearestPoint3']:
#         print("in ra ở đây: ", ele)
#     # get windspeed and windirection at that time
#     try:
#         con = pymysql.connect(host=db_ip[-1], port=db_port[-1], user=db_user[-1], password=db_password[-1],
#                               db=db_name[-1],
#                               charset='utf8')
#         m = get_m()
#         # print(f"m: {m}, p_time: {m}")

#         query = f"""
#             SELECT winddirection, windspeed
#             FROM raw_data
#             WHERE m_date = '{d_date}' AND m_name = {d_grid_num}
#         """
#         data = pd.read_sql_query(query, con)
#         con.close()

#         center_lat = data["center_lat"][0]
#         center_lot = data["center_lot"][0]

#         result = {
#             "01center_lat": center_lat,
#             "02center_lot": center_lot,
#         }

#         return jsonify(result)
#     except Exception as e:
#         return jsonify({'error': 'Internal Server Error'})

    # return jsonify(data)

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # Bán kính trái đất đơn vị kilometer

    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance

@app.route('/calculate_vitual_sensor', methods=['POST'])
def calculate_vitual_sensor():
    try:
        data = request.get_json()
        
        # Lấy thông tin điểm được chọn
        chosen_lng = data["data"]["choosingPoint"]["lngPoint"]
        chosen_lat = data["data"]["choosingPoint"]["latPoint"]

        # Lấy thông tin các nút cảm biến gần nhất
        sensor_nodes = data["data"]["NearestPoint3"]

        # Tính tốc độ gió tại điểm được chọn dựa trên thông tin các nút cảm biến
        total_distance = 0
        total_wind_speed = 0

        for node in sensor_nodes:
            node_lng = node["lng"]
            node_lat = node["lat"]

            distance = calculate_distance(chosen_lat, chosen_lng, node_lat, node_lng)
            total_distance += distance
            total_wind_speed += 1 / distance  # Giả định đơn vị tốc độ gió ở mỗi node là 1/distance

        # Tính tốc độ gió trung bình dựa trên các nút cảm biến
        average_wind_speed = total_wind_speed / total_distance

        result = {
            "average_wind_speed": average_wind_speed
        }

        print(result)
        return jsonify(result)  # Trả về kết quả tốc độ gió trung bình dưới dạng JSON
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'})
    

if __name__ == '__main__':
    print("**** 확인")
    app.run(debug=True,host='0.0.0.0', port=5001)

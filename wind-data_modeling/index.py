import random
import math
import pandas as pd
import scipy as sp
import scipy.stats
from pyproj import Transformer
import pymysql

import folium
from folium import plugins
from selenium import webdriver

import time
import warnings

pd.options.mode.chained_assignment = None  # Disable warning display. Can be removed

warnings.filterwarnings("ignore")  # Disable warning display. Can be removed

# Contain target gps location [lat, lot]
target_location = {1: {'lat': 35.542925, 'lot': 129.254590}, 2: {'lat': 35.542978, 'lot': 129.255347},
                   3: {'lat': 35.542912, 'lot': 129.255888}, 4: {'lat': 35.545618, 'lot': 129.254853},
                   5: {'lat': 35.543165, 'lot': 129.256811}, 6: {'lat': 35.544776, 'lot': 129.256055},
                   7: {'lat': 35.543331, 'lot': 129.257444}, 8: {'lat': 35.543519, 'lot': 129.257718},
                   9: {'lat': 35.543536, 'lot': 129.254547}, 10: {'lat': 35.543685, 'lot': 129.255121},
                   11: {'lat': 35.543209, 'lot': 129.255749}, 12: {'lat': 35.543244, 'lot': 129.256232},
                   13: {'lat': 35.546483, 'lot': 129.255921}, 14: {'lat': 35.543414, 'lot': 129.257036},
                   15: {'lat': 35.543523, 'lot': 129.257364}, 16: {'lat': 35.543667, 'lot': 129.257712},
                   17: {'lat': 35.544418, 'lot': 129.254386}, 18: {'lat': 35.544213, 'lot': 129.255078},
                   19: {'lat': 35.544318, 'lot': 129.255588}, 20: {'lat': 35.544431, 'lot': 129.256049},
                   21: {'lat': 35.544392, 'lot': 129.256645}, 22: {'lat': 35.544209, 'lot': 129.257047},
                   23: {'lat': 35.544078, 'lot': 129.257509}, 24: {'lat': 35.544148, 'lot': 129.257836},
                   25: {'lat': 35.544776, 'lot': 129.254628}, 26: {'lat': 35.544894, 'lot': 129.255025},
                   27: {'lat': 35.544972, 'lot': 129.255422}, 28: {'lat': 35.544885, 'lot': 129.255990},
                   29: {'lat': 35.544859, 'lot': 129.256709}, 30: {'lat': 35.544876, 'lot': 129.257074},
                   31: {'lat': 35.544890, 'lot': 129.257433}, 32: {'lat': 35.544951, 'lot': 129.257702},
                   33: {'lat': 35.545536, 'lot': 129.254708}, 34: {'lat': 35.545300, 'lot': 129.254783},
                   35: {'lat': 35.545435, 'lot': 129.255143}, 36: {'lat': 35.545295, 'lot': 129.255486},
                   37: {'lat': 35.545330, 'lot': 129.256666}, 38: {'lat': 35.545343, 'lot': 129.257085},
                   39: {'lat': 35.545352, 'lot': 129.257471}, 40: {'lat': 35.545618, 'lot': 129.257187}}


def folium_geo(t, i, c):  # t: 시각화 그룹, i: index, c: color
    tmp = df1[df1['seconds'] == s_list[i]]
    for i in range(len(tmp)):
        tmp = tmp.reset_index(drop=True)  # index 초기화
        speed = tmp.loc[i, 'windspeed']  # 속도 가져옴
        if speed < 1:  # 속도 1미만 제외
            continue
        direction = tmp.loc[i, 'winddirection']  # 방향 가져옴
        longitude = tmp.loc[i, 'lot']  # y
        latitude = tmp.loc[i, 'lat']  # x

        x = latitude + math.cos(math.pi / 180 * direction) * 0.0004
        y = longitude + math.sin(math.pi / 180 * direction) * 0.0004

        line_list = [[latitude, longitude], [x, y]]
        folium.CircleMarker(location=[latitude, longitude], color=c, radius=3).add_to(t)
        folium.PolyLine(locations=line_list, color=c, weight=5).add_to(t)


# 지도에 하나씩 그리는 함수 (속도 고려)
def folium_geo_sx(t, i, c):
    tmp = df2[df2['seconds'] == s_list[i]]
    for i in range(len(tmp)):
        tmp = tmp.reset_index(drop=True)  # index 초기화
        direction = tmp.loc[i, 'winddirection']  # 방향 가져옴
        speed = tmp.loc[i, 'windspeed']  # 속도 가져옴
        longitude = tmp.loc[i, 'lot']  # y
        latitude = tmp.loc[i, 'lat']  # x

        x = latitude + math.cos(math.pi / 180 * direction) * (0.0004 * speed)
        y = longitude + math.sin(math.pi / 180 * direction) * (0.0004 * speed)

        print("x = ", x)
        print("y = ", y)

        line_list = [[latitude, longitude], [x, y]]
        folium.CircleMarker(location=[latitude, longitude], color=c, radius=3).add_to(t)
        folium.PolyLine(locations=line_list, color=c, weight=2).add_to(t)


def folium_geo_predict_line(tp, line, color):
    folium.PolyLine(locations=line, weight=7, color=color).add_to(tp)
    folium.CircleMarker(line[0], radius=2, color='yellow').add_to(tp)
    folium.CircleMarker(line[1], radius=2, color='yellow').add_to(tp)


#
#
#


# Database connection config
db_ip = '127.0.0.1'
db_port = 3307
db_user = 'root'
db_password = ''
db_name = 'weather'

# CONFIG PARAMS
dateFrom = '2022-05-18'  # start tracking date, should be from 2022-05-15 ~ 2022-05-25
timeFrom = '13:00:00'   # start tracking time, any time in a day

START_TRACKING_SENSOR_ID = 29  # 1 ~ 40
NBO_DATA_SET_PER_PREDICTION = 20  # equal to the number of steps for wind path prediction
NBO_UPDATED_DATA_SET_PER_PREDICTION = 3  # 1, 2, 3, 4 ... this number will define the html display updated rate
                                         # update-rate = NBO_UPDATED_DATA_SET_PER_PREDICTION * interval (seconds)

mapFname = 'DB_snap_predict_program_speed_ver0708.html'
file_location = "C:/Users/phung/OneDrive/Desktop/wind-data_modeling/" + mapFname  # path to html file -> change it to your working directory
#
#
#

""" Find the m_id where we will start from """
# Get data from DataBase
# STEP 1: MySQL Connection
con = pymysql.connect(host=db_ip, port=db_port, user=db_user, password=db_password,
                      db=db_name, charset='utf8')  # 한글처리 (charset = 'utf8')

sql = "SELECT * FROM raw_data WHERE m_date  > STR_TO_DATE('" + dateFrom + " " + timeFrom + "', '%Y-%m-%d %H:%i:%s') LIMIT 1"

# STEP 2: MySQL Query By Pandas
data = pd.read_sql_query(sql, con)

# STEP 3: DB Disconnection
con.close()

if data.empty:
    print("No data to process")
    exit(-1)

# get the m_id of the first data row from 'dateFrom'
data_start_id = data.iloc[0]['m_id']

# 기본 설정
interval = 13.2  # 센서 interval
second = 300  # n초 이전까지 예측
choice_num = 3  # 예측에 사용되는 근접 센서 개수
weight = 0.1  # 시그마
normal_num = 100  # 정규분포 개수
NBO_RECORDS_PER_DATA_SET = 40  # equal to the number of sensors

# 저장할 딕셔너리
predict_dict = {}

# Start looping to process data from DB
previous_id = data_start_id
while 1:
    con = pymysql.connect(host=db_ip, port=db_port, user=db_user, password=db_password,
                          db=db_name, charset='utf8')  # 한글처리 (charset = 'utf8')

    sql = "SELECT * FROM raw_data WHERE m_id >= " + str(data_start_id) + " LIMIT " + str(
        2 * NBO_DATA_SET_PER_PREDICTION * NBO_RECORDS_PER_DATA_SET)

    data = pd.read_sql_query(sql, con)

    con.close()

    if data.empty:
        print("No data to process")
        exit(-1)

    # Convert name WTi to i
    for i in range(NBO_RECORDS_PER_DATA_SET + 1)[1:]:
        temp_str = "WT" + str(i)
        data['m_name'] = data['m_name'].replace(temp_str, i)

    # In this version, we assume that one of data WT1, WT2 or WT3 is always available in a data set
    # Therefore, we assume that a data set can be used if it contains WT1, WT2 or WT3
    # TODO: refine later
    while 1:
        temp_id = data.iloc[0]['m_name']
        if temp_id in [1, 2, 3]:  # if sensor name is 1, 2, or 3 we take this current data set
            break
        data.drop(data.head(1).index, inplace=True)  # 위의 조건에 해당 안 된 경우 마지막 행 제거

    # Process the data before executing wind path prediction algorithm
    seconds = []
    tmp = 0
    increased_flag = False
    last_id = 0
    for i in data['m_name']:
        if i < last_id:
            increased_flag = False
        if i in [1, 2, 3] and increased_flag is False:
            tmp += 1
            increased_flag = True
        last_id = i
        seconds.append(tmp)

    data['seconds'] = seconds

    # Get only NBO_DATA_SET_PER_PREDICTION set for prediction
    data.drop(data[data['seconds'] > NBO_DATA_SET_PER_PREDICTION].index, inplace=True)
    data = data.reset_index(drop=True)

    print("PREDICT INTERVAL: " + str(data.iloc[0]['m_date']) + " ~ " + str(data.iloc[-1]['m_date']))
    print("START ID: " + str(data_start_id) + ".   DIFF: " + str(data_start_id - previous_id))

    # Update the start m_id for the next data prediction round
    for index, row in data.iterrows():
        if row['seconds'] > NBO_UPDATED_DATA_SET_PER_PREDICTION:
            # Update the m_id for the next data sets
            previous_id = data_start_id
            data_start_id = row['m_id']
            break

    # 데이터 역순으로
    reverse_data = data[::-1].reset_index(drop=True)

    df1 = reverse_data.copy()

    # 10개씩 들어감 확인
    df1.groupby('m_name').count()

    # 그룹 용 seconds 컬럼 추가
    s_list = list(set(df1['seconds']))
    s_list.sort()

    # 지도에 표시될 그룹 이름 만들기
    time_str = str(data.iloc[0]['m_date']) + " ~ " + str(data.iloc[-1]['m_date'])

    # 바람길 예측용 df
    df2 = reverse_data.copy()
    
    # print(df2)

    # 필요없는 컬럼 제거
    # df2 = df2.drop(['m_id', 'temperature', 'humidity'], axis=1)
    df2 = df2.drop(['m_id'], axis=1)
    df2['seconds'] = data['seconds']

    target = df2.iloc[df2[(df2['seconds'] == 1) & (df2['m_name'] == START_TRACKING_SENSOR_ID)].index].squeeze()

    if target.empty:
        # If the current data set missed the data of the target sensor, we need to create a dummy data for this target
        target = df2.head(1).copy()

        # Then update only the necessary information
        tl = target_location[START_TRACKING_SENSOR_ID]
        target.at[0, 'm_name'] = START_TRACKING_SENSOR_ID
        target.at[0, 'lat'] = tl['lat']
        target.at[0, 'lot'] = tl['lot']
        target.at[0, 'seconds'] = 1

        target = target.squeeze()

    target_df = pd.DataFrame(target).transpose()
    target_df = target_df.drop(['m_name', 'winddirection', 'windspeed', 'm_date'], axis=1)
    target_df = target_df[['seconds', 'lat', 'lot']]

    # 열 이름 변경하기 (seconds --> time)
    target_df = target_df.rename(columns={'seconds': 'time'})

    # 현재 초
    current_seconds = target['seconds']

    # display(target, target_df, current_seconds)

    data[data['windspeed'] != 0.0]['windspeed'].min()
    # speed 중 가장 작은 값 = 0.2

    # 좌표 설정
    epsg4326 = Transformer.from_crs("epsg:4326", "epsg:5179")  ## 지리 좌표계
    epsg5179 = Transformer.from_crs("epsg:5179", "epsg:4326")  ## 투영 좌표계

    # 시간 순 정렬
    sort_time_list = sorted(set(df2['seconds']))
    sort_time_list.append(len(sort_time_list) + 1)
    # print(sort_time_list)

    # 프로그램
    counts = NBO_DATA_SET_PER_PREDICTION  # second // interval
    for _ in range(int(counts)):
        location_point = epsg4326.transform(target['lat'], target['lot'])

        time_df = df2[df2['seconds'] == target['seconds']]

        df_list = time_df.values.tolist()  ## t시간의 타깃이 아닌 데이터  #convert to list bỏ target

        location = []
        for df in df_list:
            a, b = epsg4326.transform(df[4], df[5])
            df[3] = a
            df[4] = b
            location.append((a, b))

        length_list = [((abs(j[0] - location_point[0]) ** 2 + abs(j[1] - location_point[1]) ** 2) ** (1 / 2), i) for
                       i, j in enumerate(location)]  ## dist(s(t), Pk)
        length_list.sort(key=lambda x: x[0])

        choice_list = length_list[:choice_num]  ## Ns(타깃과의 길이, 인덱스) (추측)
        # print(choice_list)

        total_w = 0  ## W (추측)

        for i in choice_list:
            if i[0] == 0:
                temp = 1
            else:
                temp = i[0]
            total_w += 1 / temp

        total_vector_x = 0
        total_vector_y = 0  ## Vs(t) (추측)
        for j in choice_list:
            w = j[0]  ## j[0]: 타깃과의 길이 / j[1]: 인덱스
            speed = df_list[j[1]][2]
            if speed == 0: speed = 0.1  # speed가 0이라서 나는 오류 방지
            # direction = (abs(df_list[j[1]][1] - 360) + 90) % 360  # radian setting
            direction = df_list[j[1]][1]
            # print("direction = ", direction)
            vector_x = speed * (math.cos(math.pi * (direction / 180)))  # x
            vector_y = speed * (math.sin(math.pi * (direction / 180)))  # y  ## Vk(t)

            # print("vector_x = ", vector_x)

            # if j[0] == 0: temp = 1
            # else: temp = j[0]
            # total_w += 1/temp

            if j[0] < 10: distance_weight = 1
            if 10 <= j[0] < 20: distance_weight = 1 / 2
            if 20 <= j[0] < 30: distance_weight = 1 / 3
            if 30 <= j[0]: distance_weight = 1 / 4

            # total_vector_x += ((1/total_w)*(1/temp)) * vector_x
            # total_vector_y += ((1/total_w)*(1/temp)) * vector_y

            total_vector_x += distance_weight * vector_x
            total_vector_y += distance_weight * vector_y
            # total_vector_x += vector_x
            # total_vector_y += vector_y

        predict_location_point = (location_point[0] - (interval * total_vector_x),
                                  location_point[1] - (interval * total_vector_y))  # 경도, 위도 ## s(t-1) (추측)

        total_vector_distance = ((total_vector_x * interval) ** 2 + (total_vector_y * interval) ** 2) ** (1 / 2)

        print("predict_location_point = ", predict_location_point)
        # Vs(t)*T (추측)
        distance = total_vector_distance
        mu = [0, 0]
        mu = [predict_location_point[0], predict_location_point[1]]
        cov = [[weight * distance, 0], [0, weight * distance]]

        rv = sp.stats.multivariate_normal(mu, cov)
        X = rv.rvs(normal_num)  ## N(mu, sigma) (추측)

        # random_choice = random.choice(X)
        random_choice = mu
        latitude, longitude = epsg5179.transform(random_choice[0], random_choice[1])
        predict_dict[target['seconds']] = {'lot': longitude, 'lat': latitude}
        target['seconds'] = sort_time_list[target['seconds']]
        target['lot'] = longitude
        target['lat'] = latitude

        # print("target = ",target)

    lat = []
    long = []
    check_time = []  # time 추가 - 이 시간, 이 위치에서의 센서 측정값 있는지 확인위함
    for i, v in predict_dict.items():
        check_time.append(i)
        lat.append(v['lat'])
        long.append(v['lot'])
    predict = pd.DataFrame({'time': check_time, 'lat': lat, 'lot': long})

    predict = pd.concat([target_df, predict]).reset_index(drop=True)

    predict_list = predict.drop('time', axis=1).values.tolist()

    m = folium.Map(location=[35.544585, 129.256250], zoom_start=50)
    m.save(mapFname)

    driver = webdriver.Chrome()
    driver.set_window_size(1380, 1080)
    driver.get(file_location)

    # driver.maximize_window()

    c = ['brown', 'gray', 'darkcyan', 'olive', 'navy', 'purple', 'blue', 'green', 'orange', 'black']
    trace_time_point = df2.iloc[0]['m_date']
    draw_list = []
    fg2 = folium.FeatureGroup(name=time_str)
    m.add_child(fg2)
    t92 = plugins.FeatureGroupSubGroup(fg2, 'brown [' + str(trace_time_point) + ']' )
    m.add_child(t92)
    draw_list.append(t92)
    t82 = plugins.FeatureGroupSubGroup(fg2, 'gray [-' + str(round(interval, 1)) + 's]')
    m.add_child(t82)
    draw_list.append(t82)
    t72 = plugins.FeatureGroupSubGroup(fg2, 'darkcyan [-' + str(round(2*interval, 1)) + 's]')
    m.add_child(t72)
    draw_list.append(t72)
    t62 = plugins.FeatureGroupSubGroup(fg2, 'olive [-' + str(round(3*interval, 1)) + 's]')
    m.add_child(t62)
    draw_list.append(t62)
    t52 = plugins.FeatureGroupSubGroup(fg2, 'navy [-' + str(round(4*interval, 1)) + 's]')
    m.add_child(t52)
    draw_list.append(t52)
    t42 = plugins.FeatureGroupSubGroup(fg2, 'purple [-' + str(round(5*interval, 1)) + 's]')
    m.add_child(t42)
    draw_list.append(t42)
    t32 = plugins.FeatureGroupSubGroup(fg2, 'blue [-' + str(round(6*interval, 1)) + 's]')
    m.add_child(t32)
    draw_list.append(t32)
    t22 = plugins.FeatureGroupSubGroup(fg2, 'green [-' + str(round(7*interval, 1)) + 's]')
    m.add_child(t22)
    draw_list.append(t22)
    t12 = plugins.FeatureGroupSubGroup(fg2, 'orange [-' + str(round(8*interval, 1)) + 's]')
    m.add_child(t12)
    draw_list.append(t12)
    t02 = plugins.FeatureGroupSubGroup(fg2, 'black [-' + str(round(9*interval, 1)) + 's]')
    m.add_child(t02)
    draw_list.append(t02)

    # 그룹 이름 설정 (센서 이름_날짜 및 시간_300s(예측시간))
    group_str = "WT" + str(target['m_name']) + "_" + str(target['m_date']) + "_" + str(int(NBO_DATA_SET_PER_PREDICTION * interval)) + 'secs'

    fg3 = folium.FeatureGroup(name=group_str)
    m.add_child(fg3)
    tp = plugins.FeatureGroupSubGroup(fg3, 'predict')
    m.add_child(tp)
    folium.LayerControl(collapsed=False).add_to(m)

    # draw 10 wind vectors
    for i in range(len(draw_list)):
        folium_geo_sx(draw_list[i], i, c[i])

    m.save(mapFname)
    # driver.refresh()

    # draw predicted line
    folium.CircleMarker(predict_list[0], radius=6, color='red').add_to(tp)  # start point
    m.save(mapFname)

    for i in range(len(predict_list) - 1):
        predict_points = (predict_list[i], predict_list[i + 1])
        folium_geo_predict_line(tp, predict_points, color='darkviolet')
        m.save(mapFname)
        driver.refresh()

    time.sleep(NBO_UPDATED_DATA_SET_PER_PREDICTION * interval)

    driver.quit()

print("============== END =============")
exit(-1)

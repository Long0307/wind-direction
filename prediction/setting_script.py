# setting_script.py
import pymysql
import pandas as pd
import pyproj
import scipy as sp
import math
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings("ignore")
upper_left = [[127.456, 37.456]]
lower_right = [[127.789, 37.123]]
grid_size = [50]
start_time = ["2023-04-11 11:30:00"]
sensor_method = [1]
sensor_count = [3]
sensor_radius = [100]
start_point = [[129.567, 37.345]]
prediction_start_time = ["2023-04-11 11:30:00"]
m_before = [3]

interval = [5]
sensor_num = [8]
interval_time = [13.2]
normal_distribution = [100]
cluster_method = [1]

# db_ip = ["192.168.100.6"]
db_ip = ["127.0.0.1"]
db_port = [3307]
db_user = ["root"]
db_password = ["root"]
db_name = ["weather"]
table1 = ["raw_data"]
table2 = ["estimate_grid_sensor_data"]
table3 = ["cmap_grid_data"]


def return_setting():
    result = {
        "01upper_left": [upper_left[-1][1], upper_left[-1][0]],
        "02lower_right": [lower_right[-1][1], lower_right[-1][0]],
        "03grid_size": grid_size[-1],
        "04start_time": start_time[-1],
        "05sensor_method": sensor_method[-1],
        "06sensor_count": sensor_count[-1],
        "07sensor_radius": sensor_radius[-1],
        "08start_point": [start_point[-1][1], start_point[-1][0]],
        "09prediction_start_time": prediction_start_time[-1],
        "10interval": interval[-1],
        "11sensor_num": sensor_num[-1],
        "12interval_time": interval_time[-1],
        "13normal_distribution": normal_distribution[-1],
        "14cluster_method": cluster_method[-1],
        "15m_before": m_before[-1],
    }

    return result


def draw_grid():
    grid_table = 'sensor_grid'
    con = pymysql.connect(host=db_ip[-1], port=db_port[-1], user=db_user[-1], password=db_password[-1], db=db_name[-1], charset='utf8')
    sql1 = f"SELECT * FROM {grid_table} order by grid_num asc"
    sensor_grid = pd.read_sql_query(sql1, con).reset_index(drop=True)
    con.close()

    lot = sensor_grid['lower_left_lot'].drop_duplicates().tolist()
    lot.append(sensor_grid['upper_right_lot'].drop_duplicates().max())

    lat = sensor_grid['lower_left_lat'].drop_duplicates().tolist()
    lat.append(sensor_grid['upper_right_lat'].drop_duplicates().max())

    result = {
        "01lat": lat,
        "02lot": lot,
    }

    return result


def find_neighbors(cell, grid, input_cells):
    neighbors = []
    for dr, dc in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
        new_r, new_c = cell[0] + dr, cell[1] + dc
        if 0 <= new_r < len(grid) and 0 <= new_c < len(grid[0]) and grid[new_r][new_c] in input_cells:
            neighbors.append((new_r, new_c))
    return neighbors


def find_cluster(start, grid, input_cells):
    visited = set()
    queue = [start]
    cluster = []

    while queue:
        curr_r, curr_c = queue.pop(0)
        if (curr_r, curr_c) not in visited:
            visited.add((curr_r, curr_c))
            cluster.append(grid[curr_r][curr_c])
            neighbors = find_neighbors((curr_r, curr_c), grid, input_cells)
            queue.extend(neighbors)

    return sorted(cluster)


def speed_direction(predictDateTime):
    grid_tabel = 'sensor_grid'
    m = get_m()
    con = pymysql.connect(host=db_ip[-1], port=db_port[-1], user=db_user[-1], password=db_password[-1], db=db_name[-1], charset='utf8')
    sql1 = "SELECT * FROM " + grid_tabel
    sensor_grid = pd.read_sql_query(sql1, con).reset_index(drop=True)

    grid_num = len(sensor_grid)  # 280 #324
    dateTime = [predictDateTime]

    m_name = []
    center_lot = []
    center_lat = []
    wd = []
    ws = []

    for i in range(10):
        sql2 = "SELECT * FROM " + table2[-1] + " WHERE date <= STR_TO_DATE('" + dateTime[-1] + "', '%Y-%m-%d %H:%i:%s') order by m_id ASC LIMIT " + str(grid_num)
        data1 = pd.read_sql_query(sql2, con)  # .sort_values(by=['m_id'], ascending=True).reset_index(drop=True)
        time = interval[-1] * interval_time[-1] * m

        predictDateTime_obj = datetime.strptime(dateTime[-1], '%Y-%m-%d %H:%M:%S')
        new_predictDateTime_obj = predictDateTime_obj - timedelta(seconds=time)
        dateTime.append(new_predictDateTime_obj.strftime('%Y-%m-%d %H:%M:%S'))

        m_name.append(data1['m_name'].tolist())
        # print(f"m_name: {i} : {m_name[i]}")
        center_lot.append(data1['center_lot'].tolist())
        center_lat.append(data1['center_lat'].tolist())
        wd.append(data1['wd'].tolist())
        ws.append(data1['ws'].tolist())

    con.close()

    return_value = {
        "01m_name": m_name,
        "02center_lot": center_lot,
        "03center_lat": center_lat,
        "04wd": wd,
        "05ws": ws,
    }

    return return_value


# windpath_prediction here
def windpath_predict(predictDateTime, predictCoordinates):

    source_proj = pyproj.CRS('EPSG:4326')  # 위경도 좌표계 -> latitude and longitude coordinate system
    target_proj = pyproj.CRS('EPSG:5186')  # 미터 좌표계 -> metric coordinate system

    transformer_4326_5186 = pyproj.Transformer.from_crs(source_proj, target_proj, always_xy=True)  # 좌표계 변환 -> Coordinate system transformation
    transformer_5186_4326 = pyproj.Transformer.from_crs(target_proj, source_proj, always_xy=True)

    cmap_num_list = []
    data_list = []
    weight = 1  # 그리드 간격 50m, 풍속 4-5m/s 기준 정규분포 시그마 1 -> Normal distribution sigma 1 based on grid spacing of 50m and wind speed of 4-5m/s
    normal_num = normal_distribution[-1]  # 정규분포 개수: 100 -> Number of normal distributions: 100
    # normal_num = 100
    t = 10  # t-4
    prediction_start_time1 = predictDateTime  # prediction_start_time  # "2022-05-18 19:00:00"
    m = get_m()
    grid_tabel = 'sensor_grid'

    con = pymysql.connect(host=db_ip[-1], port=db_port[-1], user=db_user[-1], password=db_password[-1], db=db_name[-1], charset='utf8')
    sql1 = "SELECT * FROM " + grid_tabel
    sensor_grid = pd.read_sql_query(sql1, con).reset_index(drop=True)  # .sort_values(by=['m_id'], ascending=True).reset_index(drop=True)

    grid_num = len(sensor_grid)  # 280 #324
    # print("grid_num: ", grid_num)

    sql2 = "SELECT * FROM " + table2[-1] + " WHERE date <= STR_TO_DATE('" + prediction_start_time1 + "', '%Y-%m-%d %H:%i:%s') order by m_id ASC LIMIT " + str(grid_num + 1)
    dataA = pd.read_sql_query(sql2, con)  # .sort_values(by=['m_id'], ascending=True).reset_index(drop=True)

    table_sql = f"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '{db_name[-1]}' AND table_name = '{table3[-1]}'"
    table_exists = pd.read_sql_query(table_sql, con).iloc[0, 0]

    exist_id = 0

    if table_exists:
        id_sql = f"SELECT MAX(id) AS max_id FROM {table3[-1]}"
        sql_result = pd.read_sql_query(id_sql, con)
        max_id_value = sql_result['max_id'].iloc[0]
        if max_id_value is None:
            exist_id = 0
        else:
            exist_id = max_id_value + 1
    else:
        exist_id = 0

    con.close()

    if dataA.empty or sensor_grid.empty:
        # print("No data to process")
        exit(-1)

    # cmap용 정규분포 개수 확인 데이터프레임 생성
    normal_check = pd.DataFrame({
        # 'm_id': range(0, len(data3)),
        'grid_num': range(1, grid_num + 1),
        'normal_num': [0] * grid_num,
        'date': ['0000-00-00 00:00:00'] * grid_num,
        't_n': [0] * grid_num  # 몇 번째 루프
    })

    # 그리드 생성
    cluster_grid = []

    width = len(sensor_grid['lower_left_lot'].drop_duplicates())
    height = len(sensor_grid['lower_left_lat'].drop_duplicates())

    start = width * height - width + 1

    for row in range(height):
        if row % 2 == 0:
            cluster_grid.append(list(range(start, start + width)))
        else:
            cluster_grid.append(list(range(start + width - 1, start - 1, -1))[::-1])
        start -= width

    min_lot = sensor_grid['lower_left_lot'].drop_duplicates().min()
    min_lat = sensor_grid['lower_left_lat'].drop_duplicates().min()

    max_lot = sensor_grid['upper_right_lot'].drop_duplicates().max()
    max_lat = sensor_grid['upper_right_lat'].drop_duplicates().max()

    data_start_id2 = dataA.loc[dataA['m_name'] == 1].iloc[0]['m_id']

    lista = []
    listc = []

    #print(cluster_grid)

    for a in range(t):
        normal_check['t_n'] = a
        cmap_num_list.append(normal_check.copy())

        # '''
        con = pymysql.connect(host=db_ip[-1], port=db_port[-1], user=db_user[-1], password=db_password[-1], db=db_name[-1], charset='utf8')
        sql = "SELECT * FROM " + table2[-1] + " WHERE m_id >= " + str(data_start_id2) + " order by m_id ASC LIMIT " + str(grid_num)
        data3 = pd.read_sql_query(sql, con).sort_values(by=['m_id'], ascending=True).reset_index(drop=True)
        data_list.append(data3.copy())
        con.close()
        # '''

        if data3.empty:
            print("No data to process")
            exit(-1)
            # break
        else:
            print("----data connect----")
            # print(data_start_id2)
            data_start_id2 = data_start_id2 + (grid_num * m)

    for c in range(t):
        data3 = data_list[c]
        #print(data3)
        lista = listc
        listc = []
        out = 0
        gaussian_check = pd.DataFrame(0, index=range(1), columns=range(1, grid_num + 1))

        for a in range(normal_num):
            if (c == 0):  # t-1인 경우 정규 분포 모두 같은 위치에서 시작
                start_point1 = predictCoordinates  # start_point
            else:
                start_point1 = lista[a]

            # 각 그리드 중심 좌표
            lot = data3['center_lot'].drop_duplicates().to_list()
            lat = data3['center_lat'].drop_duplicates().to_list()

            if not lot or not lat:
                # print("Empty lot or lat sequence")
                break

            # 시작 위치에서 가장 가까운 그리드 중심 좌표 계산
            closest_point = (min(lot, key=lambda x: abs(x - start_point1[0])), min(lat, key=lambda x: abs(x - start_point1[1])))
            # print("closest_point: ", closest_point) # okk

            if closest_point[0] is None or closest_point[1] is None:
                print("No valid closest point found")
                break

            # 해당 그리드 중심 좌표에서의 데이터
            filtered_data = data3.loc[(data3['center_lot'] == closest_point[0]) & (data3['center_lat'] == closest_point[1])]

            grid_point = transformer_4326_5186.transform(closest_point[0], closest_point[1])
            location_point = transformer_4326_5186.transform(start_point1[0], start_point1[1])

            pre_dist = (abs(grid_point[0] - location_point[0]) ** 2 + abs(grid_point[1] - location_point[1]) ** 2) ** (1 / 2)

            # print(filtered_data)
            j = [filtered_data['m_name'].iloc[0], pre_dist]  # [122, 15.637063464939587] 122번 그리드, 바람길 추적 시작 위치와의 거리

            # print("풍속, 풍향 값 꺼내쓸 가장 가까운 그리드[번호, 거리(m)]:", j) -> print("Lưới gần nhất để lấy giá trị tốc độ và hướng gió [số, khoảng cách (m)]:", j)

            total_vector_x = 0
            total_vector_y = 0  ## Vs(t) (추측) 

            speed = float(data3.loc[data3['m_name'] == j[0]]['ws'].iloc[0])

            if speed == 0.0:
                speed = 0.1  # speed가 0이라서 나는 오류 방지

            direction = float(data3.loc[data3['m_name'] == j[0]]['wd'].iloc[0])

            vector_x = float(data3.loc[data3['m_name'] == j[0]]['vec_x'].iloc[
                                 0])  # speed * (math.sin(math.pi * (direction / 180)))  # x
            vector_y = float(data3.loc[data3['m_name'] == j[0]]['vec_y'].iloc[
                                 0])  # speed * (math.cos(math.pi * (direction / 180)))  # y  ## Vk(t)

            predict_location_point = ((location_point[0] - (interval_time[-1] * interval[-1] * m * vector_x)), (
                    location_point[1] - (interval_time[-1] * interval[-1] * m * vector_y)))  # ----------------------

            total_vector_distance = ((vector_x * interval_time[-1] * interval[-1] * m) ** 2 + (
                    vector_y * interval_time[-1] * interval[-1] * m) ** 2) ** (1 / 2)
            distance = total_vector_distance

            mu = [0, 0]
            mu = [predict_location_point[0], predict_location_point[1]]
            cov = [[weight * distance, 0], [0, weight * distance]]

            rv = sp.stats.multivariate_normal(mu, cov)
            X = rv.rvs(1)

            start_point2 = transformer_5186_4326.transform(X[0], X[1])  # 다음 t초 전 좌표 시작 위치
            listc.append(start_point2)
            # print("start_point2: ", start_point2)

            # start_point2이 어느 grid 칸에 포함되는 지 카운트
            if ((start_point2[0] > max_lot or start_point2[0] < min_lot) or (
                    start_point2[1] > max_lat or start_point2[1] < min_lat)):
                if (cluster_method[-1] == 1):
                    listc.remove(start_point2)

                # print("예측 좌표가 그리드 범위를 벗어남")
                out += 1
            else:
                # print("예측 좌표가 그리드 내에 위치함")
                longitude = start_point2[0]  # 경도
                latitude = start_point2[1]  # 위도

                # 경도와 위도의 범위를 확인하는 조건식을 벡터화된 방식으로 작성
                condition = (
                        (sensor_grid['upper_left_lot'] <= longitude) &
                        (sensor_grid['lower_right_lot'] >= longitude) &
                        (sensor_grid['upper_left_lat'] >= latitude) &
                        (sensor_grid['lower_right_lat'] <= latitude)
                )

                # 조건을 만족하는 행의 인덱스를 가져옴
                matching_index = condition[condition].index
                # 인덱스에 해당하는 열을 증가시킴
                gaussian_check.loc[0, matching_index + 1] += 1

        # 반 이상 그리드 넘어가면 멈춤
        if (out >= normal_num // 2):
            break

        gaussian_check = gaussian_check.loc[:, (gaussian_check != 0).any(axis=0)]
        gaussian_check = gaussian_check.T.reset_index(drop=False)
        gaussian_check.columns = ['grid_num', 'normal_num']
        # print(gaussian_check)

        normal_check1 = cmap_num_list[c]

        mask = gaussian_check['normal_num'] != 0
        grid_nums = gaussian_check.loc[mask, 'grid_num'].values
        normal_check1.loc[normal_check1['grid_num'].isin(grid_nums), 'normal_num'] += gaussian_check.loc[
            mask, 'normal_num'].values
        normal_check1 = normal_check1[normal_check1['normal_num'] != 0]
        normal_check1.loc[:, 'date'] = data_list[c].iloc[0]['date']  #

        cmap_num_list[c] = normal_check1.copy()

        if (cluster_method[-1] == 1):  # 비례 안 하는 버전도
            # clustering 후 grid 갯수에 비례하게 listc에 중심 좌표로 변경해서 넣어주기
            cmap = cmap_num_list[c]
            # print(cmap)
            input_cells = cmap['grid_num'].tolist()
            # print(c, " input_cells: ", input_cells)
            max_rows = cmap[cmap['normal_num'] == cmap['normal_num'].max()].head(1)
            start_cell = max_rows['grid_num'].values[0]

            # Find the start cell coordinates in the grid
            start_coordinates = None
            for i in range(len(cluster_grid)):
                for j in range(len(cluster_grid[i])):
                    if cluster_grid[i][j] == start_cell:
                        start_coordinates = (i, j)
                        break
                if start_coordinates:
                    break

            # Get the cluster starting from the start cell
            cluster = find_cluster(start_coordinates, cluster_grid, input_cells)
            # print(c, " cluster: ", cluster)

            cluster_rows = cmap[cmap['grid_num'].isin(cluster)]
            cluster_rows = cmap[cmap['grid_num'].isin(cluster)]

            remaining_sum = normal_num - cluster_rows['normal_num'].sum()
            df = cluster_rows

            # condition = cmap_num_list[c]['grid_num'].isin(cluster_rows['grid_num'])
            # normal_check1 = normal_check1[condition]

            if remaining_sum != 0:
                # 각 grid_num 별로 normal_num 비율 계산
                df['proportion'] = df['normal_num'] / df['normal_num'].sum()
                # 비율에 맞게 normal_num 값을 계산하여 추가
                df['additional_normal_num'] = (df['proportion'] * remaining_sum).apply(math.floor)
                # 추가해야 할 개수 조정
                diff = remaining_sum - df['additional_normal_num'].sum()
                # print(diff)
                if diff > 0:
                    max_proportion = df.loc[df['proportion'] != 0, 'proportion'].max()
                    max_indices = df.index[df['proportion'] == max_proportion]
                    additional_per_index = diff // len(max_indices)  # 균등 분배할 값 계산
                    remaining_additional = diff % len(max_indices)  # 나머지 개수 계산

                    # 균등 분배
                    df.loc[max_indices, 'additional_normal_num'] += additional_per_index

                    # 나머지 추가 분배
                    if remaining_additional > 0:
                        df.loc[max_indices[:remaining_additional], 'additional_normal_num'] += 1
                df['normal_num'] += df['additional_normal_num']
                df = df.drop(['proportion', 'additional_normal_num'], axis=1)
                normal_check1 = df

                if normal_check1['normal_num'].sum() != normal_num:
                    print(c, " 10개 no")

                cmap_num_list[c] = normal_check1.copy()
                if c == t - 1:
                    # print("fin.")
                    break
                else:
                    listb = []
                    for d in range(len(listc)):
                        longitude = listc[d][0]  # 경도
                        latitude = listc[d][1]  # 위도

                        # 경도와 위도의 범위를 확인하는 조건식을 벡터화된 방식으로 작성
                        condition = (
                                (sensor_grid['upper_left_lot'] <= longitude) &
                                (sensor_grid['lower_right_lot'] >= longitude) &
                                (sensor_grid['upper_left_lat'] >= latitude) &
                                (sensor_grid['lower_right_lat'] <= latitude)
                        )

                        # 조건을 만족하는 행의 인덱스를 가져옴
                        matching_index = condition[condition].index  # [0]
                        # print("매칭: ", matching_index + 1)

                        if (cluster_rows['grid_num'].isin([matching_index + 1]).any() == True):
                            listb.append(listc[d])

                    while (len(listb) != normal_num):
                        cluster_rows = cluster_rows.sort_values(by='additional_normal_num', ascending=False)
                        grid_data = sensor_grid.loc[sensor_grid['grid_num'] == cluster_rows['grid_num'].iloc[0]]
                        cluster_rows['additional_normal_num'].iloc[0] -= 1
                        # 정규분포 시작위치를 그리드 중심으로 변경
                        listb.append([grid_data['center_lot'].iloc[0], grid_data['center_lat'].iloc[0]])
                    listc = []
                    listc = listb
    # '''
    # db_connection_path = 'mysql+pymysql://root:root@192.168.100.6/weather'
    db_connection_path = 'mysql+pymysql://root@127.0.0.1:3307/weather'
    engine = create_engine(db_connection_path)
    # '''
    max_value = 0

    for i in range(len(cmap_num_list)):
        data4 = cmap_num_list[i]
        data4 = data4[data4['normal_num'] != 0]
        data4['id'] = exist_id

        data4.to_sql(table3[-1], con=engine, if_exists='append', index=False)

        if len(data4) != 0:
            max_value = i
        '''
        if (i == 0):
            data4.to_sql(table3, con=engine, if_exists='replace', index=False)
        else:
            data4.to_sql(table3, con=engine, if_exists='append', index=False)
        '''
    # '''
    engine.dispose()

    return_value = {
        "01exist_id": int(exist_id),
        "02max_value": int(max_value),
    }
    return return_value


def get_m():
    m = (int(m_before[-1]) * 60) // (float(interval_time[-1]) * int(interval[-1]))
    return m

import mysql.connector
import math

# Thay các thông tin sau bằng thông tin của cơ sở dữ liệu MySQL của bạn
config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',  # hoặc địa chỉ IP của máy chủ MySQL
    'port': 3307,  # Cổng kết nối, mặc định là 3306 cho MySQL
    'database': 'weather',
    'raise_on_warnings': True
}

def calculate_distance(lat1, lon1, lat2, lon2):
    # Chuyển đổi độ sang radian
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)
    
    # Tính khoảng cách giữa hai điểm
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = 6371 * c  # 6371 là bán kính trái đất (đơn vị km)
    
    return distance

conn = mysql.connector.connect(**config)

if conn.is_connected():
    print('Connected to MySQL database')

    # Tạo đối tượng Cursor để thực hiện truy vấn
    cursor = conn.cursor()

    # Viết truy vấn SQL để lấy dữ liệu từ bảng
    querySensorData = 'SELECT DISTINCT m_date FROM raw_data'

    # Thực thi truy vấn
    cursor.execute(querySensorData)

    # Lấy tất cả các dòng dữ liệu
    rowsSensorGrid = cursor.fetchall()

    # Hiển thị dữ liệu
    for row in rowsSensorGrid:
        m_date = row[0]

        queryRawData = 'SELECT * FROM raw_data WHERE m_date = "'+str(m_date)+'"'
                # Thực thi truy vấn
        cursor.execute(queryRawData)

        # Lấy tất cả các dòng dữ liệu
        rowsRawData = cursor.fetchall()

        for rowsofRawData in rowsRawData:
            longitude = rowsofRawData[5]  
            latitude = rowsofRawData[6]  
            X_rawData = rowsofRawData[7]
            Y_rawData = rowsofRawData[8]   
            nameofRawData = rowsofRawData[1]
            m_date_RawData = rowsofRawData[4]
            rowData = rowsofRawData
            
            querySensorData = 'SELECT * FROM sensor_grid'

            # Thực thi truy vấn
            cursor.execute(querySensorData)

            # Lấy tất cả các dòng dữ liệu
            rowsSensorGrid = cursor.fetchall()
            nearest_points = []
            ExistingLotLat = []
            # Hiển thị dữ liệu
            for rowsofSensorgrid in rowsSensorGrid:
                latofSensorgrid = rowsofSensorgrid[11]
                lotofSensorgrid = rowsofSensorgrid[10]
                grid_num = rowsofSensorgrid[0]

                distance = calculate_distance(lotofSensorgrid, latofSensorgrid, latitude, longitude)
                nearest_points.append((nameofRawData,rowsofSensorgrid, distance, m_date_RawData, grid_num, lotofSensorgrid, latofSensorgrid,X_rawData,Y_rawData))

            # Sắp xếp theo khoảng cách và chọn ba điểm gần nhất
            nearest_points.sort(key=lambda x: x[2])  # Sắp xếp theo khoảng cách
            nearest_points = nearest_points[:3]      # Chọn ba dòng gần nhất

            vec_x = 0
            vec_y = 0
            print("distance = ", distance)
            print("nearest_points = ", nearest_points)
        break

            # for element in nearest_points:
            #     print("element: ", element)
                # wd = element[1][2]
                # ws = element[1][3]
                # date = element[1][4]
                # grid_num = element[4]
                # center_lot_nearest = element[5]
                # center_lat_nearest = element[6]
                # # calculate vector x for each sensors
                # x = ws*math.sin(math.radians(wd))
                # y = ws*math.cos(math.radians(wd))
                # vec_x += x
                # vec_y += y

            # realWindSpeed = math.sqrt((vec_x*vec_x) + (vec_y*vec_y))

            # # Tìm góc a từ giá trị sin bằng cách sử dụng hàm arcsin
            # radian_angle = math.asin(vec_x/realWindSpeed)

            # # Chuyển đổi radian sang độ
            # degree_angle = math.degrees(radian_angle)

            # # print("Góc a là:", degree_angle, "độ")

            # # case 4
            # if((vec_x < 0) & (vec_y < 0)):
            #     degree_angle = (90 - (degree_angle * (-1))) + 180
            #     # print("Độ thật = ", degree_angle)
            # # case 3
            # elif (vec_x > 0) & (vec_y < 0):
            #     degree_angle = 90 + degree_angle
            #     # print("Độ thật = ", degree_angle)
            # # case 2
            # elif (vec_x > 0) & (vec_y > 0):
            #     degree_angle = degree_angle
            #     # print("Độ thật = ", degree_angle)
            # # case 1
            # elif(vec_x < 0) & (vec_y > 0):
            #     degree_angle = 270 + (90 - (degree_angle * (-1)))
            #     print("Độ thật = ", degree_angle)

            # print("realWindSpeed: ", realWindSpeed)

            # # Câu lệnh INSERT INTO
            # sql = "INSERT INTO estimate_grid_sensor_data_test (m_name, center_lot,center_lat,wd,ws,vec_x,vec_y,date,section) VALUES (%s, %s, %s, %s, %s, %s,%s, %s, %s)"

            # # Dữ liệu cần chèn vào
            # val = (grid_num, center_lot_nearest, center_lat_nearest, degree_angle, realWindSpeed, vec_x, vec_y, date, 1)

            # # Thực hiện INSERT INTO với dữ liệu cần chèn vào

            # cursor.execute(sql, val)

            # # Lưu các thay đổi
            # conn.commit()

            # # In thông báo sau khi chèn dữ liệu thành công
            # print(cursor.rowcount, "record inserted.")
            # # break
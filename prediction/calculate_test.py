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

# Kết nối đến cơ sở dữ liệu
try:
    conn = mysql.connector.connect(**config)

    if conn.is_connected():
        print('Connected to MySQL database')

        # Tạo đối tượng Cursor để thực hiện truy vấn
        cursor = conn.cursor()

        # Viết truy vấn SQL để lấy dữ liệu từ bảng
        querySensorData = 'SELECT * FROM sensor_grid'

        # Thực thi truy vấn
        cursor.execute(querySensorData)

        # Lấy tất cả các dòng dữ liệu
        rowsSensorData = cursor.fetchall()

        ExistingLotLat = []
        # Hiển thị dữ liệu
        for row in rowsSensorData:
            lat = row[11]
            lot = row[10]
            ExistingLotLat.append(lot)
            ExistingLotLat.append(lat)

        # print("ExistingLotLat: ",ExistingLotLat)

        # Tìm ba dòng dữ liệu gần nhất
        nearest_points = []
        queryRawData = 'SELECT * FROM raw_data'

        # Thực thi truy vấn
        cursor.execute(queryRawData)

        # Lấy tất cả các dòng dữ liệu
        rowsRawData = cursor.fetchall()

        for row in rowsRawData:
            longitude = row[5]  # Lấy kinh độ từ dòng dữ liệu
            latitude = row[6]   # Lấy vĩ độ từ dòng dữ liệu
            name = row[1]
            m_date = row[4]
            
            distance = calculate_distance(ExistingLotLat[0], ExistingLotLat[1], latitude, longitude)
            
            nearest_points.append((name, row, distance, m_date))

        # Sắp xếp theo khoảng cách và chọn ba điểm gần nhất
        nearest_points.sort(key=lambda x: x[2])  # Sắp xếp theo khoảng cách
        nearest_points = nearest_points[:3]      # Chọn ba dòng gần nhất

        vec_x = 0
        vec_y = 0

        print("nearest_points = ", nearest_points)
        
        # In ra ba dòng dữ liệu gần nhất
        for name, point, distance, m_date in nearest_points:
            # print(f"Name: {name}, m_date: {m_date}, Longitude: {point[-1]}, Latitude: {point[-2]}, Distance: {distance} km")
            # Hàm tính khoảng cách giữa hai điểm dựa trên kinh độ và vĩ độ
            # Viết truy vấn SQL để lấy dữ liệu từ bảng
            queryRawDataCon = 'SELECT * FROM raw_data WHERE m_name = "'+name+'" AND m_date = "'+str(m_date)+'"'

            # Thực thi truy vấn
            cursor.execute(queryRawDataCon)

            # Lấy tất cả các dòng dữ liệu
            queryRawDataConHaha = cursor.fetchall()

            for element in queryRawDataConHaha:
                wd = element[2]
                ws = element[3]
                
                # calculate vector x for each sensor

                x = ws*math.sin(math.radians(wd))
                y = ws*math.cos(math.radians(wd))

                vec_x += x
                vec_y += y

                # print("x: ", x)
                # print("y: ", y)
                # print("vec_x: ", vec_x)
                # print("vec_y: ", vec_y)

            realWindSpeed = math.sqrt((vec_x*vec_x) + (vec_y*vec_y))

            # realWindDirection = math.sin(math.radians(vec_x/realWindSpeed))

            # Tìm góc a từ giá trị sin bằng cách sử dụng hàm arcsin
            radian_angle = math.asin(vec_x/realWindSpeed)

            # Chuyển đổi radian sang độ
            degree_angle = math.degrees(radian_angle)

            # print("Góc a là:", degree_angle, "độ")
            
            # case 4
            if((vec_x < 0) & (vec_y < 0)):
                degree_angle = (90 - (degree_angle * (-1))) + 180
                # print("Độ thật = ", degree_angle)
            # case 3
            elif (vec_x > 0) & (vec_y < 0):
                degree_angle = 90 + degree_angle
                # print("Độ thật = ", degree_angle)
            # case 2
            elif (vec_x > 0) & (vec_y > 0):
                degree_angle = degree_angle
                # print("Độ thật = ", degree_angle)
            # case 1
            elif(vec_x < 0) & (vec_y > 0):
                degree_angle = 270 + (90 - (degree_angle * (-1)))
                # print("Độ thật = ", degree_angle)

            # print("realWindSpeed: ", realWindSpeed)
            # print("realWindDirection: ", realWindDirection)

            # Lấy ra center_lot và center_lat, lấy ra grid_num của sensor_grid



        # Lấy ra m_date của raw_data

        # Đóng kết nối và cursor
        cursor.close()
        conn.close()

except mysql.connector.Error as err:
    print(f"Error: {err}")




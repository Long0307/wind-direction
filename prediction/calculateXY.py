import mysql.connector
import math

# Replace the following information with your MySQL database information
config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',  # or the IP address of the MySQL server
    'port': 3307,  # Connection port, default is 3306 for MySQL
    'database': 'weather',
    'raise_on_warnings': True
}

def calculate_distance(lotofSensorgrid, latofSensorgrid, latitude, longitude):

    distance = (longitude - lotofSensorgrid)*(longitude - lotofSensorgrid) + (latitude - latofSensorgrid)*(latitude - latofSensorgrid)

    result = math.sqrt(distance)
    
    return result

conn = mysql.connector.connect(**config)

if conn.is_connected():
    print('Connected to MySQL database')

    # Create a Cursor object to perform queries
    cursor = conn.cursor()

    # Write SQL query to get data from table
    querySensorData = 'SELECT DISTINCT m_date FROM raw_data'

    # Execute query
    cursor.execute(querySensorData)

    # Get all rows of data
    rowsSensorGrid = cursor.fetchall()

    # Display data
    for row in rowsSensorGrid:
        m_date = row[0]
        
        querySensorData = 'SELECT * FROM sensor_grid'

        # Execute query
        cursor.execute(querySensorData)

        # Get all rows of data
        rowsSensorGrid = cursor.fetchall()
        ExistingLotLat = []
        # Display data
        for rowsofSensorgrid in rowsSensorGrid:
            latofSensorgrid = rowsofSensorgrid[11]
            lotofSensorgrid = rowsofSensorgrid[10]
            grid_num = rowsofSensorgrid[0]

            queryRawData = 'SELECT * FROM raw_data WHERE m_date = "'+str(m_date)+'"'
            # Execute query
            cursor.execute(queryRawData)

            # Get all rows of data
            rowsRawData = cursor.fetchall()

            nearest_points = []
            for rowsofRawData in rowsRawData:
                # print("rowsRawData = ", rowsofRawData)
                wd = rowsofRawData[2]
                ws = rowsofRawData[3]
                # ========================================================
                latitude = rowsofRawData[5]  
                longtitude = rowsofRawData[6]  
                # ==========================================================
                X_rawData = rowsofRawData[7]
                Y_rawData = rowsofRawData[8]   
                nameofRawData = rowsofRawData[1]
                m_date_RawData = rowsofRawData[4]
                rowData = rowsofRawData

                # =======================================================

                # print(lotofSensorgrid, latofSensorgrid, latitude, longtitude)

                distance = calculate_distance(lotofSensorgrid, latofSensorgrid, latitude, longtitude)
                nearest_points.append((nameofRawData,rowsofSensorgrid, distance, m_date_RawData, grid_num, lotofSensorgrid, latofSensorgrid,X_rawData,Y_rawData, wd, ws))
                # nearest_points.append((nameofRawData,rowsofSensorgrid, distance, m_date_RawData))
                # nearest_points.append(distance)
                # print("nearest_points = ", nearest_points)
            nearest_points.sort(key=lambda x: x[2])  # Sort by distance
            nearest_points = nearest_points[:3]      # Select the three closest lines
            # distanceArray.append(distance)
            print("nearest_points = ", nearest_points)
            # break
            # calculate w1, w2, w3
            d = []
            for element in nearest_points:
                d.append(element[2])
            # print("w = ", d)

            weight = []
            
            if len(weight) == 1:
                for element in nearest_points:
                    w = (1/element[2])/(1/d[0])
                    weight.append(w)
                    
                    vec_x = (weight[0]*nearest_points[0][7])
                    vec_y = (weight[0]*nearest_points[0][8])
            elif len(weight) == 2:
                for element in nearest_points:
                    w = (1/element[2])/((1/d[0])+(1/d[1])+(1/d[2]))
                    weight.append(w)
                    
                    vec_x = (weight[0]*nearest_points[0][7])+(weight[1]*nearest_points[1][7])
                    vec_y = (weight[0]*nearest_points[0][8])+(weight[1]*nearest_points[1][8])
            elif len(weight) == 3:
                for element in nearest_points:
                    w = (1/element[2])/((1/d[0])+(1/d[1])+(1/d[2]))
                    weight.append(w)
                    
                    vec_x = (weight[0]*nearest_points[0][7])+(weight[1]*nearest_points[1][7])+(weight[2]*nearest_points[2][7])
                    vec_y = (weight[0]*nearest_points[0][8])+(weight[1]*nearest_points[1][8])+(weight[2]*nearest_points[2][8])
            
            print("v1 = ", vec_x)
            print("v2 = ", vec_y)

            ws = math.sqrt((vec_x*vec_x)+(vec_y*vec_y))
            
            radian_angle = math.sin(vec_x/ws)

            degree_angle = math.degrees(radian_angle)

            print("ws = ", ws)
            print("ws = ", degree_angle)
            # print("wd = ", wd*(-1) + 180)
        #     break
        # break

            # case 4
            if((vec_x < 0) & (vec_y < 0)):
                degree_angle = (degree_angle * (-1)) + 180
                print("Độ thật 1 = ", degree_angle)
            # case 3
            elif (vec_x > 0) & (vec_y < 0):
                degree_angle = (90 - degree_angle) + 90
                print("Độ thật 2 = ", degree_angle)
            # case 2
            elif (vec_x > 0) & (vec_y > 0):
                degree_angle = degree_angle
                print("Độ thật 3 = ", degree_angle)
            # case 1
            elif(vec_x < 0) & (vec_y > 0):
                degree_angle = 270 + (90 - (degree_angle * (-1)))
                print("Độ thật 4 = ", degree_angle)

            print("degree_angle: ", degree_angle)

            # INSERT INTO statement
            sql = "INSERT INTO estimate_grid_sensor_data_test_2 (m_name, center_lot,center_lat,wd,ws,vec_x,vec_y,date,section) VALUES (%s, %s, %s, %s, %s, %s,%s, %s, %s)"

            # Data to be inserted
            val = (grid_num, lotofSensorgrid, latofSensorgrid, degree_angle, ws, vec_x, vec_y, m_date_RawData, 1)

            # Perform INSERT INTO with the data to be inserted

            cursor.execute(sql, val)

            # Save changes
            conn.commit()

            # Print a message after inserting data successfully
            print(cursor.rowcount, "record inserted.")
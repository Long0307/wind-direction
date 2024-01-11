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

            queryRawData = "SELECT * FROM raw_data WHERE m_name IN ('WT3', 'WT7') AND m_date = '"+str(m_date)+"'"

            # Execute query
            cursor.execute(queryRawData)

            # Get all rows of data
            rowsRawData = cursor.fetchall()

            nearest_points = []

            for rowsofRawData in rowsRawData:
                # print("rowsRawData = ", rowsofRawData)
                wd = rowsofRawData[2]
                ws = rowsofRawData[3]
                longitude = rowsofRawData[5]  
                latitude = rowsofRawData[6]  
                X_rawData = rowsofRawData[7]
                Y_rawData = rowsofRawData[8]   
                nameofRawData = rowsofRawData[1]
                m_date_RawData = rowsofRawData[4]
                rowData = rowsofRawData

                nearest_points.append((nameofRawData,rowsofSensorgrid, "", m_date_RawData, grid_num, lotofSensorgrid, latofSensorgrid,X_rawData,Y_rawData, wd, ws))

            vec_x = 0
            vec_y = 0
            # print("distance = ", distance)
            # print("nearest_points = ", nearest_points)

            for element in nearest_points:
                print("element: ", element)
                wd = element[9]
                ws = element[10]
                date = element[3]
                grid_num = element[4]
                center_lot_nearest = element[5]
                center_lat_nearest = element[6]
                # calculate vector x for each sensors
                x = ws*math.sin(math.radians(wd))
                y = ws*math.cos(math.radians(wd))
                vec_x += x
                vec_y += y

            realWindSpeed = math.sqrt((vec_x*vec_x) + (vec_y*vec_y))

            # Find angle a from the sine value using the arcsin function
            radian_angle = math.asin(vec_x/realWindSpeed)
            # radian_angle = math.sin(vec_x/realWindSpeed)

            # # Convert radians to degrees
            degree_angle = math.degrees(radian_angle)

            print("Góc a là:", degree_angle, "độ")

            # case 4
            if((vec_x < 0) & (vec_y < 0)):
                degree_angle = (90 - (degree_angle * (-1))) + 180
                print("Độ thật = ", degree_angle)
            # case 3
            elif (vec_x > 0) & (vec_y < 0):
                degree_angle = 90 + degree_angle
                print("Độ thật = ", degree_angle)
            # case 2
            elif (vec_x > 0) & (vec_y > 0):
                degree_angle = degree_angle
                print("Độ thật = ", degree_angle)
            # case 1
            elif(vec_x < 0) & (vec_y > 0):
                degree_angle = 270 + (90 - (degree_angle * (-1)))
                print("Độ thật = ", degree_angle)

            print("realWindSpeed: ", realWindSpeed)

            # INSERT INTO statement
            sql = "INSERT INTO estimate_grid_sensor_data_test_1 (m_name, center_lot,center_lat,wd,ws,vec_x,vec_y,date,section) VALUES (%s, %s, %s, %s, %s, %s,%s, %s, %s)"

            # Data to be inserted
            val = (grid_num, center_lot_nearest, center_lat_nearest, degree_angle, realWindSpeed, vec_x, vec_y, date, 1)

            # Perform INSERT INTO with the data to be inserted

            cursor.execute(sql, val)

            # Save changes
            conn.commit()

            # Print a message after inserting data successfully
            print(cursor.rowcount, "record inserted.")
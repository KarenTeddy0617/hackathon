from flask import Flask, render_template, request
from datetime import datetime, timedelta
import mysql.connector as sqlcon
import os

# Establish MySQL connection
mcon = sqlcon.connect(host='localhost', user='root', passwd='root123', database='crops')
cursor = mcon.cursor()

try:
    cursor.execute("create database crops")
    cursor.execute("use crops")
except:
    cursor.execute("use crops")
try:
    cursor.execute('create table crop1 (crop_id int primary key, crop varchar(25), Growing_season_south varchar(50), Growing_season_north varchar(50),Sowing_distance_ft int, Duration_days int)')
except:
    pass
try:   
    cursor.execute(" insert into crop1 values(1, 'Onion', 'Mar-Apr May-Jun Sept-Oct', 'May-Jun', 4, 150)")
    cursor.execute("insert into crop1 values(2, 'Bottle Gourd', 'Feb-Mar Jun-July', 'Nov-Dec Dec-Jan Jan-July', 4, 150)")
    cursor.execute("insert into crop1 values (3,'Carrot','Aug-Sept-Oct','Aug-Nov', 2,  75)")
    cursor.execute("insert into crop1 values (4,'Tomato','Jun-Aug Nov-Dec','Jan-Feb Jun-Jul Oct-Nov',1,  110)")
    cursor.execute("insert into crop1 values (5,'Melon','Feb-Mar Jun-Jul','Jan-Feb Mar-Jun Oct-Dec', 18,70)")
    cursor.execute("insert into crop1 values (6,'Potato','Oct-Dec','Oct-Dec',4, 70)")
    cursor.execute("insert into crop1 values (7,'Cabbage','Sept-Oct','Jun-Jul Oct-Nov', 1,  90)")
    cursor.execute("insert into crop1 values (8,'Beans','Feb-Mar',NULL,8,45)")
    cursor.execute("insert into crop1 values (9,'Broccoli','Aug-Sept','Aug-Sept',1 ,90)")
    cursor.execute("insert into crop1 values (10,'Cucumber','Feb-Mar Jun-Jul','Jun-Jul Sept-Oct Dec-Jan',12,50)")
    cursor.execute("insert into crop1 values (11,'Corn','Oct-Nov','Sept-Oct', 4,60)")
    cursor.execute("insert into crop1 values (12,'Lettuce','Sept-Oct','Oct-Dec',8,45)")
    cursor.execute("insert into crop1 values (13,'Radish','Aug-Jan',NULL,2,40)")
    cursor.execute("insert into crop1 values (14,'Pumpkin','Jan-Mar Sept-Dec May-Jun','Jun-Jul Dec-Jan',24,70)")
    cursor.execute("insert into crop1 values (15,'Bitter Gourd','Feb-Mar', 'Jun-Jul Nov-Dec Dec-Jan Jun-Jul',1 ,55)")
    mcon.commit()
except:
    pass

app = Flask(__name__)

# Set the folder for image uploads
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Function to check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/pagetwo', methods=['POST', 'GET'])
def input():
    if request.method == 'POST':
        # Get data from the form
        area = float(request.form['manualarea'])  # Convert area to float
        crop = request.form['crop-select']
        date_str = request.form['date-input']
        
        # Handle image upload
        image = request.files.get('image-input')
        image_url = None

        if image and allowed_file(image.filename):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(filename)
            image_url = filename  # Store the file path in the database or pass it to the template
        try:
            cursor.execute('create table input (area int(11) ,crop varchar(25) primary key ,date date ,image_url varchar(255) )')
        except:
            cursor.execute('drop table input')
            cursor.execute('create table input (area int(11) ,crop varchar(25) primary key ,date date ,image_url varchar(255) )')
            
        # Insert the data into the database
        cursor.execute("INSERT INTO input  (area, crop, date, image_url) VALUES (%s, %s, %s, %s)", (area, crop, date_str, image_url))
        mcon.commit()
    
        # Retrieve data from the database based on the selected crop
        cursor.execute('SELECT * FROM crop1 WHERE crop = %s', (crop,))
        data = cursor.fetchone()
       
        if not data:
            return "No data found for this crop.", 404  # Handle the case if no data is found
        cursor.execute('drop table input')

        # Extract the relevant data from the query result
        a = data[4]  # The field size (likely area in meters)
        s_ind = data[2]  # Seed index (assuming from the database structure)
        n_ind = data[3]  # Another index (assuming this is needed)
        growth_duration = data[5]  # Growth duration in days (assuming this is in the 5th column)
        crop=data[1]
        # Calculate seed count based on area
        seed_cal = area / (a * a)

        # Convert the input date to a datetime object
        date_format = "%Y-%m-%d"
        input_date = datetime.strptime(date_str, date_format)

        # Calculate the expected optimal yield dates
        result_date = input_date + timedelta(days=growth_duration)
        result_date2 = result_date + timedelta(days=7)

        # Format the result dates to strings
        t = (result_date.strftime(date_format), result_date2.strftime(date_format))

        # Return the calculated data and image URL to the output page
        return render_template('output.html',crop=crop,seed_cal=seed_cal, t=t, s_ind=s_ind, n_ind=n_ind, image_url=image_url)

    return render_template('trial.html')


@app.route('/')
def home():
    return render_template('trial.html')


if __name__ == '__main__':
    app.run(debug=True)

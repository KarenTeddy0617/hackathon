from flask import Flask, render_template, request
from datetime import datetime, timedelta
import mysql.connector as sqlcon
import os

# Establish MySQL connection
mcon = sqlcon.connect(host='localhost', user='root', passwd='root123', database='crops')
cursor = mcon.cursor()

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

        # Insert the data into the database
        query = "INSERT INTO input (area, crop, date, image_url) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (area, crop, date_str, image_url))
        mcon.commit()

        # Retrieve data from the database based on the selected crop
        q = 'SELECT * FROM crop1 WHERE crop = %s'
        cursor.execute(q, (crop,))
        data = cursor.fetchone()

        if not data:
            return "No data found for this crop.", 404  # Handle the case if no data is found

        # Extract the relevant data from the query result
        a = data[4]  # The field size (likely area in meters)
        s_ind = data[2]  # Seed index (assuming from the database structure)
        n_ind = data[3]  # Another index (assuming this is needed)
        growth_duration = data[5]  # Growth duration in days (assuming this is in the 5th column)

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
        return render_template('output.html', seed_cal=seed_cal, t=t, s_ind=s_ind, n_ind=n_ind, image_url=image_url)

    return render_template('trial.html')


@app.route('/')
def home():
    return render_template('trial.html')


if __name__ == '__main__':
    app.run(debug=True)

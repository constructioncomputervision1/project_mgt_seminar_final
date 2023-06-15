from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import matplotlib.pyplot as plt
import io
import base64
import seaborn as sns
import pandas as pd


app = Flask(__name__)

app.secret_key = 'james'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'user-system'

mysql = MySQL(app)


@app.route('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = %s AND password = %s', (email, password,))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['userid'] = user['userid']
            session['name'] = user['name']
            session['email'] = user['email']
            message = 'Logged in successfully !'

            # Fetch data from the 'housing' table
            cursor.execute('SELECT * FROM housing')
            housing_data = cursor.fetchall()

            # Prepare data for scatter plot
            prices = [row['price'] for row in housing_data]
            areas = [row['area'] for row in housing_data]

            # Generate scatter plot
            fig, ax = plt.subplots()
            ax.scatter(areas, prices)
            ax.set_xlabel('Area')
            ax.set_ylabel('Price')
            ax.set_title('Scatter Plot: Price vs. Area')

            # Save the plot image to a BytesIO object
            plot_image = io.BytesIO()
            plt.savefig(plot_image, format='png')
            plot_image.seek(0)

            # Encode the plot image to base64 string
            plot_image_base64 = base64.b64encode(plot_image.getvalue()).decode()

            # Fetch data for heatmap
            heatmap_data = []
            for row in housing_data:
                heatmap_data.append([row['area'], row['price'], row['bedrooms'], row['bathrooms'], row['stories']])

            # Create a DataFrame for the heatmap data
            heatmap_df = pd.DataFrame(heatmap_data, columns=['Area', 'Price', 'Bedrooms', 'Bathrooms', 'Stories'])

            # Calculate correlation matrix
            correlation_matrix = heatmap_df.corr()

            # Generate heatmap
            fig, ax = plt.subplots()
            sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', ax=ax)
            ax.set_title('Heatmap: Correlation Matrix')

            # Save the heatmap plot image to a BytesIO object
            heatmap_image = io.BytesIO()
            plt.savefig(heatmap_image, format='png')
            heatmap_image.seek(0)

            # Encode the heatmap plot image to base64 string
            heatmap_image_base64 = base64.b64encode(heatmap_image.getvalue()).decode()

            return render_template('user.html', message=message, housing_data=housing_data,
                                   plot_image=plot_image_base64, heatmap_image=heatmap_image_base64)


        else:
            message = 'Please enter correct email / password !'
    return render_template('login.html', message=message)



@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    mesage = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form:
        userName = request.form['name']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = % s', (email,))
        account = cursor.fetchone()
        if account:
            mesage = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mesage = 'Invalid email address !'
        elif not userName or not password or not email:
            mesage = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO user VALUES (NULL, % s, % s, % s)', (userName, email, password,))
            mysql.connection.commit()
            mesage = 'You have successfully registered !'
    elif request.method == 'POST':
        mesage = 'Please fill out the form !'
    return render_template('register.html', mesage=mesage)


if __name__ == "__main__":
    app.run()







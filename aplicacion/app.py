from flask import Flask, render_template, request, redirect, url_for, flash
#from flask_mysqldb import MySQL
from flask_cassandra import CassandraCluster
from cassandra.cqlengine import columns


# initializations
app = Flask(__name__)
cassandra = CassandraCluster()


app.config['CASSANDRA_NODES'] = ['localhost']

# settings
app.secret_key = "mysecretkey"



# routes
@app.route('/')
def Index():
    session = cassandra.connect()
    session.set_keyspace("db")
    q = request.args.get('q')
    if q:
        query = session.execute("SELECT * from contacts where fullname like '{}%'".format(q))
        #query=session.execute("SELECT * FROM contacts where fullname = '{}' ALLOW FILTERING".format(q))
        return render_template('index.html', contacts = query)
    else:

        data = session.execute("SELECT * FROM contacts")
        return render_template('index.html', contacts = data)

@app.route('/add_contact', methods=['POST'])
def add_contact():
    if request.method == 'POST':
        fullname = request.form['fullname']
        phone = int(request.form['phone'])
        email = request.form['email']
        session = cassandra.connect()
        session.set_keyspace("db")
        session.execute("INSERT INTO contacts (fullname, phone, email) VALUES (%s,%s,%s)", (fullname, phone, email))
        flash('Contact Added successfully')
        return redirect(url_for('Index'))

@app.route('/edit/<phone>', methods = ['POST', 'GET'])
def get_contact(phone):
    session = cassandra.connect()
    session.set_keyspace("db")
    data = session.execute('SELECT * FROM contacts WHERE phone = {0}'.format(phone))
    print(data[0])
    return render_template('edit-contact.html', contact = data[0])

@app.route('/update/<phone>', methods=['POST'])
def update_contact(phone):
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        session = cassandra.connect()
        session.execute("""
            UPDATE contacts
            SET fullname = %s,
                email = %s,
            WHERE phone = %s
        """.format(int(phone), str(email), str(fullname)))
        flash('Contact Updated Successfully')
        return redirect(url_for('Index'))

@app.route('/delete/<string:phone>', methods = ['POST','GET'])
def delete_contact(phone):
    session = cassandra.connect()
    session.set_keyspace("db")
    session.execute('DELETE FROM contacts WHERE phone = {0}'.format(phone))
    flash('Contact Removed Successfully')
    return redirect(url_for('Index'))
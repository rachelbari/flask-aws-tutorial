'''
Simple Flask application to test deployment to Amazon Web Services
Uses Elastic Beanstalk and RDS

Author: Scott Rodkey - rodkeyscott@gmail.com

Step-by-step tutorial: https://medium.com/@rodkey/deploying-a-flask-application-on-aws-a72daba6bb80
'''

from flask import Flask, render_template, request, send_file
from application import db
from application.models import Data
from application.forms import EnterDBInfo, RetrieveDBInfo
import pymysql.cursors
import csv
import boto
from boto.s3.key import Key
import pandas as pd
from io import BytesIO

# Elastic Beanstalk initalization
application = Flask(__name__)
application.debug=True
# change this to your own value
application.secret_key = 'cC1YCIWOj9GgWspgNEo2'   

            
@application.route('/', methods=['GET', 'POST'])
@application.route('/index', methods=['GET', 'POST'])
def index():
    form1 = EnterDBInfo(request.form) 
    form2 = RetrieveDBInfo(request.form) 
    
    if request.method == 'POST' and form1.validate():
        data_entered = Data(notes=form1.dbNotes.data)
        try:     
            db.session.add(data_entered)
            db.session.commit()        
            db.session.close()
        except:
            db.session.rollback()
        return render_template('thanks.html', notes=form1.dbNotes.data)
        
    if request.method == 'POST' and form2.validate():
        try:   
            num_return = int(form2.numRetrieve.data)
            query_db = Data.query.order_by(Data.id.desc()).limit(num_return)
            for q in query_db:
                print(q.notes)
            db.session.close()
        except:
            db.session.rollback()
        return render_template('results.html', results=query_db, num_return=num_return)                
    
    return render_template('index.html', form1=form1, form2=form2)
@application.route('/dump',methods=['GET','POST'])
def dump():
    form1 = EnterDBInfo(request.form) 
    form2 = RetrieveDBInfo(request.form) 
    connection = pymysql.connect(host='database-1.c6lvlt1bior5.us-east-2.rds.amazonaws.com',
                                user='admin',
                                password='adminpassword',
                                db='db1')

    cursor = connection.cursor()
    sql = "SELECT * FROM data"
    
    df = pd.read_sql(sql, connection)
    print('df')
    df.to_csv()
    print(df)
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1',index=False)
    writer.close()
    output.seek(0)
    print('done')

    del df

    connection.close()
    cursor.close()

    return send_file(output, attachment_filename="testing.xlsx", as_attachment=True)
    #return render_template('index.html', form1=form1, form2=form2)

if __name__ == '__main__':
    application.run(host='0.0.0.0')

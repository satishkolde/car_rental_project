import random
from flask import Flask,render_template,request,redirect
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from functions import pdfReader, user_data
from functions import UserInfo
import os
from sqlalchemy import select
import datetime
from fpdf import FPDF

def comp_str(x,y):
    ch=0
    if len(x)==len(y):
        for i in range (len(x)):
            print(f"{x[i]} ,{y[i]}")
            if x[i]!=y[i]:
                print("Strings are not equal")
                ch=1
                break
        if(ch==0):
            return True
    else:
        return False


# global login_value
# login_value = "something"
db = SQLAlchemy()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///user_data.db"
user = None
app.config['SQLALCHEMY_BINDS'] = {'car_data':"sqlite:///car_data.db",'book':"sqlite:///booking.db"}
db.init_app(app)


class User(db.Model):
    index = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String,unique=True,nullable=False)
    email = db.Column(db.String,unique=True,nullable=False)
    mobile = db.Column(db.String,unique=True,nullable=False)
    password = db.Column(db.String,unique=True,nullable=False)

class UserInf(db.Model):
    __bind_key__ = "book"
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String,unique=False,nullable=False)
    jdate = db.Column(db.String,unique=False,nullable=False)
    price = db.Column(db.Integer,unique=False,nullable=False)
    vehicle = db.Column(db.String,unique=False,nullable=False)
    
class CarData(db.Model):
    __bind_key__ = "car_data"
    id = db.Column(db.Integer,primary_key=True)
    carname = db.Column(db.String,unique=False,nullable=False)
    carrating = db.Column(db.Integer,unique=False,nullable=False)
    carprice = db.Column(db.Integer,unique=False,nullable=False)
    cartype = db.Column(db.String,unique=False,nullable=False)
    carlink = db.Column(db.String,unique=False,nullable=False)
    carcapacity = db.Column(db.String,unique=False,nullable=False)

    def __repr__(self) -> str:
        return f"{self.carname}"



@app.route('/',methods=["GET","POST"])
def home():
    return render_template('home.html',user=user)


@app.route('/login',methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        stmt = select(User).where(User.email == email)        
        result = db.session.execute(stmt).scalar()
        if result == None:
            return render_template('login_page.html',user=None,login=None,password=None)
        if result.password != password:
            return render_template('login_page.html',user=None,login=None,password="Invalid Password")
        global user
        name = result.name
        email = result.email
        password = result.password
        mobile = result.mobile
        user = UserInfo(name,email,password,mobile)
        return redirect('/')
    return render_template('login_page.html',user=None,login=None,password=None)

@app.route('/registration',methods=["GET","POST"])
def registration():    
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        mobile = request.form['mobile']
        password = request.form['password']
        name = name.split()
        name = '_'.join(name)        
        global user
        user = UserInfo(name,email,password,mobile)      
        use = User(name=name,email=email,mobile=mobile,password=password)
        db.session.add(use)
        db.session.commit()  
        return redirect('/')
    return render_template('registration.html',user=user)


loc = None
dat = None
day = None
with app.app_context():
    data = db.session.query(CarData).all()

@app.route('/booking',methods=["GET","POST"])
def booking():    
    global loc
    global dat
    global data
    global day
    if "booking.db" not in os.listdir('instance'):
        with app.app_context():
            db.create_all(bind_key="book")
    if request.method == "GET":
        if type_car == "all":
            data = db.session.query(CarData).all()
        else:
            data = db.session.query(CarData).where(CarData.cartype == type_car)

    if request.method == "POST":
        location = request.form['location']
        loc = location
        day = request.form['jdays']
        date = request.form['date']
        dat = date
        
        return render_template('booking.html',data=data,location=location,date=date,user=user,day=day)
    
    return render_template('booking.html',data=data,location=loc,date=dat,user=user,day=day)

@app.route('/booking/<date>/<place>/<price>/<car_name>',methods=['GET'])
def booked_data(car_name,date,place,price):
    print(user.name)
    
    return redirect('/booking')



@app.route('/user/del',methods=["GET",'POST'])
def del_user():
    # global user
    global user
    user = None    
    return redirect('/')

type_car = "all"

@app.route('/filter',methods=["GET","POST"])
def filter():
    global type_car
    if request.method == "POST":
        type_car = request.form['cartype']
        return redirect('/booking')

@app.route('/invoice/<carname>/<date>/<day>',methods=['GET','POST'])
def invoice(carname,date,day):
        global user
        car = db.session.query(CarData).where(CarData.carname == carname).first()
        car1 = UserInf(email = user.email,jdate=date,price=car.carprice,vehicle=car.carname)
        db.session.add(car1)
        db.session.commit()
        pdfReader(f'{datetime.date.today()}',carname,car.carcapacity,car.carprice,day,date)
        with open('./static/invoice.txt','rb') as file:
            d = file.read().decode('utf8')
            d = d.replace('DATE',f'{datetime.date.today()}')
            d = d.replace('RANDOM',f'{random.randint(10000,50000)}')
            d = d.replace('CARNAME',carname)
            d = d.replace('XXX',f'{car.carcapacity}')
            d = d.replace('WWW',date)
            d = d.replace('YYY',f'{car.carprice}')
            d = d.replace('ZZZ',f'{day}')
            sub = int(day)*car.carprice * 100 + 1000
            tax = sub*4/100
            d = d.replace('AAA',f'{sub}') 
            d = d.replace('BBB',f'{tax}')
            total = sub + tax
            d  = d.replace('CCC',f'{total}')
        with open('./static/provision_invoice.txt','wb') as file:
            file.write(d.encode('utf-8'))        
        return render_template('invoice.html',car=car,carlink=car.carlink[1:],user=user)

@app.route('/history')
def history():
    user_data = db.session.query(UserInf).where(UserInf.email == user.email)
    return render_template('history.html',user=user,data=user_data)

@app.route('/history/delete/<date>/<price>/<carname>')
def del_user_data(date,price,carname):
    global user
    item = select(UserInf).where(UserInf.email == user.email)
    item = db.session.execute(item)   
    for items in item:
       
        if items[0].vehicle == carname and items[0].jdate == date:
            db.session.delete(items[0])
            db.session.commit()    
    return redirect('/history')

if __name__ == "__main__":
    app.run(port=80,debug=False)
    


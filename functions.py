import pandas as pd
import os
from flask import request
import shutil
from flask import session
import pathlib
from fpdf import FPDF
import random
def user_data(name,email,mobile,password):
        dic = {}
        dic['name'] = name
        dic['email'] = email
        dic['mobile'] = mobile
        dic['password'] = password
        return dic

def data_enter(dict):
    d = pd.read_csv('./static/user_data.csv')
    d = pd.DataFrame(d)
    output = pd.DataFrame()
    output = output.append(dict,ignore_index=True)
    d = d.append(output)
    d.to_csv('./static/user_data.csv',index=False)
    
def data_searcher(email,password):
        d = pd.read_csv('./static/user_data.csv')
        d = pd.DataFrame(d)
        d = d[d['email'] == email]
        d = d[d['password'] == password]
        if d.shape[0] <= 1:
                return True
        return False

def pdfReader(book_date,carname,carcapacity,carprice,days,jdate):
    pdf = FPDF(orientation = 'P', unit = 'mm', format='A5')
    pdf.add_page()
    pdf.set_font('Arial', 'B', 8)
    pdf.cell(148,10,txt='CAR RENTAL RECEIPT',ln=1,align='C')
    pdf.cell(148,5,txt=f'Date: {book_date}',ln=1,align='L')
    pdf.cell(148,5,txt=f'Receipt : {random.randint(1,30)}',ln=1,align='L')
    pdf.cell(148,10,txt='Rental Company Info',ln=1,align='C')
    pdf.cell(148,5,txt=f'Company: Car Rental',ln=1,align='L')
    pdf.cell(148,5,txt=f'Representative: Pavan and Satish',ln=1,align='L')
    pdf.cell(148,5,txt=f'Location: Bengaluru',ln=1,align='L')
    pdf.cell(148,5,txt=f'City/State/ZIP: Karnataka',ln=1,align='L')
    pdf.cell(148,5,txt=f'Phone: #########',ln=1,align='L')
    pdf.cell(148,10,txt='Vehicle Information',ln=1,align='C')
    pdf.cell(148,5,txt=f'Model: {carname}',ln=1,align='L')
    pdf.cell(148,5,txt=f'Capacity: {carcapacity}',ln=1,align='L')
    pdf.cell(148,5,txt=f'Journey Date : {jdate}',ln=1,align='L')
    pdf.cell(148,15,txt=f'Renting Info',ln=1,align='C')
    pdf.cell(148,5,txt=f"Cost/km - {carprice}\tRenting Days - {days}",ln=1,align='C')
    pdf.cell(148,5,txt=f'Additional Costs - 1000',ln=1,align='C')
    sub = carprice*100*int(days)+1000
    pdf.cell(148,5,txt=f'Subtotal - {sub}',ln=1,align='C')
    tax = sub*4/100
    pdf.cell(148,5,txt=f'Tax - {tax}',ln=1,align='C')
    pdf.cell(148,5,txt=f'Total - {tax+sub}',ln=1,align='L')
    pdf.cell(148,5,txt=f'Amout Paid - {tax+sub}')
    pdf.output('./static/invoice.pdf','F')

class UserInfo:
        def __init__(self,name,email,password,number):
                self.name = name
                self.email = email
                self.password = password
                self.number = number        
        
        def __repr__(self) -> str:
               return f"{self.name}-{self.email}-{self.password}-{self.number}"
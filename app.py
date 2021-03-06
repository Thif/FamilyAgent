from flask import Flask,render_template, flash, request,url_for
import pandas as pd
import numpy as np
import datetime as dt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

TODAYS_DATE= dt.datetime.now()
FILEPATH="./data/Key_dates.csv"
GMAIL_ADDRESS=""
GMAIL_PASSWORD=""
SENDER_NAME="Thibaut Forest"

def send_email(receiver_email,receiver_name,content):

	
	msg = MIMEMultipart('alternative')
	msg['Subject'] = "Daily news - Forest Family"
	msg['From'] = SENDER_NAME
	msg['To'] = receiver_email
	
	# Create the body of the message (a plain-text and an HTML version).

	html = """\
	<html>
	  <head></head>
	  <body>
	    <h2>Hi """ +str(receiver_name)+"""!</h2><br>
	       <h4><i>Today we celebrate</i></h4>
	       <h2><font color="red">""" +str(content)+"""</font></h2>
	       <h4><i>Birthday</i></h4>
	    <img src=https://media3.giphy.com/media/qFnzbxQhHG3xS/200w.gif >
	  </body>
	</html>
	"""

	part = MIMEText(html, 'html')
	msg.attach(part)

	s = smtplib.SMTP('smtp.gmail.com:587')
	s.ehlo()
	s.starttls()
	s.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
	s.sendmail(GMAIL_ADDRESS, receiver_email, msg.as_string())
	s.quit()
	
def yearsago(years, from_date=None):
    if from_date is None:
        from_date = datetime.now()
    return from_date - relativedelta(years=years)
    
def read_data(file):
	headers = ['Firstname','Lastname','Birthday','Saintsday']
	dtypes = {'Firstname': 'str', 'Lastname': 'str', 'Birthday': 'str', 'Saintsday': 'str'}
	parse_dates = ['Birthday', 'Saintsday']
	df=pd.read_csv("./data/Key_dates.csv",delimiter=";", dtype=dtypes, parse_dates=parse_dates)
	
	return df
	
def Get_name_list_for_today(df,type):
	df_temp=df.copy()
	firstname=df_temp[(df_temp[type].dt.month==TODAYS_DATE.month) & (df_temp[type].dt.day==TODAYS_DATE.day)]["Firstname"].values
	lastname = df_temp[(df_temp[type].dt.month == TODAYS_DATE.month) & (df_temp[type].dt.day == TODAYS_DATE.day)][
		"Lastname"].values
	ages = np.rint(df_temp[(df_temp[type].dt.month == TODAYS_DATE.month) & (df_temp[type].dt.day == TODAYS_DATE.day)][
		"Age"]).values

	return zip(firstname, lastname, ages.astype(int))

def Add_age(df):
	df_temp=df.copy()
	df_temp["Age"]=TODAYS_DATE.date()-df_temp["Birthday"]
	df_temp["Age"]=df_temp["Age"] / np.timedelta64(1, 'Y')
	return df_temp

def Get_name_list_of_next(df,type,number):
	df_temp=df.copy()

	df_temp["temp_date"]=pd.to_datetime((TODAYS_DATE.year*10000+df_temp[type].dt.month*100+df_temp[type].dt.day).apply(str),format='%Y%m%d')
	df_temp["TimeDelta"]=df_temp["temp_date"]-TODAYS_DATE.date()
	df_temp["Delta"]=df_temp["TimeDelta"]
	df_temp=df_temp[df_temp["Delta"].dt.days!=0] # avoid current
	df_temp.loc[df_temp["TimeDelta"].dt.days<0,"Delta"]=df_temp["TimeDelta"]+dt.timedelta(days=365)

	firstname=df_temp.nsmallest(number, 'Delta')["Firstname"].values
	lastname=df_temp.nsmallest(number, 'Delta')["Lastname"].values
	ages=np.rint(df_temp.nsmallest(number, 'Delta')["Age"]).values

	day = df_temp.nsmallest(number, 'Delta')[type].dt.strftime("%B %d")

	return zip(firstname,lastname,ages.astype(int),day)
	
def Get_todays_events(df):
	return

def Plot_event_data(df):

	return zip(df["Birthday"].dt.strftime("%d/%m/%y").tolist(),df["Age"].tolist())
	
@app.route('/', methods=['POST','GET'])
def main():

	df=read_data(FILEPATH)

	df=Add_age(df)
	
	todays_birthdays=Get_name_list_for_today(df,"Birthday")
	todays_saintsday=Get_name_list_for_today(df,"Saintsday")
	next_birthdays=Get_name_list_of_next(df,"Birthday",3)
	next_saintsday=days=Get_name_list_of_next(df,"Saintsday",3)
	plot_data=Plot_event_data(df)
	send_email(GMAIL_ADDRESS,SENDER_NAME,"content")
	
	return render_template('main.html',todays_birthdays=todays_birthdays,todays_saintsday=todays_saintsday,next_birthdays=next_birthdays,next_saintsday=next_saintsday,plot_data=plot_data)

if __name__ == '__main__':
    app.run(debug=True)

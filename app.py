from flask import Flask,render_template, flash, request,url_for
import pandas as pd
import numpy as np
import pandas as pd
import datetime as dt



app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

TODAYS_DATE= dt.datetime.now()
FILEPATH="./data/Key_dates.csv"

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
	return df_temp[(df_temp[type].dt.month==TODAYS_DATE.month) & (df_temp[type].dt.day==TODAYS_DATE.day)]["Firstname"].values

def Add_age(df):
	df_temp=df.copy()
	df_temp["Age"]=TODAYS_DATE.date()-df_temp["Birthday"]
	df_temp["Age"]=df_temp["Age"] / np.timedelta64(1, 'Y')
	return df_temp

def Get_name_list_of_next(df,type,number):
	df_temp=df.copy()
	if type=="Saintsday":
		df_temp["temp_date"]=pd.to_datetime((TODAYS_DATE.year*10000+df_temp["Saintsday"].dt.month*100+df_temp["Saintsday"].dt.day).apply(str),format='%Y%m%d')	
	else:
		df_temp["temp_date"]=pd.to_datetime((TODAYS_DATE.year*10000+df_temp["Birthday"].dt.month*100+df_temp["Birthday"].dt.day).apply(str),format='%Y%m%d')
		
	df_temp["TimeDelta"]=df_temp["temp_date"]-TODAYS_DATE.date()
	df_temp["Delta"]=df_temp["TimeDelta"]
	df_temp.loc[df_temp["TimeDelta"].dt.days<0,"Delta"]=df_temp["TimeDelta"]+dt.timedelta(days=365)
		
	
	firstname=df_temp.nsmallest(number, 'Delta')["Firstname"].values
	lastname=df_temp.nsmallest(number, 'Delta')["Lastname"].values
	ages=np.round_(df[df["Firstname"].isin(firstname)]["Age"]).values
	birthday=df[df["Firstname"].isin(firstname)]["Birthday"].dt.date
	
	

	return zip(firstname,lastname,ages,birthday)
	
def Get_todays_events(df):
	return
	
@app.route('/', methods=['POST','GET'])
def main():

	df=read_data(FILEPATH)
	df=Add_age(df)
	
	todays_birthdays=Get_name_list_for_today(df,"Birthday")
	todays_saintsday=Get_name_list_for_today(df,"Saintsday")
	next_birthdays=Get_name_list_of_next(df,"Birthday",3)
	next_saintsday=days=Get_name_list_of_next(df,"Saintsday",3)

	return render_template('main.html',todays_birthdays=todays_birthdays,todays_saintsday=todays_saintsday,next_birthdays=next_birthdays,next_saintsday=next_saintsday)

if __name__ == '__main__':
    app.run(debug=True)

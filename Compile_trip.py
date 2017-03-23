import time
import pandas as pd
import os
from numba import jit
import shutil

colnames1={
'tripduration':'duration',
'starttime':'starttime',
'stoptime':'stoptime',
'start station id':'stn1_id',
'start station name':'stn1_name',
'start station latitude':'lat1',
'start station longitude':'long1',
'end station id':'stn2_id',
'end station name':'stn2_name',
'end station latitude':'lat2',
'end station longitude':'long2',
'bikeid':'bikeid',
'usertype':'usertype',
'birth year':'birth_yr',
'gender':'gender',

}

colnames2={
'Trip Duration':'duration',
'Start Time':'starttime',
'Stop Time':'stoptime',
'Start Station ID':'stn1_id',
'Start Station Name':'stn1_name',
'Start Station Latitude':'lat1',
'Start Station Longitude':'long1',
'End Station ID':'stn2_id',
'End Station Name':'stn2_name',
'End Station Latitude':'lat2',
'End Station Longitude':'long2',
'Bike ID':'bikeid',
'User Type':'usertype',
'Birth Year':'birth_yr',
'Gender':'gender'
}



folder = './by_grid/'
if os.path.exists(folder):
	shutil.rmtree(folder)
if not os.path.exists(folder):
	os.makedirs(folder)
# colnames=[
# 'duration',
# 'starttime',
# 'stoptime',
# 'stn1_id',
# 'stn1_name',
# 'lat1',
# 'long1',
# 'stn2_id',
# 'stn2_name',
# 'lat2',
# 'long2',
# 'bikeid',
# 'usertype',
# 'birth_yr',
# 'gender'

# ]


# 40.6466 40.804213
# -74.0171345 -73.9298910999999

lat_min,lat_max=40.67,40.78
long_min,long_max=-74.02,-73.94
lat_sep=60
long_sep=40
lat_div=(lat_max-lat_min)/lat_sep
long_div=(long_max-long_min)/long_sep

# @jit(nopython=True)
def calc_gridx(longi):
	if long_min<longi<long_max:
		# grid_y=int((lat-lat_min)/lat_div)
		grid_x=int((longi-long_min)/long_div)
		# grid=grid_x+long_sep*grid_y
		return grid_x
	else:
		return -1

def calc_gridy(lat):
	if lat_min<lat<lat_max:
		grid_y=int((lat-lat_min)/lat_div)
		# grid_x=int((longi-long_min)/long_div)
		# grid=grid_x+long_sep*grid_y
		return grid_y
	else:
		return -1


print ('\n', 'start')
start=time.time()


dfs=[]
files=[f for f in os.listdir('./') if 'data' in f and '.csv' in f]
print (files,'\n','\n')

for eachFile in files[0:1]:
	print (eachFile)
	df=pd.read_csv(eachFile,sep=',',low_memory=True,skipinitialspace=True)#,nrows=10000)#,usecols=[1,2,5,6,9,10])
	if df.columns[0]=="tripduration":
		colnames=colnames1
	else:
		colnames=colnames2

	df.rename(columns=colnames,inplace=True)
	df=df[df.lat1.between(39,42)];df=df[df.long1.between(-80,-70)]
	df=df[df.lat2.between(39,42)];df=df[df.long2.between(-80,-70)]

	# print (df.lat1.min(), df.lat1.max())
	# print (df.long1.min(), df.long1.max())
	# print (df.lat2.min(), df.lat2.max())
	# print (df.long2.min(), df.long2.max())

	# df2=df.groupby(['stn1_id','yr1','week1'],as_index=False).agg({'lat1':['count','mean'],'long1':['count','mean']})
	# print (df2[0:30])

	# df2=df.groupby(['stn1_id'], as_index=False).agg({'lat1':['count','mean']})
	# print (len(df2))
	# print (df2[0:10])

	# df['starttime']=pd.to_datetime(df['starttime'],infer_datetime_format=True)
	# df['stoptime']=pd.to_datetime(df['stoptime'],infer_datetime_format=True)
	# df['yr1']=df['starttime'].dt.year
	# df['week1']=df['starttime'].dt.week


	## ----------------- Trips that start at station xx ----------------------
	df1=df[['stn1_id','starttime','lat1','long1','gender']]
	df1['starttime']=pd.to_datetime(df1['starttime'],infer_datetime_format=True)
	df1['yr']=df1['starttime'].dt.year
	df1['week']=df1['starttime'].dt.week

	#summarize to stn level:
	df1=df1.groupby(['stn1_id','lat1','long1','yr','week'],as_index=False).agg({'gender':'count'}) 
	# df1.columns=df1.columns.droplevel()
	# df1.reset_index(level=[0,1,2,3,4],inplace=True)
	df1['grid_x']=df1.apply(lambda row:calc_gridx(row['long1']), axis=1)
	df1['grid_y']=df1.apply(lambda row:calc_gridy(row['lat1']), axis=1)

	#summarize to grid level:
	df1=df1.groupby(['grid_x','grid_y','yr','week'],as_index=False).agg({'gender':'sum'}) 
	# df1=df1.groupby(['grid','yr','week'],as_index=False)#.agg({'gender':'count','stn1_id':'mean'})
	# print (df1[df1.gender>1])
	# for groups, df_x in df1:
	# 	if len(df_x)>2:
	# 		print (df_x)
	df1.rename(columns={'gender':'count1'}, inplace=True)
	df1=df1[['grid_x','grid_y','yr','week','count1']]
	# df1.to_csv("df1.csv")


	## ------------ Trips that ends at station xx -----------------
	df2=df[['stn2_id','starttime','lat2','long2','gender']]
	df2['starttime']=pd.to_datetime(df2['starttime'],infer_datetime_format=True)
	df2['yr']=df2['starttime'].dt.year
	df2['week']=df2['starttime'].dt.week
	df2=df2.groupby(['stn2_id','lat2','long2','yr','week'],as_index=False).agg({'gender':'count'})
	# df2.columns=df2.columns.droplevel()
	# df2.reset_index(level=[0,1,2,3,4],inplace=True)
	df2['grid_x']=df2.apply(lambda row:calc_gridx(row['long2']), axis=1)
	df2['grid_y']=df2.apply(lambda row:calc_gridy(row['lat2']), axis=1)
	df2=df2.groupby(['grid_x','grid_y','yr','week'],as_index=False).agg({'gender':'sum'})
	df2.rename(columns={'gender':'count2'}, inplace=True)
	df2=df2[['grid_x','grid_y','yr','week','count2']]



	## ----------------- Trips that start and end at the same station xx ---------------
	df3=df[df.stn1_id==df.stn2_id]
	df3=df3[['stn1_id','starttime','lat1','long1','gender']]
	df3['starttime']=pd.to_datetime(df3['starttime'],infer_datetime_format=True)
	df3['yr']=df3['starttime'].dt.year
	df3['week']=df3['starttime'].dt.week
	df3=df3.groupby(['stn1_id','lat1','long1','yr','week'],as_index=False).agg({'gender':'count'})
	# df3.columns=df3.columns.droplevel()
	# df3.reset_index(level=[0,1,2,3,4],inplace=True)
	df3['grid_x']=df3.apply(lambda row:calc_gridx(row['long1']), axis=1)
	df3['grid_y']=df3.apply(lambda row:calc_gridy(row['lat1']), axis=1)

	df3=df3.groupby(['grid_x','grid_y','yr','week'],as_index=False).agg({'gender':'sum'})
	df3.rename(columns={'gender':'count3'}, inplace=True)
	df3=df3[['grid_x','grid_y','yr','week','count3']]

	## ----------- Summarizing trips start/end at grid xx ---------------------
	## trips that start and end in same grid will be double counted, so need to minus off 
	df=df1.merge(df2,on=['grid_x','grid_y','yr','week'],how='outer')
	df=df.merge(df3,on=['grid_x','grid_y','yr','week'],how='outer')

	df.fillna(0,inplace=True)
	df['count']=df['count1']+df['count2']-df['count3']

	# print (df_final[0:10])
	# print (len(df_final))
	df.to_csv(folder+eachFile)
	# dfs.append(df)


# df=pd.concat(dfs)
# print (len(df))



end=time.time()
print ('time:',end-start)
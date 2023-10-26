import pandas as pd
import os
from datetime import datetime

def newest(path,fname,itera=None):     
	"""
	this function returns newest file in top level folder by partial filename
	optional argument to perform search return last {itera} items
	optional argument doesn't disrupt existing operations, maintains original behavior
	"""
	files = os.listdir(path)
	paths = [os.path.join(path, basename) for basename in files if fname in basename]
	thatlist=sorted(paths,key=os.path.getmtime)
	finallist=[]
	if itera:
		itera=itera
	else:
		itera=1
	for i in range(itera):
		finallist.append(thatlist[-(i+1)])
	if len(finallist)<2:
		finallist=finallist[0]
	return(finallist)

def getdata(fileloc):
	"""
	This function gets the newest data from designated folder on shared drive
	for history reports
	"""
	filename=newest(fileloc,"NPAY502")
	with open(filename) as file:
		Data=file.read()
	return(Data)

#TODO create a dictionary format for this encompassing the categories defined below
def processor(row,newrows,deptid,rowdata):
	"""
	This function iterates over each line of the file to collect and compile data
	"""
	if "N" in row[1]:
		if len(rowdata)>1:
			if "N number" in rowdata:
				newrows.append(rowdata)
		items=[item for item in row.split(' ') if item!=""]
		rowdata={"N number":items[0],"Record number":items[1],"Action":items[2],\
		"Start Date":items[3],"End Date":items[4],"Hours":items[5],"Days":items[6],\
		"Amount":items[7],"Units":items[8]}
		rowdata["Agency"]=deptid
		rowdata["Inactive"]=""
		rowdata["Ineligible"]=""
		rowdata["Job Change"]=""
		rowdata["Other"]=""
		rowdata["Remediation"]=""
	elif "ERROR" in row:
		if "Employee ineligible for Earnings Code based on Earnings Program." in row:
			rowdata["Ineligible"]="Yes"
		if "The employee is not active in the department." in row:
			rowdata["Inactive"]="Yes"
		elif "Earnings code dates overlap a Job Change." in row:
			rowdata["Job Change"]="Yes"
		else:
			rowdata["Other"]="Yes"

	if "DeptID" in row:
		items=row.split(" ")
		deptid=[item for item in items if "70" in item][0]
	#N num, record num, action type, start date, end date, hours, days, amount, units
	#discover which type of data it is and categorize accordingly

	return(newrows,deptid,rowdata)

def write_tab(data,fileloc):
	"""
	This function writes the data into an excel report in a folder named Formatted
	"""
	df = pd.DataFrame(data)
	date=datetime.today().strftime('%Y_%m_%d')
	newfilename=f"{fileloc}/formatted/Control_D_{date}.xlsx"
	df.to_excel(newfilename,index=False)
	

def file_move(fileloc):
	"""
	This function renames the original data and moves to a folder named Raw
	"""
	filename=newest(fileloc,"NPAY502")
	date=datetime.today().strftime('%Y_%m_%d')
	newfilename=f"{fileloc}/raw/Control_D_{date}.txt"
	os.rename(filename,newfilename)
	


def main(fileloc,Data=None):
	"""
	This is the main function which accepts txt NPAY502 Control D data
	and returns a formatted and interpreted set of readale information
	"""
	if Data:
		Data=Data
	else:
		Data=getdata(fileloc)
	Data=Data.split('\n')
	Data=[row for row in Data if row!=" "]
	Data=[row for row in Data if len(row)>1]
	newrows=[]
	rowdata=""
	deptid=""
	for row in Data:
		newrows,deptid,rowdata=processor(row,newrows,deptid,rowdata)
	write_tab(newrows,fileloc)
	file_move(fileloc)
	
if __name__ == "__main__":
	main("z:/reports/ctrl d reports")
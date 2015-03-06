import pandas as pd
from sklearn.naive_bayes import MultinomialNB
import sklearn.preprocessing
from sklearn.ensemble import RandomForestClassifier
from patsy import dmatrices
import datetime as dt
import csv
import numpy as np
from ggplot import *
from sklearn import linear_model

fileName = "SPD_Incident_Response.csv"
#Via json. Only returns the last 1000 rows
test = pd.read_json('https://data.seattle.gov/resource/3k2p-39jp.json')

SPData = pd.read_csv(fileName)
SPData['EvClearDate'] = pd.to_datetime(SPData['Event Clearance Date'])
temp = pd.DataFrame(SPData['EvClearDate'].str.split(' ',2).tolist(),columns = ['date', 'EvTime'])
SPData = SPData.join(temp)

#FORMAT DATA FOR MACHINE LEARNING ANALYSIS
#Create scene date and time integers as well as hour and minute. Might want to use datetime package instead
def dateClean(SPData):
    SPscene = SPData.dropna(subset=['At Scene Time'])
    SPscene = SPscene.reset_index(drop=True)
    temp2 = pd.DataFrame(SPscene['At Scene Time'].str.split(' ',2).tolist(),columns = ['sceneDate', 'sceneTime'])
    SPscene = SPscene.join(temp2)
    month = pd.DataFrame(SPscene['sceneDate'].str.split('/').tolist(),columns = ['month', 'day', 'year'])
    SPscene = SPscene.join(month)
    hour = pd.DataFrame(SPscene['sceneTime'].str.split(':').tolist(), columns = ['hour', 'minute'])
    SPscene = SPscene.join(hour)
    return SPscene
len(SPscene)

#For getting time in a plottable form
def timeValue(row):
    try:
        temp = float(row['sceneTime'].split(':')[0])
        temp1 = float(row['sceneTime'].split(':')[1])/60
        return temp + temp1
    except:
        print row['sceneTime']
SPscene['timePlot'] = SPscene.apply(timeValue, axis=1)

#Create a hash table of urgency levels with crimes for Higher, Lower, Same
def toDict(file2):
    with open(file2) as f:
        f.readline() # ignore first line (header)
        mydict = dict(csv.reader(f, delimiter=','))
    return mydict
file3 = "UrgencyHash.csv"
urgHash = toDict(file3)

#Hash the values
def hashIt(SPscene):
    SPscene['EventUrgency'] = 1
    SPscene['InitialUrgency'] = 1
    SPscene['UrgentLevel'] = None
    for i in xrange(0, len(SPscene)):
        try:
            SPscene['EventUrgency'][i] = urgHash[SPscene['Event Clearance Group'][i]]
            SPscene['InitialUrgency'][i] = urgHash[SPscene['InitialTypeGroup'][i]]
            if  SPscene['InitialUrgency'][i] > SPscene['EventUrgency'][i]:
                SPscene['UrgentLevel'][i] = "Lower"
            elif SPscene['InitialUrgency'][i] < SPscene['EventUrgency'][i]:
                SPscene['UrgentLevel'][i] = "Higher"
            else:
                SPscene['UrgentLevel'][i] = "Same"
        except:
            pass
    return SPscene
SPscene.to_csv("SPData.csv")
# Data cleaning done!

filePath = "SPData.csv"
SPscene = pd.read_csv(filePath)
SPscene.rename(columns={'Event Clearance Group': 'EvClearGroup'}, inplace=True)
SPscene['UrgentLevel'].value_counts()
SPscene[SPscene['EvClearGroup'] == 'ARREST']['InitialTypeGroup'].value_counts()      
SPHigher = SPscene[SPscene.UrgentLevel == "Higher"]  
SPHigher['InitialTypeGroup'].value_counts()
SPHigher[SPHigher.InitialTypeGroup == "TRAFFIC RELATED CALLS"]['EvClearGroup'].value_counts()
SPLower = SPscene[SPscene.UrgentLevel == 'Lower']
SPLower['InitialTypeGroup'].value_counts()
SPLower[SPLower.InitialTypeGroup == 'THEFT']['EvClearGroup'].value_counts()

#Displays a matrix of initial crime and how it relates to eventual crime
def displayMatrix(data, group, group2):
    table = pd.DataFrame(data[group].value_counts())
    crimes = list(table.index.values)
    for crime in crimes:
        crime2 = pd.DataFrame(data[data[group] == crime][group2].value_counts())
        headers = list(crime2.index.values)
        #Place headers in dataframe
        for head in headers:
            if head not in list(table.columns):
                table[head] = 0
            #print head
            table.loc[crime, head] = crime2.loc[head][0]
    return table

#Soring the false alarms
temp1 = pd.DataFrame(police2014[police2014['EvClearGroup'] == "FALSE ALARMS"]["ZoneBeat"].value_counts())
temp2 = pd.DataFrame(police2014["ZoneBeat"].value_counts())
false = temp2.merge(temp1, left_on=temp2.index, right_on=temp1.index, how='inner', suffixes=['all', 'falseAlarms'])
false['percent'] = false['0falseAlarms']/false['0all']
false.sort(['percent'], ascending=False)

#Machine Learning
#Naive Bayes
SPml = SPscene.dropna(subset=['UrgentLevel'])
SPml = SPml.reset_index(drop=True)
outcome = SPml['UrgentLevel'].values
enc = LabelEncoder()
label_encoder = enc.fit(outcome)
outcome = label_encoder.transform(outcome)+1
features = SPml[['ZoneBeat', 'InitialUrgency', 'InitialTypeDesc', 'InitialTypeGroup', 'hour', 'month']]
features = pd.concat([pd.get_dummies(features[col]) for col in features], axis=1, keys=features.columns)
clf = MultinomialNB()
pred = clf.fit(features, outcome).predict(features)

def summary(outcome, pred):
    print 'Number of misclassified: ' + str((outcome != pred).sum())
    print np.mean(pred)

(SPml['UrgentLevel'].values != "Same").sum()

#Random Forest
rf = RandomForestClassifier()
fit = rf.fit(features, outcome)
pred = fit.predict(features)
split = np.random.rand(len(SPml)) < .9
xtrain = features[split]
ytrain = outcome[split]
fitTrain = rf.fit(xtrain, ytrain)
xtest = features[~split]
ytest = outcome[~split]
predTest = fitTrain.predict(xtest)
pd.crosstab(ytest, predTest, rownames=['actual'], colnames=['preds'])

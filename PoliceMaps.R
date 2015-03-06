#Police Maps

library(ggplot2)
library(ggmap)

data = "SPData.csv"
police = read.csv(data)
#Set column as date
police$EvDate = as.Date(police$EvDate, '%m/%d/%Y')
police$sceneDate = as.Date(police$sceneDate, '%m/%d/%Y')
#plot time
ggplot(police, aes(x=timePlot)) + geom_histogram(binwidth=.2)
#plot dates
plot(table(police$date))
#find top 10 most violent dates
tail(sort(table(police$date)), 10)
myfunc <- function(x,y,data){data[data$sceneDate >= x & data$sceneDate <= y,]}
time2014 <- myfunc(date1, date2, police)

#Parameters of data and date column to get time series graph of frequency
timeSeries = function(data, sceneDate) {
  time = as.data.frame(table(data[,sceneDate]))
  colnames(time)[1] = "Date"
  time$Date = as.Date(time$Date)
  return(ggplot(time, aes(Date, Freq)) + geom_line() 
         + scale_x_date(labels = date_format("%m/%d/%Y")))
}
time = timeSeries(time2014)
ggplot(time, aes(Date, Freq)) + geom_line() 
+ scale_x_date(labels = date_format("%m/%d/%Y"))

hard = time2014[time2014$EventUrgency >= 4,]
false = police[police$EventUrgency == 0,]
higher = time2014[time2014$UrgentLevel == 'Higher',]
lower = time2014[time2014$UrgentLevel == 'Lower',]

date1 = as.Date('2014-01-31')
date2 = as.Date('2014-02-02')
superbowl = myfunc(date1, date2, time2014)

carProwl = police[police$EvClearGroup == "CAR PROWL",]
carProwl$Latitude = as.numeric(carProwl$Latitude)
carProwl$Longitude = as.numeric(carProwl$Longitude)
colnames(carProwl)

UDistrict = qmap("University District, Seattle", zoom = 14, 
     source="stamen", maptype="toner",darken = c(.3,"#BBBBBB"))
Seattle = qmap("Seattle", zoom = 11, 
    source="stamen", maptype="toner",darken = c(.3,"#BBBBBB"))


UDistrict + geom_point(data=hard, aes(x=Longitude, y=Latitude), 
                              color="dark red", alpha=.8, size=2)

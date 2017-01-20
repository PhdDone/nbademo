import dbutils
import datetime

dbutils.init()
current_date = datetime.datetime(2017, 1, 30)
dbutils.init()
    #dump()
dbutils.searchByOneTeam("GSW", current_date)
dbutils.drop()

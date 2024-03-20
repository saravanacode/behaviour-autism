
from datetime import datetime
from pymongo import MongoClient
import os



#client = MongoClient('mongodb+srv://ganeshyadharth:AbleLyf@students.jbrazv2.mongodb.net/?retryWrites=true&w=majority')
#mongo_db = client["attendance"]


#client = MongoClient('mongodb+srv://ganeshyadharth:AbleLyf@students.jbrazv2.mongodb.net/?retryWrites=true&w=majority')
client = MongoClient('mongodb+srv://ganeshyadharth:AbleLyf@students.jbrazv2.mongodb.net/?retryWrites=true&w=majority&appName=students')
mongo_db = client["AbleLyf"]
collection = mongo_db["behaviour"]
mongo_collection = mongo_db["candidateBehaviour"]




update_query = {'name': "saravana"}
update_data = {
        '$push': {
            'activity': {
                'status': "Active",
                'activitycur': "Fighting",
                'area': "Playhall",
                'cam': "6",
                'time': datetime.now().strftime('%H:%M:%S'),
                'date': datetime.now().strftime('%Y-%m-%d')
                }}}

mongo_collection.update_one(update_query, update_data)
     
updates_query = {'name': "sethu"}
updates_data = {
        '$push': {
            'activity': {
                'status': "InActive",
                'activitycur': "SittingInActive",
                'area': "Playhall",
                'cam': "6",
                'time': datetime.now().strftime('%H:%M:%S'),
                'date': datetime.now().strftime('%Y-%m-%d')
                }}}


mongo_collection.update_one(updates_query, updates_data)

updatess_query = {'name': "subramani"}
updatess_data = {
        '$push': {
            'activity': {
                'status': "Active",
                'activitycur': "Bitting",
                'area': "Playhall",
                'cam': "6",
                'time': datetime.now().strftime('%H:%M:%S'),
                'date': datetime.now().strftime('%Y-%m-%d')
                }}}


mongo_collection.update_one(updatess_query, updatess_data)


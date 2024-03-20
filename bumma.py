
from pymongo import MongoClient
import os


#client = MongoClient('mongodb+srv://ganeshyadharth:AbleLyf@students.jbrazv2.mongodb.net/?retryWrites=true&w=majority')
#mongo_db = client["attendance"]


#client = MongoClient('mongodb+srv://ganeshyadharth:AbleLyf@students.jbrazv2.mongodb.net/?retryWrites=true&w=majority')
client = MongoClient('mongodb+srv://ganeshyadharth:AbleLyf@students.jbrazv2.mongodb.net/?retryWrites=true&w=majority&appName=students')
mongo_db = client["AbleLyf"]
collection = mongo_db["behaviour"]
mongo_collection = mongo_db["candidateBehaviour"]


#2uhcc1glsbifus6
#13aggn1gls4u0t0j
#1rhb1gltrfcjvs

update_query = {'name': "saravana"}
update_data = {
        '$set': {
            'candidateID': "2uhcc1glsbifus6"}}
                

mongo_collection.update_one(update_query, update_data)
collection.update_one(update_query, update_data)

updates_query = {'name': "sethu"}
updates_data = {
        '$set': {
            'candidateID': "13aggn1gls4u0t0j"}}
                

mongo_collection.update_one(updates_query, updates_data)
collection.update_one(updates_query, updates_data)

updatess_query = {'name': "subramani"}
updatess_data = {
        '$set': {
            'candidateID': "1rhb1gltrfcjvs"}}
                

mongo_collection.update_one(updatess_query, updatess_data)
collection.update_one(updatess_query, updatess_data)
     


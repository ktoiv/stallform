import pymongo
import os

class DataAccessor(object):

    def __init__(self, db_name, collection_name):
        self.db = None
        self.collection = None
        self.db_name = db_name
        self.collection_name = collection_name

    

    def connect(self):
        username = os.environ['MONGO_USER']
        password = os.environ['MONGO_PASSWORD']
        cluster_name = os.environ['MONGO_CLUSTER_NAME']

        self.client = pymongo.MongoClient(f"mongodb+srv://{username}:{password}@{cluster_name}.xlbh3.mongodb.net/{self.db_name}?retryWrites=true&w=majority")
        self.db = self.client[self.db_name]
        self.collection = self.db[self.collection_name]

    
    def insert_one(self, data):
        self.collection.insert_one(data)

    def insert_many(self, data_list):
        if len(data_list) < 1:
            return
        self.collection.insert_many(data_list)

    def find(self, query):
        result_cursor = self.collection.find(query)
        return list(result_cursor)

    def find_one(self,  query):
        result = self.collection.find_one(query)
        return result

    
    def count(self, query):
        return self.collection.count_documents(query)

    def distinct(self, field):
        return self.collection.distinct(field)
    
    def delete_many(self, query):
        self.collection.delete_many(query)

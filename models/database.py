import pymongo


class Database(object):
    URI = "mongodb://127.0.0.1:27017"
    DATABASE = None

    @staticmethod
    def initialize(datab):
        client = pymongo.MongoClient(Database.URI)
        Database.DATABASE = client[datab]

    @staticmethod
    def insert(collection, data):
        Database.DATABASE[collection].insert(data)

    @staticmethod
    def find(collection, query, sortField=None):
        if sortField:
            result = Database.DATABASE[collection].find(query).sort(sortField)
            for i in result:
                return i
        return Database.DATABASE[collection].find_one(query)

    @staticmethod
    def find_all(collection, query, sortField=None, limit_=0, skip_=0):
        if sortField:
            # print('sorting with field')
            result = Database.DATABASE[collection].find(query).sort(
                [(sortField, pymongo.DESCENDING)]).limit(limit_).skip(skip_)
            # result = sorted(result, key= lambda r: r[sortField] , reverse=True)
            return result

        return Database.DATABASE[collection].find(query).limit(limit_).skip(skip_)

    @staticmethod
    def find_multi(collection, SearchField, items, sortField = None, limit_ = 0, skip_ = 0, findOne = True):
        """
            Useful For Searching..
            field = feildname
            items = list of items
        """

        if SearchField:
            if sortField:
                result = Database.DATABASE[collection].find({f'{SearchField}': {'$elemMatch': {
                        '$elemMatch': {'$in': items}}}}).sort(
                        [(sortField, pymongo.DESCENDING)]
                        ).limit(limit_).skip(skip_)
            else:
                if findOne:
                    # works on nested data
                    result = Database.DATABASE[collection].find_one({f'{SearchField}': {'$elemMatch': {
                            '$elemMatch': {'$in': items}}}})
                else:
                    result = Database.DATABASE[collection].find({f'{SearchField}': {'$in': items}}).limit(limit_).skip(skip_)

            return result
            
        return Database.DATABASE[collection].find(query).limit(limit_).skip(skip_)

        return result

    @staticmethod
    def count(collection, query={}):
        return Database.DATABASE[collection].count_documents(query)

    @staticmethod
    def delete(collection, query):
        return Database.DATABASE[collection].delete_one(query).deleted_count

    @staticmethod
    def delete_all(collection, query={}):
        return Database.DATABASE[collection].delete_many(query).deleted_count

    @staticmethod
    def update(collection, query, update_query): 
        return Database.DATABASE[collection].update(query,
                                                    {"$set": update_query})

    @staticmethod
    def updateMany(collection, query, update_query):
        if update_query.get('$inc'):
            return Database.DATABASE[collection].update(query, update_query)   

        return Database.DATABASE[collection].update_many(query,
                                                         {"$set": update_query})
    @staticmethod
    def created_at(_id):
        return _id.generation_time

        # @staticmethod
    # def updateAll(collection, update_query, query={}):
    #     return Database.DATABASE[collection].update_many(query,
    #                                                      {"$set": update_query}
    # )

from models.database import Database


class Category(object):

    COLLECTION = 'Categories'

    def __init__(self, category,
                 number_of_images=0,
                 _id=None):
        self.category = category
        self._id = _id
        self.number_of_images = number_of_images

    def toJson(self):
        return {
            'category': self.category,
            'number_of_images': self.number_of_images
        }

    def SaveCategory(self):
        if not self.getCategory(self.category):
            return Database.insert(collection=Category.COLLECTION,
                        data=self.toJson())
        else:
            return self.updateCategories([self.category])

    @staticmethod
    def updateCategory(cat):
        return Database.update(collection=Category.COLLECTION,
                               query={'category': cat.get('category')},
                               update_query=cat)

    @staticmethod
    def updateCategories(cats, inc = 1):
        for c in cats:
            if not Category.getCategory(c):
                Category(c, number_of_images=1).SaveCategory()
            else:
                Database.updateMany(
                    collection = Category.COLLECTION,
                    query = {'category' : {'$in' : cats}}, 
                    update_query = {'$inc': {'number_of_images': inc}})

    @staticmethod
    def getCategory(category):
        return Database.find(collection=Category.COLLECTION,
                             query={'category': category})

    @staticmethod
    def getAllCategories(upload=False):
        if not upload:
            return list(Database.find_all(
            collection=Category.COLLECTION,
            query={'number_of_images': {'$gt': 0}},
            sortField='number_of_images'))

        if upload:
            categories = Database.find_all(
            collection=Category.COLLECTION,query={})
            categories = [i.get('category') for i in categories]
        return categories


if __name__ == '__main__':
    Database.initialize('Atypical')

    print(Category.getAllCategories(upload=True))

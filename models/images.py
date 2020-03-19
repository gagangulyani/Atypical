from datetime import datetime
from models.database import Database
from uuid import uuid4
from models.categories import Category
import pymongo


class Image(object):
    COLLECTION = 'Images'

    def __init__(self,
                 userID,
                 categories,
                 image,
                 img_id,
                 description="",
                 tags=[],
                 _id=None,
                 upvotes=[],
                 downvotes=[],
                 comments=[]):

        self.userID = userID
        self.categories = categories
        self.image = image
        self.description = description
        self.tags = tags
        self.totalDownloads = 0
        self.totalUpvotes = 0
        self._id = _id
        self.upvotes = upvotes
        self.downvotes = downvotes
        self.img_id = img_id
        self.comments = comments

    def saveImg(self):
        """
            This Method Saves Image object in Images Collection
        """
        Database.insert(collection=Image.COLLECTION,
                        data=self.toJson())

    def toJson(self):
        """
            Returns JSON Object of Image Object
            (excluding _id attribute)

            Note:
                It excludes _id for preventing 
                Overwriting the value
        """
        return {
            "userID": self.userID,
            "categories": self.categories,
            "image": self.image,
            "description": self.description,
            "totalUpvotes": self.totalUpvotes,
            "totalDownloads":self.totalDownloads,
            "tags": self.tags,
            "upvotes": self.upvotes,
            "downvotes": self.downvotes,
            "img_id": self.img_id,
            "comments": self.comments
        }

    @staticmethod
    def GetImg(img_id):
        JsonImg = Image.GetByImgID(img_id)
        if JsonImg:
            JsonImg.update({'created_at': Database.created_at(img_id)})

        return JsonImg

    @staticmethod
    def GetByImgID(img_id, userID=None):
        """
            Finds Image in Images Collection using
            Image ID

            Returns :
            a) if found : Json object of image
            b) if Not Found : None
        """

        result = Database.find(collection=Image.COLLECTION,
                               query={'img_id': img_id})
        return result

    @staticmethod
    def GetAllImages(query = {},skip_ = 0, limit_ = 0, sortField = None):
        return Database.find_all(
            collection=Image.COLLECTION,
            query=query, skip_ = skip_, limit_ = limit_, sortField = sortField)

    @staticmethod
    def GetImgsByCategory(category,skip_ = 0, limit_ = 0):
        """
            Finds all images with category provided in the argument
            Returns the cursor (for iterating the Images Collection)
        """
        if category.lower() == 'most downloaded':
            print('most downloaded')
            return Database.find_all(collection=Image.COLLECTION,
                                 query={}, sortField='totalDownloads', skip_ = skip_, limit_ = limit_)

        elif category.lower() == 'top rated':
            print('top rated')
            return Database.find_all(collection=Image.COLLECTION,
                                 query={}, sortField='totalUpvotes', skip_ = skip_, limit_ = limit_)

        print(category, skip_, limit_)
        return Database.find_multi(collection=Image.COLLECTION,
                                 SearchField = 'categories', items = [category],
                                  skip_ = skip_, limit_ = limit_, findOne=False)

    @staticmethod
    def GetImgCategory(cat = None):
        if cat:
           return Image.GetImgsByCategory(cat) 

        categories = Category.getAllCategories()
        finalCategories = []
        for category in categories:
            img = Database.find(
                collection=Image.COLLECTION,
                query={
                    'categories': category.get('category')},
                sortField='upvotes')

            if img:
                category.update({'image': img.get('image')})
                finalCategories.append(category)
        print(finalCategories)
        return finalCategories

    @staticmethod
    def GetImgsByUserID(userID):
        """
            Finds all images with category provided in the argument
            Returns the cursor (for iterating the Images Collection)
        """
        return Database.find_all(collection=Image.COLLECTION,
                                 query={'userID': userID})

    @staticmethod
    def removeByImgID(img_id):
        """ 
            Deletes Document by img_id 
            in Images Collectionon

            Returns Number of Images Deleted
        """
        return Database.delete(collection=Image.COLLECTION,
                               query={'img_id': img_id})

    @staticmethod
    def removeAllImagesOfUser(userID):
        """ 
            Deletes All Documents by username
            in Images Collection

            Returns Number of Images Deleted

        """
        # Useful while user wants to delete his profile
        return Database.delete_all(collection=Image.COLLECTION,
                                   query={"userID": userID})

    @staticmethod
    def removeAllImages():
        """ 
            Deletes All Documents in Images Collection
            Returns Number of Images Deleted
        """
        result = Database.delete_all(collection=Image.COLLECTION,
                                     query={})
        return result

    @staticmethod
    def updateImgData(img_id, description=None, hashtags=None, Download = None):
        """
            Updates Description of Image (in json)
            In Image Collection

            If Description is updated:
                Returns True
            else:
                Returns None
        """
        print('updateImgData being called')
        img = Image.GetByImgID(img_id)
        if img:
            print('img found!')
            if description:
                img.update({'description': description})
                print('updating description')

            if hashtags:
                hashtags_ = img.get('tags')
                for hashtag in hashtags:
                    if hashtag not in hashtags_:
                        hashtags_.append(hashtag)

                img.update({'tags': hashtags_})
                print('updating tags')

            if Download:
                totalD = img.get('totalDownloads', 0)
                img.update({'totalDownloads': totalD + 1})
                print('updating downloads')

            Database.update(collection=Image.COLLECTION,
                            query={'img_id': img_id},
                            update_query=img)
            return True
        print('img not found!')

    def editComment(self):
        pass

    def editReply(self):
        pass


if __name__ == "__main__":
    Database.initialize('Atypical')
    # img = Image(username='gagan_gulyani', category='random', image='image')
    # img.saveImg()
    # print(Image.removeAllImages())

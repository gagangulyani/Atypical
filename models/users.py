from models.database import Database
from models.images import Image
from models.categories import Category
from models.encryption_ import Encrypt, Decrypt
from uuid import uuid4
from werkzeug import generate_password_hash, check_password_hash
from datetime import datetime
import re


class User(object):

    COLLECTION = "Users"

    def __init__(self,
                 name,
                 email,
                 username,
                 password,
                 age,
                 gender,
                 current_sessions=[],
                 coverPhoto=None,
                 profilePicture=None,
                 about=None,
                 totalUploads=0,
                 totalDownloads=0,
                 totalUpvotes=0,
                 _id=None):

        self.name = name
        self.totalUploads = totalUploads
        self.username = username
        self.email = email
        self.gender = gender
        self.password = User.set_password(password)
        self.coverPhoto = coverPhoto
        self.current_sessions = current_sessions
        self.age = age
        self.profilePicture = profilePicture
        self.about = about
        self.totalDownloads = totalDownloads
        self.totalUpvotes = totalUpvotes
        self._id = _id

    @staticmethod
    def set_password(password):
        return generate_password_hash(password, method='pbkdf2:sha512')

    @staticmethod
    def checkUser(username, password, signUp=False, email=False):
        """
            This function takes username and password
            Returns if one of the following is the Case

                Case 1 : if user is not found = None
                Case 2 : if user is found 
                    a) if password is correct = True
                    b) if password is incorrect = False
        """

        if email:
            result = Database.find(collection=User.COLLECTION,
                                   query={"email": username})
        else:
            result = Database.find(collection=User.COLLECTION,
                                   query={"username": username})

        if signUp:
            if result:
                return User.getUser(result)
            return result

        if result:
            if check_password_hash(result.get("password"), password):
                return result
            else:
                return False

    def saveUser(self):
        """
            Inserts User into the collection
            Returns -1 if User Exists in Users Collection
        """
        if User.checkUser(username=self.username,
                          password=self.password, signUp=True):
            return False

        Database.insert(collection=User.COLLECTION,
                        data=self.toJson())
        return True

    def getUserInfo(self):
        """
            Converts User object to Json Object
            Adds 'created_at' attribute by using '_id'

            Returns Json Object 
        """
        userData = self.toJson()
        userData['created_at'] = Database.created_at(self._id)

        return userData

    @staticmethod
    def createSession(jsonObj):
        """
            Creates a new user session and updates current user document 
            in User Collection

            Returns New User Session
        """

        newSession = Encrypt(str(datetime.utcnow()))
        newSession = [i.decode('utf-8') for i in newSession]

        if jsonObj['current_sessions'] is None:
            jsonObj['current_sessions'] = newSession
        else:
            jsonObj['current_sessions'].append(newSession)

        Database.update(collection=User.COLLECTION,
                        query={'_id': jsonObj['_id']}, update_query=jsonObj)

        # print('updating Database for new session')
        return newSession[0]

    @staticmethod
    def getUserBySession(current_session, logout=False):
        """
            Finds User using Current Session

                If Found:
                    Returns User Object
                Else:
                    Returns None

        """
        result = Database.find_multi(
            collection=User.COLLECTION,
            SearchField='current_sessions', items=[current_session])

        if result:
            return User.getUserByID(result.get('_id'), logout=logout)

    @staticmethod
    def verifySession(current_session):
        return Database.find_multi(collection=User.COLLECTION,
                                   SearchField='current_sessions',
                                   items=[current_session])

    @staticmethod
    def getUserByID(_id, logout=False):
        usr = Database.find(collection=User.COLLECTION, query={'_id': _id})
        if usr:
            usr.pop('password', None)
            # if not logout:
            #     usr.pop('current_sessions', None)
        return usr

    @staticmethod
    def sessionCreatedAt(current_session):
        """ 
            Decrypts the session for cookie

            if session is real, 
                Returns datetime object
            else
                Returns None
        """
        result = User.verifySession(current_session)
        if result:
            result = result.get('current_sessions')
            current_session_encoded = current_session.encode('utf-8')
            key = 0
            for k in result:
                if current_session in k:
                    key = k[1]
                    break
            if key:
                time = Decrypt(enMessage=current_session_encoded,
                               key=key.encode('utf-8'))
                return datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f')

    @staticmethod
    def removeSession(current_session):
        """
            Removes a user session provided from the argument 
            and updates current user document in User Collection

            Returns None
        """
        usr = User.getUserBySession(current_session, logout=True)

        for session in usr.get('current_sessions'):
            if current_session in session:
                ele = session

        usr['current_sessions'].remove(ele)

        Database.update(collection=User.COLLECTION,
                        query={'_id': usr.get('_id')}, update_query=usr)

    def toJson(self):
        """
            Converts User object to json
            (mostly for saving and accessing user)

        """
        return {"name": self.name,
                "email": self.email,
                "username": self.username,
                "totalUploads": self.totalUploads,
                "password": self.password,
                "coverPhoto": self.coverPhoto,
                "gender": self.gender,
                "current_sessions": self.current_sessions,
                "age": self.age,
                "profilePicture": self.profilePicture,
                "about": self.about,
                "totalDownloads": self.totalDownloads,
                "totalUpvotes": self.totalUpvotes}

    @staticmethod
    def getUserByUsername(username, usr=None):
        if not usr:
            usr = Database.find(collection=User.COLLECTION,
                                query={'username': username})
            if usr:
                usr.pop('password', None)
                usr.pop('current_sessions', None)
                usr.update({'createdAt': Database.created_at(usr['_id'])})
                print('user found!')
                return usr

            print('user not found!')
            return None

        return usr

    @staticmethod
    def getImages(_id):
        """
            Returns Images uploaded by the User
        """
        return Image.GetImgsByUserID(_id)

    @staticmethod
    def getImagebyImgID(img_id):
        """
            Returns Image uploaded by the User
            By Using Image ID
        """
        img = Image.GetByImgID(img_id)
        if img:
            userID = img.get('userID')
            usr = User.getUserByID(userID)
            if usr:
                img.update(
                    {'name': usr.get('name'),
                     'profilePicture': usr.get('profilePicture'),
                     'created_at': Database.created_at(img.get('_id'))})
        return img

    @staticmethod
    def vote(_cu, img_id, inc=1, upvote=True):
        img = Image.GetByImgID(img_id)
        if img:
            print('image found')
            userID = img.get('userID')
            voter = User.verifySession(_cu)
            if voter:
                print('voter found')
                usr = User.getUserByID(userID)
                if usr:
                    print('OP found')

                    votes = len(img.get('upvotes')) - len(img.get('downvotes'))
                # subtracting current post's upvotes from User's total upvotes
                    usr.update(
                        {'totalUpvotes': usr.get('totalUpvotes') - votes})

                    if upvote:
                        val = 'upvotes'
                        val2 = 'downvotes'
                    else:
                        val = 'downvotes'
                        val2 = 'upvotes'

                    if voter.get('_id') in img.get(val2):
                        print(f'voter has already {val2} the image')
                        img.get(val2).remove(voter.get('_id'))
                        img.update(
                            {val2: img.get(val2)})
                        print(f'un{val2}ed the image')

                    if voter.get('_id') in img.get(val):
                        print(f'voter has already {val} the image')
                        img.get(val).remove(voter.get('_id'))
                        img.update(
                            {val: img.get(val)})
                        print(f'un{val} the image')

                    else:
                        print(f'previous state of img upvotes: {img.get("upvotes")}')
                        print(f'previous state of img downvotes: {img.get("downvotes")}')

                        votes = img.get(val)
                        votes.append(voter.get('_id'))

                        img.update({val: votes})

                        print(f'Adding {voter.get("_id")} to img')

                        print(f'current state of img upvotes: {img.get("upvotes")}')
                        print(f'current state of img downvotes: {img.get("downvotes")}')

                    votes = len(img.get('upvotes')) - len(img.get('downvotes'))
                    # subtracting current post's upvotes from User's total upvotes
                    usr.update(
                        {'totalUpvotes': usr.get('totalUpvotes') + votes})
                    
                    img.update({'totalUpvotes': votes})

                    Database.update(collection=Image.COLLECTION,
                                    query={'img_id': img.get('img_id')},
                                    update_query=img)

                    Database.update(collection=User.COLLECTION,
                                    query={'_id': usr.get('_id')},
                                    update_query=usr)
                    return True
                return -1
            return -2
        return -3

    @staticmethod
    def getCategories(cat =None):
        imgs = Image.GetImgCategory(cat = cat)
        return imgs

    @staticmethod
    def updateUserInfo(user, _id):
        return Database.update(collection=User.COLLECTION,
                               query={'_id': _id}, update_query=user)

    @staticmethod
    def uploadImage(_cu,
                    categories,
                    image, img_id,
                    description="", hashtags=[]):

        usr = User.verifySession(_cu)
        if usr:
            hashtags_ = re.findall(r"#(\w+)", description)
            if hashtags_:
                hashtags_ = [hashtag.lower() for hashtag in hashtags_]

            hashtags_.extend(hashtags)
            img = Image(userID=usr.get('_id'),
                        categories=categories, image=image,
                        description=description, tags=hashtags_,
                        img_id=img_id)
            img.saveImg()
            
            Category.updateCategories(categories, inc = 1)

            # Category.updateCategory(cat)

            User.updateUploads(_cu)

            return True

        return 0

    @staticmethod
    def deleteUser(_id):
        """
            Deletes User from Users Collection
        """
        return Database.delete(collection=User.COLLECTION,
                               query={"_id": _id})

    @staticmethod
    def deleteAllUsers():
        """
            Deletes All Users from Users Collection
            Returns Number of Users Deleted
        """
        return Database.delete_all(collection=User.COLLECTION,
                                   query={})

    @classmethod
    def getUser(cls, json):
        """
            Takes json object as input and 
            Returns User Object
        """
        return cls(**json)

    @staticmethod
    def getUsers():
        """
            Returns all users present in the 
            Users Collection
        """
        return Database.find_all(collection=User.COLLECTION,
                                 query={})

    @staticmethod
    def updateUploads(_cu, val=1):
        usr = User.verifySession(_cu)
        if usr:
            totalUploads = usr.get('totalUploads')
            totalUploads += val
            usr.update({'totalUploads': totalUploads})
            Database.update(collection=User.COLLECTION,
                            query={"_id": usr.get('_id')},
                            update_query=usr)
            return True

    @staticmethod
    def changePassword(_id, password):

        usr = User.getUserByID(_id)
        if usr:
            usr.update({'password': User.set_password(password)})
            Database.update(collection=User.COLLECTION,
                            query={"_id": usr.get('_id')},
                            update_query=usr)
            return True
        else:
            print(usr)

    @staticmethod
    def changeUsername(_id, username):

        usr = User.getUserByID(_id)
        if usr:
            usr.update({'username': username})
            Database.update(collection=User.COLLECTION,
                            query={"_id": usr.get('_id')},
                            update_query=usr)
            return True

    @staticmethod
    def changeAbout(_id, about):

        usr = User.getUserByID(_id)
        if usr:
            usr.update({'about': about})
            print(usr)
            Database.update(collection=User.COLLECTION,
                            query={"_id": usr.get('_id')},
                            update_query=usr)
            return True

        else:
            print(usr)

    @staticmethod
    def changeCoverPhoto(_cu, coverPhoto):

        usr = User.verifySession(_cu)
        if usr:
            usr.update({'coverPhoto': coverPhoto})
            Database.update(collection=User.COLLECTION,
                            query={"_id": usr.get('_id')},
                            update_query=usr)
            return True

        else:
            print(usr)

    @staticmethod
    def changeProfilePicture(_cu, profilePicture):

        usr = User.verifySession(_cu)
        if usr:
            usr.update({'profilePicture': profilePicture})
            Database.update(collection=User.COLLECTION,
                            query={"_id": usr.get('_id')},
                            update_query=usr)
            return True

        else:
            print(usr)

    @staticmethod
    def changeDescription(description, img_id):
        hashtags = re.findall(r"#(\w+)", description)
        if hashtags:
            hashtags = [hashtag.lower() for hashtag in hashtags]

        print('calling updateImgData')
        return Image.updateImgData(img_id, description, hashtags)


if __name__ == "__main__":
    Database.initialize('Atypical')
    # User.deleteAllUsers()
    # tempUser1 = User(username="gagan_gulyani",
    #                  name="Gagan Gulyani",
    #                  age=20,
    #                  email="gagangulyanig@gmail.com",
    #                  password="test")

    # tempUser1.saveUser()

    # print(User.checkUser('gagan_gulyani', 'test'))

    # tempUser1.deleteUser()

    # users = User.getUsers()

    # print(f"{len(list(users))} user(s) are in Users Collection\n")
    # user_objects = []

    # for user in users:
    #     user_objects.append(User.getUser(user))

    # for user in user_objects:
    #     print(user.getUserInfo())

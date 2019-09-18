class Comment(object):
    def __init__(self,
                 username,
                 profilePicture,
                 comment,
                 upvotes=0,
                 replies=[],
                 _id=None):

        self.username = username
        self.profilePicture = profilePicture
        self.comment = comment
        self.upvotes = upvotes
        self.replies = replies
        self._id = _id

    @classmethod
    def createCommentObj(cls):
        pass

    def toJson(self):
        return {
        "username" : username,
        "profilePicture" : profilePicture,
        "comment" : comment,
        "upvotes" : upvotes,
        "replies" : replies,
        }

    @staticmethod
    def AddComment():
        pass

    @staticmethod
    def RemoveComment():
        pass

    @staticmethod
    def EditComment():
        pass


def Reply(object):

    def __init__(self,
                 username,
                 reply,
                 profilePicture,
                 upvotes=0,
                 _id=None):

        self.username = username
        self.reply = reply
        self.upvotes = upvotes
        self._id = _id
        self.profilePicture = profilePicture

    @classmethod
    def createReplyObj(cls,json):
        pass

    def AddReply(self):
        pass

    def toJson(self):
        return {
        "username" : username,
        "profilePicture" : profilePicture,
        "comment" : comment,
        "upvotes" : upvotes,
        "replies" : replies,
        }

    def EditReply(self):
        pass

    def removeReply(self):
        pass

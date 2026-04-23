from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import datetime
import xmlrpc.client
from socketserver import ThreadingMixIn

from pymongo import MongoClient
# help with mongodb: https://www.mongodb.com/resources/languages/python

# mongoDB config:
client= MongoClient("mongodb://localhost:27017/")

#database
db=client["forumDB"]

#collections
userCollection= db["users"] 
topicsCollection= db["topics"]



# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# The SimpleXMLRPCServer does not handle request
# concurrently but this can be fixed with ThreadingMixIn 
# Source: https://stackoverflow.com/questions/1589150/python-xmlrpc-with-concurrent-requests
class RPCThreading(ThreadingMixIn,SimpleXMLRPCServer):
    pass

# Create server
with RPCThreading(('localhost', 8000),
                        requestHandler=RequestHandler) as server:
    server.register_introspection_functions()

    # used to create timestamp
    def today():
        today = datetime.datetime.today()
        return xmlrpc.client.DateTime(today)
    
    server.register_function(today, "today")


    # and add new posts to mongodb database
    def addPosts(topic, text, timestamp, username):

        # check if topic exists. If not, add it 
        checkTopic= topicsCollection.find_one({"topic": topic})

        # if note exists. update it
        if checkTopic:
            topicsCollection.update_one(
                {"topic": topic},
                {"$push": {
                "posts": {
                    "user": username,
                    "text": text,
                    "timestamp": timestamp
                    }
                }}
            )

        # if it does not, create new 
        else:
            topicsCollection.insert_one({
                "topic": topic,
                "posts": [{
                    "user": username,
                    "text": text,
                    "timestamp": timestamp
                }]
            })
        

        return True

    server.register_function(addPosts, "addPosts")


    # return list of topics to the client.
    def viewAllTopics():

        topics= topicsCollection.find({}, {"_id":0, "topic":1})
        return [t["topic"] for t in topics]
        
    
    server.register_function(viewAllTopics, "viewAllTopics")


    # fetch all data inside one topic that user has requested
    def viewTopicContent(topic):
        print("SEARCH:", topic)
        document= topicsCollection.find_one({"topic": topic})

        # if document does not exist, return empty array
        if not document:
            return []


        # initialize empty array for topics
        topicsArray=[]

        # go through all topics
        for j in document["posts"]:

            # add all names, text and timestamps to topicsArray list
            topicsArray.append((
                j["user"],
                j["text"],
                j["timestamp"]
            ))

        return topicsArray
    server.register_function(viewTopicContent, "viewTopicContent")

    print("Listening on port 8000")
    # Run the server's main loop
    server.serve_forever()

# other sources:

# https://docs.python.org/3/library/xmlrpc.server.html#module-xmlrpc.server
# https://docs.python.org/3/library/xmlrpc.client.html#module-xmlrpc.client

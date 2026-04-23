import bcrypt
from socketserver import ThreadingMixIn
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
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

with RPCThreading(('localhost', 8001),
                        requestHandler=RequestHandler) as server:
    server.register_introspection_functions()


    # help creating register and login functions with bcrypt: https://www.youtube.com/watch?v=YIUNTJEQwQ4
    # and: https://www.geeksforgeeks.org/python/hashing-passwords-in-python-with-bcrypt/

    def registerUser(username, password):
        print("registerUser called")

        hashedPassword = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))


        # check if username exists already
        if userCollection.find_one({"username": username}):
            return False

        # inset new user to the database
        userCollection.insert_one({
            "username": username,
            "password": hashedPassword
        })

        return True
    
    server.register_function(registerUser, "registerUser")
    
    def login(username, password):
        print("login called")
        
        #find user based on username
        user = userCollection.find_one({"username": username})

        #check if the user exists
        if not user:
            return False
        
        #check password
        if bcrypt.checkpw(password.encode(), user["password"]):
            return True
        
        return False
    
    server.register_function(login, "login")

    print("authentication service running on port 8001")
    # Run the server's main loop
    server.serve_forever()
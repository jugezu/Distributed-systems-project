# help with this file: https://medium.com/@coderviewer/building-a-flask-api-gateway-for-grpc-microservices-a-practical-guide-f912aed73b94

#Flask was chosen: https://www.moesif.com/blog/api-product-management/api-analytics/Top-5-Python-REST-API-Frameworks/
# error codes: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status

from flask import Flask, jsonify, request
import xmlrpc.client
import datetime
import jwt

# secrey key for jwt
secretKey = "secret"

app = Flask(__name__)

# RPC services:
forumProxy = xmlrpc.client.ServerProxy("http://localhost:8000/RPC2")
authProxy = xmlrpc.client.ServerProxy("http://localhost:8001/RPC2")


# called when user wants to register using /register
@app.route("/register", methods=["POST"])
def register():
    
    # the user cannot register again after logging in
    if currentUser():
        return jsonify({"error":"Already logged in"}),400
    
    data=request.json

    username= data.get("username")
    password= data.get("password")

    # call registerUser function to register user
    success=authProxy.registerUser(username, password)

    if(success):
        # again using the f string to format the username
        return jsonify({"message": f"User '{username}' registered."}),200

    # registerUser returns false if username already exists
    if success== False:
        return jsonify({"message": f"User '{username}' already exists."}),409 #409=Conflict

    else:
        return jsonify({"message": "Registarion failed."}),400
    

# called when user wants to login. /login
@app.route("/login", methods=["POST"])
def login():

    # the user cannot login again after logging in
    if currentUser():
        return jsonify({"error":"Already logged in"}),400
    
    data= request.json
    username= data.get("username")
    password= data.get("password")
   
    # call authProxy login function that matches user input to the real password and username
    success=authProxy.login(username, password)


    if(success):

        # source for expiration date: https://stackoverflow.com/questions/4557577/in-python-how-do-i-make-a-datetime-that-is-15-minutes-from-now-1-hour-from-now
        # expiration is set to 30 mins
        expirationDate = datetime.datetime.now() + datetime.timedelta(minutes=30)
        
        # help with jwt: https://www.youtube.com/watch?v=FW-XB41RSD0
        # and: # pyJWT: https://pyjwt.readthedocs.io/en/latest/usage.html

        payload={
            "username": username,
            "exp": expirationDate # exp = expiration
        }

        #HS256 is SHA-2526 with HMAC
        encodedToken = jwt.encode(payload, secretKey, algorithm="HS256")

        return jsonify({"message": "Login successful", "token":encodedToken}),200

    # if login fails:
    else:
        return jsonify({"error": "Login failed"}),401 #401= unauthorized
    

# returns username when user is logged in.
# This is used when a route requires authorization such as /add-post
def currentUser():
    auth = request.headers.get("Authorization")

    # check if the user is logged in
    if not auth:
        return None
    
    try:
        token = auth.split(" ")[1]
        
        #decode token and return username
        decodedToken= jwt.decode(token,secretKey, algorithms=["HS256"])
        return decodedToken["username"]

    # trying to catch expected errors that can occur when token expires
    except jwt.ExpiredSignatureError:
        print("expired")
        return None

    except jwt.InvalidTokenError:
        print("Invalid token")
        return None
    


@app.route("/add-post", methods=["POST"])
def addPost():

    # call currentUser to check if user is logged in and has token
    user= currentUser()

    # check if user is not logged in
    if not user:
        return jsonify({"error": "Unauthorized"}),401 #401= unauthorized
    
    data= request.json

    topic= data.get("topic")
    text= data.get("text")

    # convert the string to a datetime object
    timestamp=datetime.datetime.now().strftime("%d.%m.%Y, %H:%M")

    # call addPost to create new post
    forumProxy.addPosts(topic,text,timestamp,user)

    return jsonify({"message": "Post added\n"}),200

#used when the user wants to see list of all topics /list topics
@app.route("/topics", methods=["GET"])
def get_topics():
    
    try:
        topics= forumProxy.viewAllTopics()
        return jsonify(topics)
    
    except Exception as e:
        return jsonify({"error":str(e)}),500
    

#used when the user calls /view <topic name>
@app.route("/topic/<topic>", methods=["GET"])
def viewTopic(topic):

    topicsArray=forumProxy.viewTopicContent(topic)

    # init empty array for results
    result=[]

    # then go through the topicsArray and append the data to the result array
    for u, i, j  in topicsArray:
        result.append({
            "user":u,
            "text":i,
            "timestamp":j
        })
        
    return jsonify(result)

# starts flask
if __name__ == "__main__":
    app.run(port=5000,debug=True)
import requests

# help with colors: https://www.geeksforgeeks.org/python/introduction-to-python-colorama/
from colorama import Fore, init, Style

# initailize Colorama
init()

# initialize user token
token = None

# add new topic or text to existing topics
def addTopic():
    global token
    
    # check token
    if token is None:
        print(Fore.RED+"Login first"+Style.RESET_ALL)
        return

    topic = str(input("Give topic name: ")).strip()

    ## user has to enter topic name. Strip() method removes spaces before and after text
    #Source: https://stackoverflow.com/questions/4113716/remove-characters-from-beginning-and-end-or-only-end-of-line
    
    text = str(input("Give text: ")).strip()
   
    response= requests.post("http://localhost:5000/add-post", json={
        "topic": topic,
        "text": text,
    },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    # check that authorization token is not expired. If it is remove it.
    if response.status_code ==401:
        print(Fore.RED+"Session expired. Please login again."+Style.RESET_ALL)
        token = None
        return

    print(response.json()["message"])

    return


# If the user wants to see all topics, this function is used,
def listTopics():  

    #calling viewAllTopics function that returns all topics
    response= requests.get("http://localhost:5000/topics")

    topicsArray= response.json()
    # if array is empty, print no topics
    if topicsArray == []:
        print(Fore.YELLOW+"No topics"+Style.RESET_ALL)
        print()
        return
    
    print()
    print("--List of All topics--")
    # go through the topicsArray and print each topic
    for i in topicsArray:
        print(i)
    
    print()
    return

def viewTopic(topic):
    print()

    # without the f string the response would be {topic}. To send the actual data
    # f string was used to formats it.
    # source: https://www.geeksforgeeks.org/python/formatted-string-literals-f-strings-python/
    response= requests.get(f"http://localhost:5000/topic/{topic}")
    
    topicsArray= response.json()

    # if topicsArray is empty or does not exist, print message and return
    if not topicsArray:
        print(Fore.YELLOW+"This topic does not exist."+ Style.RESET_ALL)
        print()
        return
    
    #print topic content  
    
    for post in topicsArray:
        print("User:", post["user"])
        print("Text:", post["text"])
        print("Timestamp:", post["timestamp"])
        print()
    return

# called when user wants to register using /register
def register():
    username = str(input("Give username: "))
    while username.strip() == "":
        username = str(input("Give username: "))

    password = str(input("Give password: "))
    while password.strip() == "":    
        password = str(input("Give password: "))

    print()

    # call registerUser function to register user
    response= requests.post("http://localhost:5000/register", json={
        "username": username,
        "password": password
    })

    # when register succees:
    if(response.status_code==200):
        print(Fore.GREEN+response.json()["message"]+ Style.RESET_ALL)

    #check if user exists already
    elif(response.status_code==409):
        print(Fore.RED+response.json()["message"]+ Style.RESET_ALL)

    # if it fails:
    else:
        print(Fore.RED+response.json()["message"]+ Style.RESET_ALL)

    print()
    return

# login called when user types /login and does not have token
def login():
    global token

    username = str(input("Give username: "))
    while username.strip() == "":
        username = str(input("Give username: "))

    password = str(input("Give password: "))
    while password.strip() == "":    
        password = str(input("Give password: "))

    # call apiGateway that tests if user is already logged in and creates JWT for
    # the user 
    response= requests.post("http://localhost:5000/login", json={
        "username": username,
        "password": password
    })
    
    print()

    
    # successfull call returns status code 200.
    if(response.status_code==200):
        print(Fore.GREEN+"Login successful"+Style.RESET_ALL)

        token= response.json()["token"]

    # if login fails:
    else:
        print(Fore.RED+"Login failed"+ Style.RESET_ALL)
    print()
    
    return

def main():
    global token
    # initializing userInput for while loop
    userInput= None

    while userInput != "/quit":

        # if user is not logged in /register and /login is shown to the user
        
        if token == None:

            print("'/register' to register a new user")
            print("'/login' to start posting")
            print("'/list topics' to view all topics")
            print("'/view <topic>' to View contents of single topic")
            print("'/add' to add new topic (requires logging in) ") 
            print("'/quit' to exit")

        # and when user is logged /login and /register are not shown to the user.
        # The user cant use them even if he or she tries.
        else:
            print("'/list topics' to view all topics")
            print("'/view <topic>' to View contents of single topic")
            print("'/add' to add new topic") 
            print("'/quit' to exit")

    
        print()
        userInput=input("Enter input: ")
    
        
        #  in which case /LIST TOPICS written in uppercase also works.
        if userInput.lower() == "/list topics":
            # call the listTopics function, which lists all topics
            listTopics()


        # return contents of the database based on the given topic
        elif userInput.startswith("/view"):

            # /view = [0] <topic> = [1] 
            splitParts= userInput.split(" ", 1)

            if len(splitParts) == 2:
                topic= splitParts[1]
                viewTopic(topic)
            else:
                print(Fore.YELLOW+"usage: /view <topic>"+ Style.RESET_ALL)

        # add new topics
        elif userInput.startswith("/add"):

            # check that user is logged in. 
            # Unregistered users cannot post or create new topics.
            if token is None:
                print(Fore.YELLOW+"User must login to add new posts"+ Style.RESET_ALL)
                print()
            else:
                addTopic()


        elif userInput.lower() == "/register":
            # logged user should not be able to login again
            if token is not None:
                print(Fore.YELLOW+"You are already logged in"+ Style.RESET_ALL)
                print()

            else:
                register()
            
        elif userInput.lower() == "/login":
            # logged user should not be able to login again
            if token is not None:
                print(Fore.YELLOW+"You are already logged in."+ Style.RESET_ALL)
                print()

            else:
                login()

        # /quit to logout
        elif userInput.lower() == "/quit":
            print("Thank you for using the program.")
            token=None
            break
        
        # if user writes something else print 'Unknown command'
        else:
            print(Fore.YELLOW+"Unknown command"+ Style.RESET_ALL)
            print()

    return

# call the main function
main()
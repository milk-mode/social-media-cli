import sys

import pymongo
import uuid
from datetime import datetime
from bson import Binary

client = pymongo.MongoClient("mongodb://localhost:27017/")
database = client["social_media"]
users_collection = database["users"]
posts_collection = database["posts"]
followers_collection = database["followers"]

logged_in = False
user_document_id = ""


def user_registration(username_param, password_param):
    # take username,password
    # store in db
    user_existing = users_collection.find_one({"username": username_param})
    if not user_existing:
        users_collection.insert_one(
            {"_id": Binary(uuid.uuid4().bytes, 4), "username": username_param, "password": password_param,
             "Registered at": datetime.now()})
        print("\n** User registered successfully **")
    elif user_existing:
        print("\n** username exists,select another username **")
    menu()


def user_login(username_input, password_input):
    # ask for username,password
    # fetch from database
    global user_document_id
    global logged_in

    user_document = users_collection.find_one({"username": username_input, "password": password_input})
    if user_document:
        logged_in = True
        user_document_id = user_document.__getitem__("_id")
        print("\n** login success **")

    if not user_document:
        logged_in = False
        print("\n** Invalid credentials **")
    menu()


def post_messages(message_param):
    # logged in/existing user?
    # post message
    posts_collection.insert_one(
        {"_id": Binary(uuid.uuid4().bytes, 4), "user-id": user_document_id, "message": message_param})
    print("** post successful **")
    menu()


def follow_unfollow(user_name, task):
    # logged in/existing user?
    # follow which user - get list of users
    # unfollow which user-get list of users

    if logged_in and task == 'follow':
        user_doc = users_collection.find_one({"username": user_name})
        followers_collection.insert_one(
            {"_id": Binary(uuid.uuid4().bytes, 4), "user_id": user_doc.get("_id"),
             "username": user_doc.get("username")})
        print("\n** follow successful **")
        menu()

    if logged_in and task == 'unfollow':
        user_doc = users_collection.find_one({"username": user_name})
        followers_collection.delete_one({"username": user_doc.get("username")})
        print("** unfollow successful **")
        menu()

    print("\n** please login before following or unfollowing a user **")
    menu()


def view_user_feed(username_feed):
    # See list of messages posted from which user-get list of users ->posted_messages
    follower = followers_collection.find_one({"username": username_feed})
    if follower.get("message"):
        print(follower.get("message"))
    elif not follower.get("message"):
        print("\n** There are no posts from that user **")
    menu()


def display_users():
    documents = list(users_collection.find())
    if documents:
        for i in range(0, len(documents)):
            documents[i]['_id'] = uuid.UUID(bytes=documents[i]['_id'])
        for document in documents:
            print(document)
    elif not documents:
        print("\n** No users found **")
        menu()


def menu():
    global logged_in
    print("\nMENU")
    print("====")
    print("1. Register as a user, press 'R' or 'r'")
    print("2. Login as existing user, press 'L' or 'l'")
    print("3. Post a new message, press 'P' or 'p'")
    print("4. Follow a user, press 'F' or 'f'")
    print("5. Unfollow a user,press 'U' or 'u'")
    print("6. View user feed, press 'V' or 'v'")
    print("7. Log out current user: 'O' or 'o'")
    print("8. press 'E' or 'e' to exit program")
    choice = str(input("\nEnter choice:  "))

    if choice == 'R' or choice == 'r':
        username_reg = str(input("\nEnter username: "))
        password_reg = str(input("Enter password: "))
        user_registration(username_reg, password_reg)
    elif choice == 'L' or choice == 'l':
        username_input = str(input("\nEnter username for login: "))
        password_input = str(input("Enter password for login: "))
        user_login(username_input, password_input)
    elif choice == 'P' or choice == 'p':
        if logged_in:
            message = str(input("\nEnter post message: "))
            post_messages(message)
        else:
            print("\n** please login before posting a message **")
            menu()
    elif choice == 'F' or choice == 'f':
        display_users()
        username = str(input("\nEnter the username of the person you want to follow from the list: "))
        follow_unfollow(username, 'follow')
    elif choice == 'U' or choice == 'u':
        username = str(input("\nEnter the username of the person you want to unfollow from the list: "))
        display_users()
        follow_unfollow(username, 'unfollow')
    elif choice == 'V' or choice == 'v':
        if logged_in:
            username = str(input("\nEnter the username of the person you want view: "))
            view_user_feed(username)
        else:
            print("\n** please login before viewing a feed **")
            menu()
    elif choice == 'O' or choice == 'o':
        logged_in = False
        print("\n** log out success **")
        menu()
    elif choice == 'E' or choice == 'e':
        sys.exit(0)
    else:
        print("** Invalid choice **,choose again: ")
        menu()


print("Welcome to the social media cli,choose operation:")
print("------- -- --- ------ ----- ------ ---------")
menu()

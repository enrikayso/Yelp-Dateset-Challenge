import json
from tkinter import *
from tkinter.ttk import *
import psycopg2
import tkinter as tk


window = tk.Tk()
window.title("User UI")
window.geometry("1500x900")
conn = psycopg2.connect("dbname='milestone2' user='postgres' host='localhost' password='solarion'")
cur = conn.cursor()

userListBox = Listbox(window)
un = ''


def login_clicked():
    global userListBox, un

    un = login.get(1.0, "end-1c")
    cur.execute("SELECT user_id, uname FROM users WHERE uname = '%s' ORDER BY uname" % un)
    userList = cur.fetchall()
    userVars = StringVar(value=userList)
    userListBox = Listbox(window, listvariable=userVars)
    userListBox.grid(row=3, column=0)
    userListBox.bind("<<ListboxSelect>>", user_selected)


def user_selected(event):
    global userListBox

    temp = userListBox.curselection()
    uid = userListBox.get(temp)
    uid = uid[0]

    cur.execute("SELECT uname, average_stars, yelping_since, fans, tipCount, totalLikes, "
                "user_latitude, user_longitude FROM users WHERE user_id = '%s'" % uid)
    user_info = cur.fetchall()
    print(user_info)
    print(type(user_info))
    user_info_Vars = StringVar(value=user_info)

    #
    # print(user_info_Vars)
    # print(user_info_Vars[0])
    # print(type(user_info_Vars))


    userInfoBox = tk.Text(window, height=2, width=40)
    # userName = Entry(window)
    userInfoBox.grid(row=0, column=2)
    userInfoBox.insert('end', user_info)




    cur.execute("SELECT uname FROM users WHERE user_id = '%s'" % uid)
    uname = cur.fetchall()
    user_name = tk.Text(window, height=2, width=20)
    user_name.grid(row=1, column=2)
    user_name.insert('end', uname)

    cur.execute("SELECT average_stars FROM users WHERE user_id = '%s'" % uid)
    average_stars = cur.fetchall()
    average_stars_tb = tk.Text(window, height=2, width=20)
    average_stars_tb.grid(row=2, column=2)
    average_stars_tb.insert('end', average_stars)

    cur.execute("SELECT yelping_since FROM users WHERE user_id = '%s'" % uid)
    yelping_since = cur.fetchall()
    yelping_since_tb = tk.Text(window, height=2, width=20)
    yelping_since_tb.grid(row=3, column=2)
    yelping_since_tb.insert('end', yelping_since)

    cur.execute("SELECT fans FROM users WHERE user_id = '%s'" % uid)
    fans = cur.fetchall()
    fans_tb = tk.Text(window, height=2, width=20)
    fans_tb.grid(row=4, column=2)
    fans_tb.insert('end', fans)

    cur.execute("SELECT tipCount FROM users WHERE user_id = '%s'" % uid)
    tipCount = cur.fetchall()
    tipCount_tb = tk.Text(window, height=2, width=20)
    tipCount_tb.grid(row=5, column=2)
    tipCount_tb.insert('end', tipCount)

    cur.execute("SELECT totalLikes FROM users WHERE user_id = '%s'" % uid)
    totalLikes = cur.fetchall()
    totalLikes_tb = tk.Text(window, height=2, width=20)
    totalLikes_tb.grid(row=6, column=2)
    totalLikes_tb.insert('end', totalLikes)

    cur.execute("SELECT user_latitude FROM users WHERE user_id = '%s'" % uid)
    user_latitude = cur.fetchall()
    user_latitude_tb = tk.Text(window, height=2, width=20)
    user_latitude_tb.grid(row=7, column=2)
    user_latitude_tb.insert('end', user_latitude)

    cur.execute("SELECT user_longitude FROM users WHERE user_id = '%s'" % uid)
    user_longitude = cur.fetchall()
    user_longitude_tb = tk.Text(window, height=2, width=20)
    user_longitude_tb.grid(row=8, column=2)
    user_longitude_tb.insert('end', user_longitude)

    cur.execute(
        "SELECT users.uname, totalLikes, average_stars, yelping_since FROM users inner join (SELECT * FROM friends WHERE user_id = '%s') user_friends"
                " ON users.user_id = user_friends.friend_id" %uid)
    friends_info = cur.fetchall()
    # print(friends_info)

    user_friends_tb = tk.Text(window, height=20, width=40)
    user_friends_tb.grid(row=0, column=3)
    user_friends_tb.insert('end', 'Name|Total Likes|Avg Stars|Yelping Since\n')
    user_friends_tb.insert('end', friends_info)

    cur.execute("SELECT user_id, uname FROM users WHERE uname = '%s' ORDER BY uname" % un)
    friends_tips = cur.fetchall()
    friends_tips_tb = tk.Text(window, height=20, width=40)
    friends_tips_tb.grid(row=1, column=3)
    friends_tips_tb.insert('end', 'Name|Business|City|Text|Date\n')
    user_friends_tb.insert('end', friends_tips)


if __name__ == "__main__":

    #selecting user
    setCurrentUserLabel = Label(window, text="Set Current User").grid(row=0, column=0)
    # login = Entry(window)
    login = tk.Text(window, height=1, width=20)
    login.grid(row=1, column=0, sticky='n')
    login_button = tk.Button(window, text="Login", command=login_clicked)
    login_button.grid(row=2, column=0, sticky='n')
    # stateListBox = Listbox(window)
    # userListBox.grid(row=3, column=0)



    #displaying users friends
    setFriendsLabel = Label(window, text="Friends").grid(row=4, column=0)
    friendsListBox = Listbox(window)
    friendsListBox.grid(row=5, column=0)

    #displaying user information
    setUserInfoLabel = Label(window, text="User Information").grid(row=0, column=1)
    setNameLabel = Label(window, text="Name:").grid(row=1, column=1)
    # userName = Entry(window)
    # userName.grid(row=1, column=2)

    setStarsLabel = Label(window, text="Stars:").grid(row=2, column=1)
    # Stars = Entry(window)
    # Stars.grid(row=2, column=2)

    # setFansLabel = Label(window, text="Fans:").grid(row=2, column=3)
    setFansLabel = Label(window, text="Fans:").grid(row=4, column=1)

    # Fans = Entry(window)
    # Fans.grid(row=2, column=4)

    setYelpingSinceLabel = Label(window, text="Yelping Since:").grid(row=3, column=1)
    # YelpingSince = Entry(window)
    # YelpingSince.grid(row=3, column=2)

    setVotesLabel = Label(window, text="Votes:").grid(row=4, column=1)

    setFunnyLabel = Label(window, text="funny:").grid(row=4, column=2)
    # Funny = Entry(window)
    # Funny.grid(row=5, column=2)

    # setCoolLabel = Label(window, text="cool:").grid(row=4, column=3)
    # # Cool = Entry(window)
    # # Cool.grid(row=5, column=3)
    #
    # setUsefulLabel = Label(window, text="useful:").grid(row=4, column=4)
    # Useful = Entry(window)
    # Useful.grid(row=5, column=4)

    # setTipCountLabel = Label(window, text="Tip Count:").grid(row=6, column=1)
    setTipCountLabel = Label(window, text="Tip Count:").grid(row=5, column=1)

    # TipCount = Entry(window)
    # TipCount.grid(row=6, column=2)

    # setTotalTipLikesLabel = Label(window, text="Total Tip Likes:").grid(row=7, column=1)
    setTotalTipLikesLabel = Label(window, text="Total Tip Likes:").grid(row=6, column=1)

    # TotalTipLikes = Entry(window)
    # TotalTipLikes.grid(row=7, column=2)

    # setLocationLabel = Label(window, text="Location:").grid(row=8, column=1)

    # setLatLabel = Label(window, text="Latitude:").grid(row=9, column=1)
    setLatLabel = Label(window, text="Latitude:").grid(row=7, column=1)

    # Latitude = Entry(window)
    # Latitude.grid(row=9, column=2)
    # LatitudeBtn = Button(window, text="Edit")
    # LatitudeBtn.grid(row=9, column=3)

    # setLongLabel = Label(window, text="Longitude").grid(row=10, column=1)
    setLongLabel = Label(window, text="Longitude").grid(row=8, column=1)
    # Longitude = Entry(window)
    # Longitude.grid(row=10, column=2)
    # LongitudeBtn = Button(window, text="Update")
    # LongitudeBtn.grid(row=10, column=3)

    setFriendTipsLabel = Label(window, text="Latest tips of my friends?").grid(row=0, column=5)
    FriendsTipsListBox = Listbox(window)
    FriendsTipsListBox.grid(row=1, column=5)

    window.mainloop()
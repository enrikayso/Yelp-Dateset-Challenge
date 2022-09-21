import json
from tkinter import *
from tkinter.ttk import *
import psycopg2


root = Tk()
root.title("Yelp Database")
root.geometry("1500x900")
conn = psycopg2.connect("dbname='milestone2' user='postgres' host='localhost' password='psswrd'")
#conn = psycopg2.connect("dbname='milestone1db' user='postgres' host='localhost' password=''")
cur = conn.cursor()
trueAttributes = 0

filterAttributeList = []
filterPriceList = []

stateIsSelected = False
selectedState = ''
stateList = ["SELECT DISTINCT state FROM business ORDER BY state"]
cityList = ["SELECT DISTINCT city FROM business ORDER BY city"]
selected_zipcode = ''

cur = conn.cursor()
cur.execute("SELECT DISTINCT state FROM business ORDER BY state")
stateList = cur.fetchall()
stateVars = StringVar(value=stateList)
stateListBox = Listbox(root,
listvariable=stateVars)


cur = conn.cursor()
cur.execute("SELECT DISTINCT city FROM business ORDER BY city")
cityList = cur.fetchall()
cityVars = StringVar(value=cityList)
cityListBox = Listbox(root,listvariable=cityVars)
#cityListBox.delete(0,END)
#cur.close()


cur = conn.cursor()
cur.execute("SELECT DISTINCT zipcode FROM business ORDER BY zipcode")
zipCodeList = cur.fetchall()
#zipCodeVars = StringVar(value=zipCodeList)
#zipCodeListBox = Listbox(root)#,listvariable=zipCodeVars)

categoryListBox = Listbox(root)
attributeListBox = Listbox(root)
bnameListBox = Listbox(root)
priceRangeListBox = Listbox(root)
mealsListBox = Listbox(root)
bnameList = []
bidList = []

####Ideally, at most 3 categories, 2 attributes, 2 prices, 2 meals.
blanketCategories = []
blanketAttributes = []
blanketPrice = []
blanketMeals = []

tipMessage = Message(root)
#searchButton = Button(root)
tipEntry = Entry(root, width=40)
tipEntry.grid(row=6, column=1)
tipEntry_label = Label(root, text="Add new tip!")
tipEntry_label.grid(row=6,column=0)

tipToAdd = ''
selected_business_id = ''
tipList = []


def cleanStr4SQL(s):
    return s.replace("'", "`").replace("\n", " ")


def flatten_json(obj):
    ret = {}

    # recursive function
    def flatten(x, flattened_key=""):
        # we want to loop over the keys in the object
        # and flatten
        if type(x) is dict:
            for curr_key in x:
                # we are appending the nested keys to the original
                flatten(x[curr_key], curr_key + '_')
        else:
            # base case: not at a list or object or dict (i.e. at a single string)
            # meaning x will be a string, integer, etc
            # take our flattened key and add it to our return object
            ret[flattened_key[:-1]] = x

    flatten(obj)
    return ret.items()


def parseBusinessData():
    # read the JSON file
    # We assume that the Yelp data files are available in the current directory. If not, you should specify the path when you "open" the function. 
    with open('.\DBPopulate\yelp_business.JSON', 'r') as f:
        outfile = open('.//business.txt', 'w')
        line = f.readline()
        count_line = 0
        # read each JSON abject and extract data
        while line:
            data = json.loads(line)
            outfile.write("{} - business info : '{}' ; '{}' ; '{}' ; '{}' ; '{}' ; '{}' ; {} ; {} ; {} ; {}\n".format(
                str(count_line),  # the line count
                cleanStr4SQL(data['business_id']),
                cleanStr4SQL(data["name"]),
                cleanStr4SQL(data["address"]),
                cleanStr4SQL(data["state"]),
                cleanStr4SQL(data["city"]),
                cleanStr4SQL(data["postal_code"]),
                str(data["latitude"]),
                str(data["longitude"]),
                str(data["stars"]),
                str(data["is_open"])))

            # process business categories
            categories = data["categories"].split(', ')
            outfile.write("      categories: {}\n".format(str(categories)))

            # TO-DO : write your own code to process attributes
            # make sure to **recursively** parse all attributes at all nesting levels. You should not assume a particular nesting level.

            attributes = data["attributes"]
            outfile.write("      attributes: {}\n".format(str(flatten_json(attributes))))

            # TO-DO : write your own code to process hours data

            hours = data["hours"]
            businessHours = []
            for day in hours:
                hours_str = "('" + day + "','" + \
                             hours[day].split("-")[0] + "','" + hours[day].split("-")[1] + "')"
                businessHours.append(hours_str)
            outfile.write("      hours: {}".format(str(flatten_json(businessHours))))

            outfile.write("")

            outfile.write('\n')

            line = f.readline()
            count_line += 1
    print(count_line)
    outfile.close()
    f.close()

def insert2BusinessTable():
    #reading the JSON file
    with open('.\DBPopulate\yelp_business.JSON', 'r') as f:    #TO-DO: update path for the input file
        line = f.readline()
        count_line = 0
        #connect to yelpdb database on postgres server using psycopg2
        try:
            #TO-DO: update the database name, username, and password
            conn = psycopg2.connect("dbname='milestone2' user='postgres' host='localhost' password='psswrd'")
        except:
            print('Unable to connect to the database!')
        cur = conn.cursor()
        while line:
            data = json.loads(line)
            # Generate the INSERT statement for the current business
            # TO-DO: The below INSERT statement is based on a simple (and incomplete) businesstable schema. Update the statement based on your own table schema and
            # include values for all businessTable attributes
            try:
                cur.execute("INSERT INTO Business (business_id, bname, address, state, city, zipcode, latitude, longitude, stars, numCheckins, numTips, is_open)"
                       + " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (data['business_id'], cleanStr4SQL(data["name"]), cleanStr4SQL(data["address"]),
                         data["state"], data["city"], data["postal_code"], data["latitude"], data["longitude"],
                         data["stars"], 0, 0, [False, True][data["is_open"]]))
            except Exception as e:
                print("Insert to businessTABLE failed!", e)
            conn.commit()
            line = f.readline()
            count_line += 1
        cur.close()
        conn.close()
    print(count_line)
    f.close()

def parseUserData():
    # TO-DO : write code to parse yelp_user.JSON
    #read the JSON file
    # We assume that the Yelp data files are available in the current directory. If not, you should specify the path when you "open" the function.
    with open('.\DBPopulate\yelp_user.JSON', 'r') as f:
        outfile =  open('.//user.txt', 'w')
        line = f.readline()
        count_line = 0
        #read each JSON abject and extract data
        while line:
            data = json.loads(line)
            outfile.write("{} - user info : '{}' ; '{}' ; '{}' ; '{}' ; '{}' ; '{}'\n".format(
                              str(count_line), # the line count
                              cleanStr4SQL(data['user_id']),
                              cleanStr4SQL(data["name"]),
                              cleanStr4SQL(data["yelping_since"]),
                              str(data["tipcount"]),
                              str(data["fans"]),
                              str(data["average_stars"])
                              #str(data["account_reviews"])
                            )
                        )

            # TO-DO : write your own code to process friends

            friends = data["friends"]
            outfile.write("      friends: {}\n".format(str(flatten_json(friends))))

            outfile.write("")

            outfile.write('\n')

            line = f.readline()
            count_line +=1
    print(count_line)
    outfile.close()
    f.close()
    pass

def insert2UserTable():
    #reading the JSON file
    with open('.\DBPopulate\yelp_user.JSON', 'r') as f:    # TO-DO: update path for the input file
        #outfile =  open('./yelp_business_out.SQL', 'w')  #uncomment this line if you are writing the INSERT statements to an output file.
        line = f.readline()
        count_line = 0
        #connect to yelpdb database on postgres server using psycopg2
        try:
            #TO-DO: update the database name, username, and password
            conn = psycopg2.connect("dbname='milestone2' user='postgres' host='localhost' password='psswrd'")
        except:
            print('Unable to connect to the database!')
        cur = conn.cursor()
        while line:
            data = json.loads(line)
            try:
                cur.execute("INSERT INTO Users (user_id, uname, average_stars, fans, cool, tipCount, funny, totalLikes, useful, user_latitude, user_longitude, yelping_since)" +
                            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                            (cleanStr4SQL(data['user_id']), cleanStr4SQL(data["name"]),
                             (data["average_stars"]), data["fans"],  data["cool"],
                             data["tipcount"], data["funny"], (data["cool"] + data["funny"] + data["useful"]), data["useful"], 0, 0,
                             cleanStr4SQL(data["yelping_since"])))
            except Exception as e:
                print("Insert to usersTABLE failed!", e)
            conn.commit()
            line = f.readline()
            count_line += 1
        cur.close()
        conn.close()
    print(count_line)
    f.close()


def parseCheckinData():
    pass
    # TO-DO : write code to parse yelp_checkin.JSON
    #read the JSON file
    # We assume that the Yelp data files are available in the current directory. If not, you should specify the path when you "open" the function.


    with open('.\DBPopulate\yelp_checkin.JSON','r') as f:
        outfile =  open('.//checkin.txt', 'w')
        line = f.readline()
        count_line = 0
        #read each JSON abject and extract data
        while line:
            data = json.loads(line)
            outfile.write("{}- '{}': \n".format(
                              str(count_line), # the line count
                              cleanStr4SQL(data['business_id']),
                              #cleanStr4SQL(data["date"])
                            )
                        )

            # TO-DO : write your own code to process date

            friends = data["date"]
            date = friends.split(',')
            i = 0
            # year = ''
            # month = ''
            # day = ''
            # time = ''
            while i < len(date):
                outfile.write("(" + "'" + date[i][:4] + "'" + "," + "'" + date[i][5:7] + "'" + "," + "'" + date[i][8:10] + "'" + "," + "'" + date[i][11:19] + "'" + ")")
                outfile.write("")
                i = i + 1
                # year = date[i][:4]
                # month = date[i][5:7]
                # day = date[i][8:10]
                # time = date[i][11:19]

            outfile.write("")
            outfile.write('\n')

            line = f.readline()
            count_line +=1
    #print(count_line)
    outfile.close()
    f.close()

def insert2CheckinTable():
    #reading the JSON file
    with open('.\DBPopulate\yelp_checkin.JSON', 'r') as f:    # TO-DO: update path for the input file
        #outfile =  open('./yelp_business_out.SQL', 'w')  #uncomment this line if you are writing the INSERT statements to an output file.
        line = f.readline()
        count_line = 0
        #connect to yelpdb database on postgres server using psycopg2
        try:
            #TO-DO: update the database name, username, and password
            conn = psycopg2.connect("dbname='milestone2' user='postgres' host='localhost' password='psswrd'")
        except:
            print('Unable to connect to the database!')
        cur = conn.cursor()
        while line:
            data = json.loads(line)
            try:
                friends = data["date"]
                date = friends.split(',')
                year = ''
                month = ''
                day = ''
                time = ''
                i = 0
                while i < len(date):
                    year = date[i][:4]
                    month = date[i][5:7]
                    day = date[i][8:10]
                    time = date[i][11:19]
                    i += 1
                cur.execute("INSERT INTO Checkins (business_id, year, month, day, time)" +
                            "VALUES (%s, %s, %s, %s, %s)",
                            (cleanStr4SQL(data['business_id']), year, month, day, time))
            except Exception as e:
                print("Insert to checkinTABLE failed!", e)
            conn.commit()
            line = f.readline()
            count_line += 1
        cur.close()
        conn.close()
    print(count_line)
    f.close()


def parseTipData():
    # TO-DO : write code to parse yelp_tip.JSON
    with open('.\DBPopulate\yelp_tip.JSON', 'r') as f:
        outfile = open('.//tip.txt', 'w')
        line = f.readline()
        count_line = 0
        # read each JSON abject and extract data
        while line:
            data = json.loads(line)
            outfile.write("{} - business info : '{}' ; '{}' ; '{}' ; '{}' ; '{}'\n".format(
                str(count_line),  # the line count
                cleanStr4SQL(data['business_id']),
                cleanStr4SQL(data["date"]),
                int(data["likes"]),
                cleanStr4SQL(data["text"]),
                cleanStr4SQL(data["user_id"])))

            outfile.write("")

            outfile.write('\n')

            line = f.readline()
            count_line += 1
    print(count_line)
    outfile.close()
    f.close()

def insert2TipTable():
    # reading the JSON file; TO-DO: update path for the inputfile
    with open('.\DBPopulate\yelp_tip.JSON', 'r') as f:
        line = f.readline()
        count_line = 0

        # connect to yelpdb database on postgres server using psycopg2
        try:
            # -- TO-DO: update the database name, username, and password
            conn = psycopg2.connect("dbname='milestone2' user='postgres' host='localhost' password='psswrd'")

        except:
            print('Unable to connect to the database!')
        cur = conn.cursor()

        while line:
            data = json.loads(line)
            # -- Generate the INSERT statement for the current tip

            try:
                cur.execute("INSERT INTO Tip (user_id, business_id, tipDate, tipText, likes)"
                            + " VALUES (%s, %s, %s, %s, %s)",
                            (cleanStr4SQL(data['user_id']), cleanStr4SQL(data['business_id']),
                             cleanStr4SQL(data['date']), data['text'], data['likes']))

            except Exception as e:
                print("Insert to tipTABLE failed!", e)
            conn.commit()

            line = f.readline()
            count_line += 1

        cur.close()
        conn.close()

    print(count_line)
    f.close()


def insert2CategoriesTable():
    #reading the JSON file
    with open('.\DBPopulate\yelp_business.JSON','r') as f:    # TO-DO: update path for the input file
        #outfile =  open('./yelp_business_out.SQL', 'w')  #uncomment this line if you are writing the INSERT statements to an output file.
        line = f.readline()
        count_line = 0
        #connect to yelpdb database on postgres server using psycopg2
        try:
            #TO-DO: update the database name, username, and password
            conn = psycopg2.connect("dbname='milestone2' user='postgres' host='localhost' password='psswrd'")
        except:
            print('Unable to connect to the database!')
        cur = conn.cursor()
        while line:
            data = json.loads(line)
            try:
                cur.execute("INSERT INTO Categories (business_id, category_name)" +
                            "VALUES (%s, %s)",
                            (cleanStr4SQL(data['business_id']), data["categories"]))
            except Exception as e:
                print("Insert to businessTABLE failed!", e)
            conn.commit()
            line = f.readline()
            count_line += 1
        cur.close()
        conn.close()
    print(count_line)
    f.close()

def insert2AttributesTable():
    #reading the JSON file
    with open('.\DBPopulate\yelp_business.JSON', 'r') as f:    # TO-DO: update path for the input file
        # #outfile =  open('./yelp_business_out.SQL', 'w')  #uncomment this line if you are writing the INSERT statements to an output file.
        line = f.readline()
        count_line = 0

        data = json.loads(line)

        #connect to yelpdb database on postgres server using psycopg2
        try:
            #TO-DO: update the database name, username, and password
            conn = psycopg2.connect("dbname='milestone2' user='postgres' host='localhost' password='psswrd'")
        except:
            print('Unable to connect to the database!')
        cur = conn.cursor()
        while line:
            data = json.loads(line)
            try:
                raw_dict = data["attributes"]
                attribute_list = []
                att_value_list = []
                add = True

                def parseNestedDict(dic, add):
                    for item in dic:
                        if isinstance(dic.get(item), dict):
                            attribute_list.append(item)
                            # att_value_list.append()
                            parseNestedDict(dic.get(item), False)
                        attribute_list.append(item)
                        att_value_list.append(dic.get(item))


                parseNestedDict(raw_dict, add)

                seen = set()
                dupes = [x for x in attribute_list if x in seen or seen.add(x)]
                seen = set()
                attribute_list = [x for x in attribute_list if x not in seen and not seen.add(x)]
                attribute_list = [x for x in attribute_list if x not in dupes]
                for item in att_value_list:
                    if isinstance(item, dict):
                        att_value_list.remove(item)

                cur.execute("INSERT INTO Attributes (business_id, attr_name, value)" +
                            "VALUES (%s, %s, %s)",
                            (cleanStr4SQL(data['business_id']), attribute_list, att_value_list))
            except Exception as e:
                print("Insert to attributesTABLE failed!", e)
            conn.commit()
            line = f.readline()
            count_line += 1
        cur.close()
        conn.close()

    print(count_line)
    f.close()

def insert2HoursTable():
    #reading the JSON file
    with open('.\DBPopulate\yelp_business.JSON', 'r') as f:    # TO-DO: update path for the input file
        #outfile =  open('./yelp_business_out.SQL', 'w')  #uncomment this line if you are writing the INSERT statements to an output file.
        line = f.readline()
        count_line = 0
        data = json.loads(line)

        #connect to yelpdb database on postgres server using psycopg2
        try:
            #TO-DO: update the database name, username, and password
            conn = psycopg2.connect("dbname='milestone2' user='postgres' host='localhost' password='psswrd'")
        except:
            print('Unable to connect to the database!')
        cur = conn.cursor()
        while line:
            data = json.loads(line)
            try:
                    raw_dict = data["hours"]
                    dayofweek = []
                    hours = []
                    open_hours = []
                    closed_hours = []

                    def parseNestedDict(dic):
                        for item in dic:
                            if isinstance(dic.get(item), dict):
                                dayofweek.append(item)
                                # att_value_list.append()
                                parseNestedDict(dic.get(item))
                            dayofweek.append(item)
                            hours.append(dic.get(item))

                    parseNestedDict(raw_dict)

                    hours_clean = str(hours).split('-')
                    # remove_char = '[]'
                    hours_clean = str(hours_clean).replace('[', '')
                    hours_clean = str(hours_clean).replace(']', '')
                    hours_clean = str(hours_clean).replace('\'', '')
                    hours_clean = str(hours_clean).replace('\"', '')
                    hours_clean = str(hours_clean).replace(',', '')
                    hours_clean = hours_clean.split(' ')
                    # open_hours = str(open_hours).replace(']', '')
                    i = 0
                    while i < len(hours_clean):
                        if i % 2 == 0:
                            open_hours.append(hours_clean[i])
                        else:
                            closed_hours.append(hours_clean[i])
                        i += 1

                    cur.execute("INSERT INTO Hours (business_id, dayOfWeek, close, open)" +
                            "VALUES (%s, %s, %s, %s)",
                            (cleanStr4SQL(data['business_id']), dayofweek, closed_hours, open_hours))
            except Exception as e:
                print("Insert to businessTABLE failed!", e)
            conn.commit()
            line = f.readline()
            count_line += 1
        cur.close()
        conn.close()
    print(count_line)
    f.close()


def blanket_search():

    global blanketAttributes, blanketCategories, blanketMeals, blanketPrice, selected_zipcode
    if type(selected_zipcode) is tuple:
        selected_zipcode = selected_zipcode[0]
    print("blanketATTRIBUTES: ", blanketAttributes)
    print("blanketCATEGORIES: ", blanketCategories)
    print("blanketPRICES: ", blanketPrice)

    ###NO CATEGORIES SELECTED
    if len(blanketCategories) == 0:
        ###NO PRICES SELECTED
        if len(blanketPrice) == 0:
            ###ONE ATTRIBUTE SELECTED
            if len(blanketAttributes) == 1:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketAttributes[0]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 2:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketAttributes[0],blanketAttributes[1]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 3:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketAttributes[0],blanketAttributes[1],blanketAttributes[2]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 4:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketAttributes[0],blanketAttributes[1],blanketAttributes[2],blanketAttributes[3]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 5:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketAttributes[0],blanketAttributes[1],blanketAttributes[2],blanketAttributes[3],blanketAttributes[4]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
        ###ONE PRICE SELECTED
        elif len(blanketPrice) == 1:
            ###NO ATTRIBTUES SELECTED
            if len(blanketAttributes) == 0:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s')" %(selected_zipcode, blanketPrice[0]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 1:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketPrice[0], blanketAttributes[0]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 2:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketPrice[0], blanketAttributes[0],blanketAttributes[1]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 3:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketPrice[0], blanketAttributes[0],blanketAttributes[1],blanketAttributes[2]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 4:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode,blanketPrice[0], blanketAttributes[0],blanketAttributes[1],blanketAttributes[2],blanketAttributes[3]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 5:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketPrice[0],blanketAttributes[0],blanketAttributes[1],blanketAttributes[2],blanketAttributes[3],blanketAttributes[4]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

    elif len(blanketCategories) == 1:
        if len(blanketPrice) == 0:
            ###ONE ATTRIBUTE SELECTED
            if len(blanketAttributes) == 0:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s')" %(selected_zipcode,blanketCategories[0]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 1:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode,blanketCategories[0], blanketAttributes[0]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 2:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketCategories[0], blanketAttributes[0],blanketAttributes[1]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 3:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketCategories[0],blanketAttributes[0],blanketAttributes[1],blanketAttributes[2]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 4:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketCategories[0],blanketAttributes[0],blanketAttributes[1],blanketAttributes[2],blanketAttributes[3]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 5:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketCategories[0],blanketAttributes[0],blanketAttributes[1],blanketAttributes[2],blanketAttributes[3],blanketAttributes[4]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                
        ###ONE PRICE SELECTED
        elif len(blanketPrice) == 1:
            ###NO ATTRIBTUES SELECTED
            if len(blanketAttributes) == 0:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s')" %(selected_zipcode, blanketPrice[0],blanketCategories[0]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 1:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketPrice[0],blanketCategories[0],blanketAttributes[0]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 2:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s'AND value='True')" %(selected_zipcode, blanketPrice[0], blanketCategories[0],blanketAttributes[0],blanketAttributes[1]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 3:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketPrice[0], blanketCategories[0],blanketAttributes[0],blanketAttributes[1],blanketAttributes[2]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 4:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s')" %(selected_zipcode,blanketPrice[0], blanketCategories[0],blanketAttributes[0],blanketAttributes[1],blanketAttributes[2],blanketAttributes[3]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 5:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketPrice[0],blanketCategories[0],blanketAttributes[0],blanketAttributes[1],blanketAttributes[2],blanketAttributes[3],blanketAttributes[4]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

    elif len(blanketCategories) == 2:
        if len(blanketPrice) == 0:
            if len(blanketAttributes) == 0:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s')" %(selected_zipcode,blanketCategories[0],blanketCategories[1]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 1:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode,blanketCategories[0],blanketCategories[1],blanketAttributes[0]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 2:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketCategories[0], blanketCategories[1],blanketAttributes[0],blanketAttributes[1]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 3:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketCategories[0],blanketCategories[1],blanketAttributes[0],blanketAttributes[1],blanketAttributes[2]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 4:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketCategories[0],blanketCategories[1],blanketAttributes[0],blanketAttributes[1],blanketAttributes[2],blanketAttributes[3]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 5:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketCategories[0],blanketCategories[1],blanketAttributes[0],blanketAttributes[1],blanketAttributes[2],blanketAttributes[3],blanketAttributes[4]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)



        elif len(blanketPrice) == 1:
            if len(blanketAttributes) == 0:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s')" %(selected_zipcode, blanketPrice[0], blanketCategories[0],blanketCategories[1]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
                #category algorithm
            elif len(blanketAttributes) == 1:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketPrice[0], blanketCategories[0],blanketCategories[1], blanketAttributes[0]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
                #category attribute algorithm
            elif len(blanketAttributes) == 2:
                #category attribute algorithm
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketPrice[0], blanketCategories[0],blanketCategories[1], blanketAttributes[0],blanketAttributes[1]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 3:
                #category attribute algorithm
                #price and category query
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketPrice[0], blanketCategories[0],blanketCategories[1], blanketAttributes[0],blanketAttributes[1],blanketAttributes[2]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 4:
                #category attribute algorithm
                #price and category query
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') " %(selected_zipcode, blanketPrice[0], blanketCategories[0],blanketCategories[1],blanketAttributes[0],blanketAttributes[1],blanketAttributes[2],blanketAttributes[3]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 5:
                #category attribute algorithm
                #price and category query
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketPrice[0], blanketCategories[0],blanketCategories[1], blanketAttributes[0],blanketAttributes[1],blanketAttributes[2],blanketAttributes[3],blanketAttributes[4]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)



        elif len(blanketPrice) == 2:
            if len(blanketAttributes) == 0:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s')" %(selected_zipcode, blanketPrice[0], blanketPrice[1],blanketCategories[0],blanketCategories[1]))
                #category algorithm
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 1:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketPrice[0], blanketPrice[1],blanketCategories[0],blanketCategories[1], blanketAttributes[0]))
                #category attribute algorithm
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 2:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') " %(selected_zipcode, blanketPrice[0], blanketPrice[1],blanketCategories[0],blanketCategories[1], blanketAttributes[0],blanketAttributes[1]))
                #category attribute algorithm
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 3:
                #category attribute algorithm
                #price and category query
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketPrice[0], blanketPrice[1],blanketCategories[0],blanketCategories[1], blanketAttributes[0],blanketAttributes[1],blanketAttributes[2]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 4:
                #category attribute algorithm
                #price and category query
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketPrice[0], blanketPrice[1],blanketCategories[0],blanketCategories[1], blanketAttributes[0],blanketAttributes[1],blanketAttributes[2],blanketAttributes[3]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 5:
                #category attribute algorithm
                #price and category query
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketPrice[0], blanketPrice[1],blanketCategories[0],blanketCategories[1], blanketAttributes[0],blanketAttributes[1],blanketAttributes[2],blanketAttributes[3],blanketAttributes[4]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
        


    elif len(blanketCategories) == 3:
        if len(blanketPrice) == 0:
            if len(blanketAttributes) == 0:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s')" %(selected_zipcode,blanketCategories[0],blanketCategories[1],blanketCategories[2]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 1:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode,blanketCategories[0],blanketCategories[1],blanketCategories[2],blanketAttributes[0]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 2:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketCategories[0], blanketCategories[1],blanketCategories[2],blanketAttributes[0],blanketAttributes[1]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 3:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketCategories[0],blanketCategories[1],blanketCategories[2],blanketAttributes[0],blanketAttributes[1],blanketAttributes[2]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 4:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketCategories[0],blanketCategories[1],blanketCategories[2],blanketAttributes[0],blanketAttributes[1],blanketAttributes[2],blanketAttributes[3]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 5:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketCategories[0],blanketCategories[1],blanketCategories[2],blanketAttributes[0],blanketAttributes[1],blanketAttributes[2],blanketAttributes[3],blanketAttributes[4]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)



        elif len(blanketPrice) == 1:
            if len(blanketAttributes) == 0:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s')" %(selected_zipcode, blanketPrice[0], blanketCategories[0],blanketCategories[1],blanketCategories[2]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
                #category algorithm
            elif len(blanketAttributes) == 1:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketPrice[0], blanketCategories[0],blanketCategories[1],blanketCategories[2], blanketAttributes[0]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
                #category attribute algorithm
            elif len(blanketAttributes) == 2:
                #category attribute algorithm
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketPrice[0], blanketCategories[0],blanketCategories[1],blanketCategories[2], blanketAttributes[0],blanketAttributes[1]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 3:
                #category attribute algorithm
                #price and category query
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketPrice[0], blanketCategories[0],blanketCategories[1],blanketCategories[2], blanketAttributes[0],blanketAttributes[1],blanketAttributes[2]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 4:
                #category attribute algorithm
                #price and category query
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') " %(selected_zipcode, blanketPrice[0], blanketCategories[0],blanketCategories[1],blanketCategories[2],blanketAttributes[0],blanketAttributes[1],blanketAttributes[2],blanketAttributes[3]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 5:
                #category attribute algorithm
                #price and category query
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketPrice[0], blanketCategories[0],blanketCategories[1], blanketCategories[2],blanketAttributes[0],blanketAttributes[1],blanketAttributes[2],blanketAttributes[3],blanketAttributes[4]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

        elif len(blanketPrice) == 2:
            if len(blanketAttributes) == 0:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s')" %(selected_zipcode, blanketPrice[0], blanketPrice[1],blanketCategories[0],blanketCategories[1],blanketCategories[2]))
                #category algorithm
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 1:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketPrice[0], blanketPrice[1],blanketCategories[0],blanketCategories[1],blanketCategories[2], blanketAttributes[0]))
                #category attribute algorithm
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 2:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') " %(selected_zipcode, blanketPrice[0], blanketPrice[1],blanketCategories[0],blanketCategories[1],blanketCategories[2], blanketAttributes[0],blanketAttributes[1]))
                #category attribute algorithm
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 3:
                #category attribute algorithm
                #price and category query
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketPrice[0], blanketPrice[1],blanketCategories[0],blanketCategories[1],blanketCategories[2], blanketAttributes[0],blanketAttributes[1],blanketAttributes[2]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 4:
                #category attribute algorithm
                #price and category query
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketPrice[0], blanketPrice[1],blanketCategories[0],blanketCategories[1], blanketCategories[2],blanketAttributes[0],blanketAttributes[1],blanketAttributes[2],blanketAttributes[3]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            elif len(blanketAttributes) == 5:
                #category attribute algorithm
                #price and category query
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketPrice[0], blanketPrice[1],blanketCategories[0],blanketCategories[1],blanketCategories[2], blanketAttributes[0],blanketAttributes[1],blanketAttributes[2],blanketAttributes[3],blanketAttributes[4]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
            

        elif len(blanketCategories) == 4:
            if len(blanketPrice) == 0:
                if len(blanketAttributes) == 0:
                    cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s')" %(selected_zipcode,blanketCategories[0],blanketCategories[1],blanketCategories[2],blanketCategories[3]))
                    nameList = cur.fetchall()
                    nameVars = StringVar(value=nameList)

                    bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                    bnameListBox.grid(column=2, row=2, sticky='nwes')
                    bnameListBox.bind("<<ListboxSelect>>", business_selected)
                elif len(blanketAttributes) == 1:
                    cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode,blanketCategories[0],blanketCategories[1],blanketCategories[2],blanketCategories[3],blanketAttributes[0]))
                    nameList = cur.fetchall()
                    nameVars = StringVar(value=nameList)

                    bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                    bnameListBox.grid(column=2, row=2, sticky='nwes')
                    bnameListBox.bind("<<ListboxSelect>>", business_selected)
                elif len(blanketAttributes) == 2:
                    cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketCategories[0], blanketCategories[1],blanketCategories[2],blanketCategories[3],blanketAttributes[0],blanketAttributes[1]))
                    nameList = cur.fetchall()
                    nameVars = StringVar(value=nameList)

                    bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                    bnameListBox.grid(column=2, row=2, sticky='nwes')
                    bnameListBox.bind("<<ListboxSelect>>", business_selected)
                elif len(blanketAttributes) == 3:
                    cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketCategories[0],blanketCategories[1],blanketCategories[2],blanketCategories[3],blanketAttributes[0],blanketAttributes[1],blanketAttributes[2]))
                    nameList = cur.fetchall()
                    nameVars = StringVar(value=nameList)

                    bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                    bnameListBox.grid(column=2, row=2, sticky='nwes')
                    bnameListBox.bind("<<ListboxSelect>>", business_selected)
                elif len(blanketAttributes) == 4:
                    cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketCategories[0],blanketCategories[1],blanketCategories[2],blanketCategories[3],blanketAttributes[0],blanketAttributes[1],blanketAttributes[2],blanketAttributes[3]))
                    nameList = cur.fetchall()
                    nameVars = StringVar(value=nameList)

                    bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                    bnameListBox.grid(column=2, row=2, sticky='nwes')
                    bnameListBox.bind("<<ListboxSelect>>", business_selected)
                elif len(blanketAttributes) == 5:
                    cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketCategories[0],blanketCategories[1],blanketCategories[2],blanketCategories[3],blanketAttributes[0],blanketAttributes[1],blanketAttributes[2],blanketAttributes[3],blanketAttributes[4]))
                    nameList = cur.fetchall()
                    nameVars = StringVar(value=nameList)

                    bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                    bnameListBox.grid(column=2, row=2, sticky='nwes')
                    bnameListBox.bind("<<ListboxSelect>>", business_selected)



            elif len(blanketPrice) == 1:
                if len(blanketAttributes) == 0:
                    cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s')" %(selected_zipcode, blanketPrice[0], blanketCategories[0],blanketCategories[1],blanketCategories[2],blanketCategories[3],))
                    nameList = cur.fetchall()
                    nameVars = StringVar(value=nameList)

                    bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                    bnameListBox.grid(column=2, row=2, sticky='nwes')
                    bnameListBox.bind("<<ListboxSelect>>", business_selected)
                    #category algorithm
                elif len(blanketAttributes) == 1:
                    cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketPrice[0], blanketCategories[0],blanketCategories[1],blanketCategories[2],blanketCategories[3], blanketAttributes[0]))
                    nameList = cur.fetchall()
                    nameVars = StringVar(value=nameList)

                    bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                    bnameListBox.grid(column=2, row=2, sticky='nwes')
                    bnameListBox.bind("<<ListboxSelect>>", business_selected)
                    #category attribute algorithm
                elif len(blanketAttributes) == 2:
                    #category attribute algorithm
                    cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketPrice[0], blanketCategories[0],blanketCategories[1],blanketCategories[2],blanketCategories[3], blanketAttributes[0],blanketAttributes[1]))
                    nameList = cur.fetchall()
                    nameVars = StringVar(value=nameList)

                    bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                    bnameListBox.grid(column=2, row=2, sticky='nwes')
                    bnameListBox.bind("<<ListboxSelect>>", business_selected)
                elif len(blanketAttributes) == 3:
                    #category attribute algorithm
                    #price and category query
                    cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketPrice[0], blanketCategories[0],blanketCategories[1],blanketCategories[2], blanketCategories[3],blanketAttributes[0],blanketAttributes[1],blanketAttributes[2]))
                    nameList = cur.fetchall()
                    nameVars = StringVar(value=nameList)

                    bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                    bnameListBox.grid(column=2, row=2, sticky='nwes')
                    bnameListBox.bind("<<ListboxSelect>>", business_selected)
                elif len(blanketAttributes) == 4:
                    #category attribute algorithm
                    #price and category query
                    cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') " %(selected_zipcode, blanketPrice[0], blanketCategories[0],blanketCategories[1],blanketCategories[2],blanketCategories[3],blanketAttributes[0],blanketAttributes[1],blanketAttributes[2],blanketAttributes[3]))
                    nameList = cur.fetchall()
                    nameVars = StringVar(value=nameList)

                    bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                    bnameListBox.grid(column=2, row=2, sticky='nwes')
                    bnameListBox.bind("<<ListboxSelect>>", business_selected)
                elif len(blanketAttributes) == 5:
                    #category attribute algorithm
                    #price and category query
                    cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketPrice[0], blanketCategories[0],blanketCategories[1], blanketCategories[2],blanketCategories[3],blanketAttributes[0],blanketAttributes[1],blanketAttributes[2],blanketAttributes[3],blanketAttributes[4]))
                    nameList = cur.fetchall()
                    nameVars = StringVar(value=nameList)

                    bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                    bnameListBox.grid(column=2, row=2, sticky='nwes')
                    bnameListBox.bind("<<ListboxSelect>>", business_selected)

            elif len(blanketPrice) == 2:
                if len(blanketAttributes) == 0:
                    cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s')" %(selected_zipcode, blanketPrice[0], blanketPrice[1],blanketCategories[0],blanketCategories[1],blanketCategories[2],blanketCategories[3]))
                    #category algorithm
                    nameList = cur.fetchall()
                    nameVars = StringVar(value=nameList)

                    bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                    bnameListBox.grid(column=2, row=2, sticky='nwes')
                    bnameListBox.bind("<<ListboxSelect>>", business_selected)
                elif len(blanketAttributes) == 1:
                    cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketPrice[0], blanketPrice[1],blanketCategories[0],blanketCategories[1],blanketCategories[2],blanketCategories[3], blanketAttributes[0]))
                    #category attribute algorithm
                    nameList = cur.fetchall()
                    nameVars = StringVar(value=nameList)

                    bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                    bnameListBox.grid(column=2, row=2, sticky='nwes')
                    bnameListBox.bind("<<ListboxSelect>>", business_selected)
                elif len(blanketAttributes) == 2:
                    cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') " %(selected_zipcode, blanketPrice[0], blanketPrice[1],blanketCategories[0],blanketCategories[1],blanketCategories[2],blanketCategories[3], blanketAttributes[0],blanketAttributes[1]))
                    #category attribute algorithm
                    nameList = cur.fetchall()
                    nameVars = StringVar(value=nameList)

                    bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                    bnameListBox.grid(column=2, row=2, sticky='nwes')
                    bnameListBox.bind("<<ListboxSelect>>", business_selected)
                elif len(blanketAttributes) == 3:
                    #category attribute algorithm
                    #price and category query
                    cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketPrice[0], blanketPrice[1],blanketCategories[0],blanketCategories[1],blanketCategories[2],blanketCategories[3], blanketAttributes[0],blanketAttributes[1],blanketAttributes[2]))
                    nameList = cur.fetchall()
                    nameVars = StringVar(value=nameList)

                    bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                    bnameListBox.grid(column=2, row=2, sticky='nwes')
                    bnameListBox.bind("<<ListboxSelect>>", business_selected)
                elif len(blanketAttributes) == 4:
                    #category attribute algorithm
                    #price and category query
                    cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketPrice[0], blanketPrice[1],blanketCategories[0],blanketCategories[1], blanketCategories[2],blanketCategories[3],blanketAttributes[0],blanketAttributes[1],blanketAttributes[2],blanketAttributes[3]))
                    nameList = cur.fetchall()
                    nameVars = StringVar(value=nameList)

                    bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                    bnameListBox.grid(column=2, row=2, sticky='nwes')
                    bnameListBox.bind("<<ListboxSelect>>", business_selected)
                elif len(blanketAttributes) == 5:
                    #category attribute algorithm
                    #price and category query
                    cur.execute("SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" %(selected_zipcode, blanketPrice[0], blanketPrice[1],blanketCategories[0],blanketCategories[1],blanketCategories[2],blanketCategories[3], blanketAttributes[0],blanketAttributes[1],blanketAttributes[2],blanketAttributes[3],blanketAttributes[4]))
                    nameList = cur.fetchall()
                    nameVars = StringVar(value=nameList)

                    bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                    bnameListBox.grid(column=2, row=2, sticky='nwes')
                    bnameListBox.bind("<<ListboxSelect>>", business_selected)















def price_range_filter(event):
    global filterPriceList, priceRangeListBox, bnameListBox, blanketPrice
    filterPriceList = []
    blanketPrice = []
    #priceList = []
    for i in priceRangeListBox.curselection():
        selected_price = priceRangeListBox.get(i)
        #selected_price = selected_price[0]
        if selected_price == "$":
            filterPriceList.append("1")
            blanketPrice.append("1")
        elif selected_price == "$$":
            filterPriceList.append("2")
            blanketPrice.append("2")
        elif selected_price == "$$$":
            filterPriceList.append("3")
            blanketPrice.append("3")
        elif selected_price == "$$$$":
            filterPriceList.append("4")
            blanketPrice.append("4")
        #filterPriceList.append(selected_price)
    blanket_search()


def update_business():
    global tipEntry
    global selected_business_id
    global tipList
    selected_business_id = selected_business_id[0]
    tipToString = tipEntry.get()
    tipToStringVar = StringVar(value=tipToString)
    cur.execute("INSERT INTO tip (user_id,business_id,tipdate,tiptext,likes) SELECT '%s','%s','%s','%s','%s'" %('4XChL029mKr5hydo79Ljxg',selected_business_id,'03/31/22',tipToString,'1'))
    tipVars = StringVar(value=tipList)
    tipMessage = Listbox(root, listvariable=tipVars, width= 100)

def business_selected(event):
    global bidList
    global selected_business_id
    global tipList
    tips = ''
    for i in bnameListBox.curselection():
        selected_business = bnameListBox.get(i)
        selected_business = selected_business[0]
        #cur.execute("SELECT business_id FROM business WHERE bname='%s'" %selected_business) #current one
        cur.execute("SELECT tiptext FROM (SELECT business_id FROM business WHERE bname = '%s') AS bnames, tip WHERE tip.business_id = bnames.business_id" %selected_business) #testing this one out
        bizIDlist = cur.fetchall()

        if not bizIDlist:
            print("Nothing should happen.")
        else:
            bizTuple = bizIDlist[0]
            bizID = bizTuple[0]

        tipList = bizIDlist
        tipVars = StringVar(value=tipList)

        tipMessage = Listbox(root, listvariable=tipVars, width= 100)
        tipMessage.grid(column=0, row=5, sticky='nwes')
        tipMessage.bind("<<ListboxSelect>>")


def attribute_selected(event):
    global selected_zipcode
    global bidList, blanketAttributes, blanketMeals
    global bnameListBox
    bidList = []
    nameList = []
    attributeList = []
    blanketAttributes = []
    index = 0
    if type(selected_zipcode) is tuple:
        selected_zipcode = selected_zipcode[0]
    for i in attributeListBox.curselection():
        selected_attribute = attributeListBox.get(i)
        if selected_attribute == "Accepts Credit Cards" and "BusinessAcceptsCreditCards" not in blanketAttributes:
            selected_attribute = "BusinessAcceptsCreditCards"
            blanketAttributes.append("BusinessAcceptsCreditCards")
        elif selected_attribute == "Takes Reservations" and "RestaurantsReservations" not in blanketAttributes:
            selected_attribute = "RestaurantsReservations"
            blanketAttributes.append("RestaurantsReservations")
        elif selected_attribute == "Wheelchair Accessible" and "WheelchairAccessible" not in blanketAttributes:
            selected_attribute = "WheelchairAccessible"
            blanketAttributes.append("WheelchairAccessible")
        elif selected_attribute == "Outdoor Seating" and "OutdoorSeating" not in blanketAttributes:
            selected_attribute = "OutdoorSeating"
            blanketAttributes.append("OutdoorSeating")
        elif selected_attribute == "Good for Kids" and "GoodForKids" not in blanketAttributes:
            selected_attribute = "GoodForKids"
            blanketAttributes.append("GoodForKids")
        elif selected_attribute == "Good for Groups" and "RestaurantsGoodForGroups" not in blanketAttributes:
            selected_attribute = "RestaurantsGoodForGroups"
            blanketAttributes.append("RestaurantsGoodForGroups")
        elif selected_attribute == "Delivery" and "RestaurantsDelivery" not in blanketAttributes:
            selected_attribute = "RestaurantsDelivery"
            blanketAttributes.append("RestaurantsDelivery")
        elif selected_attribute == "Take Out" and "RestaurantsTakeOut" not in blanketAttributes:
            selected_attribute = "RestaurantsTakeOut"
            blanketAttributes.append("RestaurantsTakeOut")
        elif selected_attribute == "Free Wi-Fi" and "WiFi" not in blanketAttributes:
            selected_attribute = "WiFi"
            blanketAttributes.append("WiFi")
        elif selected_attribute == "Bike Parking" and "BikeParking" not in blanketAttributes:
            selected_attribute = "BikeParking"
            blanketAttributes.append("BikeParking")
    for j in mealsListBox.curselection():
        selected_attribute = mealsListBox.get(j)
        if selected_attribute == "Breakfast" and "breakfast" not in blanketAttributes:
            selected_attribute = "breakfast"
            blanketAttributes.append("breakfast")
        elif selected_attribute == "Lunch" and "lunch" not in blanketAttributes:
            selected_attribute = "lunch"
            blanketAttributes.append("lunch")
        elif selected_attribute == "Brunch" and "brunch" not in blanketAttributes:
            selected_attribute = "brunch"
            blanketAttributes.append("brunch")
        elif selected_attribute == "Dinner" and "dinner" not in blanketAttributes:
            selected_attribute = "dinner"
            blanketAttributes.append("dinner")
        elif selected_attribute == "Dessert" and "dessert" not in blanketAttributes:
            selected_attribute = "dessert"
            blanketAttributes.append("dessert")
        elif selected_attribute == "Late Night" and "latenight" not in blanketAttributes:
            selected_attribute = "latenight"
            blanketAttributes.append("latenight")
    for k in priceRangeListBox.curselection():
        selected_attribute = priceRangeListBox.get(k)
        #selected_price = selected_price[0]
        if selected_attribute == "$" and "$" not in blanketPrice:
            filterPriceList.append("1")
            blanketPrice.append("1")
        elif selected_attribute == "$$" and "$$" not in blanketPrice:
            filterPriceList.append("2")
            blanketPrice.append("2")
        elif selected_attribute == "$$$" and "$$$" not in blanketPrice:
            filterPriceList.append("3")
            blanketPrice.append("3")
        elif selected_attribute == "$$$$" and "$$$$" not in blanketPrice:
            filterPriceList.append("4")
            blanketPrice.append("4")

    blanket_search()

def category_selected(event):
    global selected_zipcode
    global bidList, blanketCategories
    global bnameListBox
    bidList = []
    nameList = []
    categoryList = []
    blanketCategories = []
    index = 0
    
    if type(selected_zipcode) is tuple:
        selected_zipcode = selected_zipcode[0]
    for i in categoryListBox.curselection():
        selected_category = categoryListBox.get(i)
        selected_category = selected_category[0]
        #categories = selected_category.split(",")
        print(selected_category)
        categoryList.append(selected_category)
        if selected_category not in blanketCategories:
            blanketCategories.append(selected_category)
    blanket_search()

    #That's enough tags for the user.

def search_clicked():
    global selected_zipcode
    global bnameList
    global bidList
    global bnameListBox
    cur.execute("SELECT bname FROM business WHERE zipcode='%s' ORDER BY bname", selected_zipcode)
    bnameList = cur.fetchall()
    bnameVars = StringVar(value=bnameList)
    #print(bnameList)
    cur.execute("SELECT business_id FROM business WHERE zipcode ='%s'" %selected_zipcode)
    bidList = cur.fetchall()
    bidVars = StringVar(value=bidList)
    bnameListBox = Listbox(root, listvariable=bnameVars, height=20)
    bnameListBox.grid(column=2, row=2, sticky='nwes')
    bnameListBox.bind("<<ListboxSelect>>", business_selected)

    global priceRangeListBox
    priceRangeList = ["$","$$","$$$","$$$$"]
    priceRangeVars = StringVar(value=priceRangeList)
    priceRangeListBox = Listbox(root, listvariable=priceRangeVars, selectmode="multiple")
    priceRangeListBox.grid(column=6, row=0, sticky='nwes')
    priceRangeListBox.bind("<<ListboxSelect>>", attribute_selected)
    #priceRangeListBox.bind("<<ListboxSelect>>", price_range_filter)

    attributeList = ["Accepts Credit Cards", "Takes Reservations","Wheelchair Accessible","Outdoor Seating","Good for Kids","Good for Groups","Delivery","Take Out","Free Wi-Fi","Bike Parking",]#cur.fetchall()
    attributeVars = StringVar(value=attributeList)

    global attributeListBox
    attributeListBox = Listbox(root, listvariable=attributeVars, selectmode="multiple")
    attributeListBox.grid(column=6,row=1,sticky='nwes')
    attributeListBox.bind('<<ListboxSelect>>', attribute_selected)

    mealsList = ["Breakfast","Lunch","Brunch","Dinner","Dessert","Late Night"]
    mealsVars = StringVar(value=mealsList)
    global mealsListBox
    mealsListBox = Listbox(root, listvariable=mealsVars, selectmode="multiple")
    mealsListBox.grid(column=7,row=1,sticky='nwes')
    mealsListBox.bind('<<ListboxSelect>>', attribute_selected)

def zipcode_selected(event):
    global bnameListBox
    global bidList
    for i in zipCodeListBox.curselection():
        global selected_zipcode
        selected_zipcode = zipCodeListBox.get(i)
        #print(selected_zipcode)
        cur.execute("SELECT DISTINCT category_name FROM business, categories WHERE business.zipcode= '%s' AND business.business_id=categories.business_id ORDER BY category_name" %selected_zipcode)
        categoryList = cur.fetchall()
        categoryVars = StringVar(value=categoryList)

        #cur.execute("SELECT DISTINCT attr_name FROM business, attributes WHERE business.zipcode= '%s' AND business.business_id=attributes.business_id ORDER BY attr_name" %selected_zipcode)
            
        global categoryListBox
        categoryListBox = Listbox(root, listvariable=categoryVars, selectmode="multiple")
        categoryListBox.grid(column=1,row=3,sticky='nwes')
        categoryListBox.bind('<<ListboxSelect>>', category_selected)
        

def city_selected(event):
    for i in cityListBox.curselection():
        selected_city = str(cityListBox.get(i))
        selected_city = selected_city[2:-3]

        if stateIsSelected == True:
            cur.execute("SELECT DISTINCT zipcode FROM (SELECT state FROM business WHERE state= '%s' ORDER BY city) business WHERE city= '%s' ORDER BY zipcode" %selected_state %selected_city)
        else:
            cur.execute("SELECT DISTINCT zipcode FROM business WHERE city= '%s' ORDER BY zipcode" %selected_city)
        global zipCodeListBox
        zipCodeList = cur.fetchall()
        stateListBox.grid(column=1, row=0, sticky='nwes')
        stateListBox.bind('<<ListboxSelect>>', state_selected)
        zipCodeVars = StringVar(value=zipCodeList)
        zipCodeListBox = Listbox(root,listvariable=zipCodeVars)
        zipCodeListBox.grid(column=1, row=2, sticky='nwes')
        zipCodeListBox.bind('<<ListboxSelect>>', zipcode_selected)


def state_selected(event):
    stateIsSelected = True
    for i in stateListBox.curselection():
        selected_state = str(stateListBox.get(i))
        print(selected_state)
        selected_state = selected_state[2:-3]
        print(selected_state)
        cur.execute("SELECT DISTINCT city FROM business WHERE state= '%s' ORDER BY city" %selected_state)
        cityList = cur.fetchall()
        cityVars = StringVar(value=cityList)
        global cityListBox
        cityListBox = Listbox(root,listvariable=cityVars)
        cityListBox.grid(column=1, row=1, sticky='nwes')
        cityListBox.bind('<<ListboxSelect>>', city_selected)


if __name__ == "__main__":
    #parseBusinessData()
    #insert2BusinessTable()
    #parseUserData()
    #insert2UserTable()
    #parseCheckinData()
    #insert2CheckinTable()
    #parseTipData()
    #insert2TipTable()
    #insert2CategoriesTable()
    #insert2AttributesTable()
    #insert2HoursTable()

    cityListBox = stateListBox
    zipCodeListBox = cityListBox
    stateListBox.grid(column=1, row=0, sticky='nwes')
    stateListBox.bind('<<ListboxSelect>>', state_selected)
    searchButton = Button(root, text="Search in zipcode", command=search_clicked)
    searchButton.grid(row=5, column=0)
    #enterTipButton = Button(root, text="Submit tip", command=update_business)
    #enterTipButton.grid(row=8, column=2)
    stateLabel = Label(root, text="State", font=("Arial",10)).grid(row=0, column=0)
    cityLabel = Label(root, text="City", font=("Arial",10)).grid(row=1, column=0)
    zipLabel = Label(root, text="Zipcode", font=("Arial",10)).grid(row=2, column=0)
    categoryLabel = Label(root, text="Categories", font=("Arial",10)).grid(row=3, column=0)
    attributeLabel = Label(root, text="Attributes", font=("Arial",10)).grid(row=4, column=0)

    root.mainloop()
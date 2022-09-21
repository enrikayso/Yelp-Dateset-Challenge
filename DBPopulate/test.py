import json
import psycopg2
import re


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
    with open('yelp_CptS451_2022/yelp_business.JSON', 'r') as f:
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
    with open('yelp_CptS451_2022/yelp_business.JSON', 'r') as f:    #TO-DO: update path for the input file
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



# USER DATA


def parseUserData():
    # TO-DO : write code to parse yelp_user.JSON
    #read the JSON file
    # We assume that the Yelp data files are available in the current directory. If not, you should specify the path when you "open" the function.
    with open('yelp_CptS451_2022/yelp_user.JSON', 'r') as f:
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
    with open('yelp_CptS451_2022/yelp_user.JSON', 'r') as f:    # TO-DO: update path for the input file
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




# Checkin Data


def parseCheckinData():
    pass
    # TO-DO : write code to parse yelp_checkin.JSON
    #read the JSON file
    # We assume that the Yelp data files are available in the current directory. If not, you should specify the path when you "open" the function.


    with open('yelp_CptS451_2022/yelp_checkin.JSON','r') as f:
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
    with open('yelp_CptS451_2022/yelp_checkin.JSON', 'r') as f:    # TO-DO: update path for the input file
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





# Tip Data

def parseTipData():
    # TO-DO : write code to parse yelp_tip.JSON
    with open('yelp_CptS451_2022/yelp_tip.JSON', 'r') as f:
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
    with open('yelp_CptS451_2022/yelp_tip.JSON', 'r') as f:
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
    with open('yelp_CptS451_2022/yelp_business.JSON','r') as f:    # TO-DO: update path for the input file
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
    with open('yelp_CptS451_2022/yelp_business.JSON', 'r') as f:    # TO-DO: update path for the input file
        # #outfile =  open('./yelp_business_out.SQL', 'w')  #uncomment this line if you are writing the INSERT statements to an output file.
        line = f.readline()
        count_line = 0

        data = json.loads(line)
        # first = str(data["attributes"])

        # print(raw_dict)
        # first = first.split('{')
        # print(first)
        # first = str(first).split('}')
        # print(first)
        # print(type(first))
        # first = first.replace('{', '')
        # print(first)


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

                # for item1 in raw_dict:
                #     if isinstance(raw_dict.get(item1), dict):
                #         attribute_list.append(item1)
                #         for item2 in raw_dict.get(item1):
                #             attribute_list.append(item2)
                #     attribute_list.append(item1)

                def parseNestedDict(dic, add):
                    for item in dic:
                        if isinstance(dic.get(item), dict):
                            attribute_list.append(item)
                            # att_value_list.append()
                            parseNestedDict(dic.get(item), False)
                        attribute_list.append(item)
                        att_value_list.append(dic.get(item))
                        # if add is True:
                        #     att_value_list.append(raw_dict.get(item))
                        # else:
                        #     add = True

                parseNestedDict(raw_dict, add)

                seen = set()
                dupes = [x for x in attribute_list if x in seen or seen.add(x)]
                seen = set()
                attribute_list = [x for x in attribute_list if x not in seen and not seen.add(x)]
                attribute_list = [x for x in attribute_list if x not in dupes]
                for item in att_value_list:
                    if isinstance(item, dict):
                        att_value_list.remove(item)

                # print(attribute_list)
                # print(att_value_list)
                # print(dupes)
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
    with open('yelp_CptS451_2022/yelp_business.JSON', 'r') as f:    # TO-DO: update path for the input file
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

                    # add = True

                    # for item1 in raw_dict:
                    #     if isinstance(raw_dict.get(item1), dict):
                    #         attribute_list.append(item1)
                    #         for item2 in raw_dict.get(item1):
                    #             attribute_list.append(item2)
                    #     attribute_list.append(item1)

                    def parseNestedDict(dic):
                        for item in dic:
                            if isinstance(dic.get(item), dict):
                                dayofweek.append(item)
                                # att_value_list.append()
                                parseNestedDict(dic.get(item))
                            dayofweek.append(item)
                            hours.append(dic.get(item))
                            # if add is True:
                            #     att_value_list.append(raw_dict.get(item))
                            # else:
                            #     add = True

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

                    # print(dayofweek)
                    # print(hours)
                    # print(hours_clean)
                    # print(type(hours_clean))
                    # print(open_hours)
                    # print(closed_hours)

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

if __name__ == "__main__":
    # parseBusinessData()
    # insert2BusinessTable()
    parseUserData()
    insert2UserTable()
    # parseCheckinData()
    # insert2CheckinTable()
    # parseTipData()
    # insert2TipTable()
    # insert2CategoriesTable()
    # insert2AttributesTable()
    # insert2HoursTable()
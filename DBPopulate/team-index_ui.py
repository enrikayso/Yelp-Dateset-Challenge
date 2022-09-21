import json
from tkinter import *
from tkinter.ttk import *
import psycopg2
from datetime import date
import calendar

root = Tk()
root.title("Yelp Database")
root.geometry("1500x900")
conn = psycopg2.connect("dbname='milestone2' user='postgres' host='localhost' password='solarion'")
# conn = psycopg2.connect("dbname='milestone1db' user='postgres' host='localhost' password=''")
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
cityListBox = Listbox(root, listvariable=cityVars)
# cityListBox.delete(0,END)
# cur.close()


cur = conn.cursor()
cur.execute("SELECT DISTINCT zipcode FROM business ORDER BY zipcode")
zipCodeList = cur.fetchall()
# zipCodeVars = StringVar(value=zipCodeList)
# zipCodeListBox = Listbox(root)#,listvariable=zipCodeVars)

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
# searchButton = Button(root)
tipEntry = Entry(root, width=40)
tipEntry.grid(row=6, column=1)
tipEntry_label = Label(root, text="Add new tip!")
tipEntry_label.grid(row=6, column=0)

tipToAdd = ''
selected_business_id = ''
tipList = []
bid_query = ''
# business_


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


def bid_event(event):
    temp = bnameListBox.curselection()
    sb = bnameListBox.get(temp)
    sb = sb[0]
    #
    # print('temp = ', temp)
    # print('sb = ', sb)

    get_bid(sb)


def get_bid(sb):

    global bid_query, selected_business_id

    bid_query = bid_query.replace('|', '\'' + sb + '\'')
    # print('hello')
    # selected_business_id = str(sb_id)
    # selected_business_id = selected_business_id[3:-4]
    # print('asdfasdf = ', bid_query)

    cur.execute(bid_query)
    sb_id = cur.fetchall()
    selected_business_id = str(sb_id)
    selected_business_id = selected_business_id[3:-4]
    bnameListBox.bind("<<ListboxSelect>>", business_selected)


def business_selected_checkins():
    cur.execute("Select extract(month from checkindate) as month, count(business_id) as checkinCount from checkins group by extract(month from checkindate)")
    checkinData = cur.fetchall()
    checkinDataTest = checkinData[0][1]
    checkinVars = StringVar(value=checkinData)
    checkinListBox = Listbox(root, listvariable=checkinVars)
    checkinListBox.grid(row=5, column=2)


def blanket_search():
    global blanketAttributes, blanketCategories, blanketMeals, blanketPrice, selected_zipcode, bnameListBox
    global selected_business_id, bid_query

    if type(selected_zipcode) is tuple:
        selected_zipcode = selected_zipcode[0]
    print("blanketATTRIBUTES: ", blanketAttributes)
    print("blanketCATEGORIES: ", blanketCategories)
    print("blanketPRICES: ", blanketPrice)

    ###NO CATEGORIES SELECTED
    if len(blanketCategories) == 0:
        ###NO PRICES SELECTED
        if len(blanketPrice) == 0:
            if len(blanketAttributes) == 0:
                cur.execute("SELECT bname FROM business WHERE zipcode = '%s')" % (selected_zipcode))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # # sb = sb[0]
                # cur.execute("SELECT bname FROM business WHERE bname = '%s' zipcode = '%s')" % (sb, selected_zipcode))
                # sb_id = cur.fetchall()
                # selected_business_id = str(sb_id)
                # selected_business_id = selected_business_id[3:-4]

                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode})"

            ###ONE ATTRIBUTE SELECTED
            if len(blanketAttributes) == 1:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketAttributes[0]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # # sb = sb[0]
                # cur.execute(
                #     "SELECT business_id FROM business WHERE bname = '%s' AND zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                #         sb, selected_zipcode, blanketAttributes[0]))
                # sb_id = cur.fetchall()
                # selected_business_id = str(sb_id)
                # selected_business_id = selected_business_id[3:-4]

                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '{blanketAttributes[0]}' AND value='True')"

            elif len(blanketAttributes) == 2:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketAttributes[0], blanketAttributes[1]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # # sb = sb[0]
                # cur.execute(
                #     "SELECT business_id FROM business WHERE bname = '%s' AND zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                #         sb, selected_zipcode, blanketAttributes[0], blanketAttributes[1]))
                # sb_id = cur.fetchall()
                # selected_business_id = str(sb_id)
                # selected_business_id = selected_business_id[3:-4]

                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '{blanketAttributes[1]}' AND value='True')"

            elif len(blanketAttributes) == 3:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketAttributes[0], blanketAttributes[1], blanketAttributes[2]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # # sb = sb[0]
                # cur.execute(
                #     "SELECT business_id FROM business WHERE bname = '%s' AND zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                #         sb, selected_zipcode, blanketAttributes[0], blanketAttributes[1], blanketAttributes[2]))
                # sb_id = cur.fetchall()
                # selected_business_id = str(sb_id)
                # selected_business_id = selected_business_id[3:-4]

                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '{blanketAttributes[1]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '{blanketAttributes[2]}' AND value='True')"

            elif len(blanketAttributes) == 4:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketAttributes[0], blanketAttributes[1], blanketAttributes[2],
                    blanketAttributes[3]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # # sb = sb[0]
                # cur.execute(
                #     "SELECT business_id FROM business WHERE bname = '%s' AND zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                #         sb, selected_zipcode, blanketAttributes[0], blanketAttributes[1], blanketAttributes[2],
                #         blanketAttributes[3]))
                # sb_id = cur.fetchall()
                # selected_business_id = str(sb_id)
                # selected_business_id = selected_business_id[3:-4]

                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '{blanketAttributes[1]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '{blanketAttributes[2]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '{blanketAttributes[3]}' AND value='True')"

            elif len(blanketAttributes) == 5:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketAttributes[0], blanketAttributes[1], blanketAttributes[2],
                    blanketAttributes[3], blanketAttributes[4]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # # sb = sb[0]
                # cur.execute(
                #     "SELECT business_id FROM business WHERE bname = '%s' AND zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                #         sb, selected_zipcode, blanketAttributes[0], blanketAttributes[1], blanketAttributes[2],
                #         blanketAttributes[3], blanketAttributes[4]))
                # sb_id = cur.fetchall()
                # selected_business_id = str(sb_id)
                # selected_business_id = selected_business_id[3:-4]

                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '{blanketAttributes[1]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '{blanketAttributes[2]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '{blanketAttributes[3]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '{blanketAttributes[4]}' AND value='True')"

        ###ONE PRICE SELECTED
        elif len(blanketPrice) == 1:
            ###NO ATTRIBTUES SELECTED
            if len(blanketAttributes) == 0:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s')" % (
                    selected_zipcode, blanketPrice[0]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # # sb = sb[0]
                # cur.execute(
                #     "SELECT business_id FROM business WHERE bname = '%s' AND zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s')" % (
                #         sb, selected_zipcode, blanketPrice[0]))
                # sb_id = cur.fetchall()
                # selected_business_id = str(sb_id)
                # selected_business_id = selected_business_id[3:-4]

                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}')"

            elif len(blanketAttributes) == 1:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketPrice[0], blanketAttributes[0]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # # sb = sb[0]
                # cur.execute(
                #     "SELECT business_id FROM business WHERE bname = '%s' AND zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                #         sb, selected_zipcode, blanketPrice[0], blanketAttributes[0]))
                # sb_id = cur.fetchall()
                # selected_business_id = str(sb_id)
                # selected_business_id = selected_business_id[3:-4]

                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '{blanketAttributes[0]}' AND value='True')"

            elif len(blanketAttributes) == 2:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketPrice[0], blanketAttributes[0], blanketAttributes[1]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = {blanketAttributes[1]} AND value='True')"
                # sb_id = cur.fetchall()
                # selected_business_id = str(sb_id)
                # selected_business_id = selected_business_id[3:-4]
                
            elif len(blanketAttributes) == 3:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketPrice[0], blanketAttributes[0], blanketAttributes[1],
                    blanketAttributes[2]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[2]}' AND value='True')"
                
                # sb_id = cur.fetchall()
                # selected_business_id = str(sb_id)
                # selected_business_id = selected_business_id[3:-4]
                
            elif len(blanketAttributes) == 4:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketPrice[0], blanketAttributes[0], blanketAttributes[1], blanketAttributes[2],
                    blanketAttributes[3]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[2]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[3]}' AND value='True')"
                
                # sb_id = cur.fetchall()
                # selected_business_id = str(sb_id)
                # selected_business_id = selected_business_id[3:-4]
            elif len(blanketAttributes) == 5:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketPrice[0], blanketAttributes[0], blanketAttributes[1], blanketAttributes[2],
                    blanketAttributes[3], blanketAttributes[4]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
                # 
                # sb = bnameListBox.get(0)
                # # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[3]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[2]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[3]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[4]}' AND value='True')"
                
                # sb_id = cur.fetchall()
                # selected_business_id = str(sb_id)
                # selected_business_id = selected_business_id[3:-4]


    elif len(blanketCategories) == 1:
        if len(blanketPrice) == 0:
            ###ONE ATTRIBUTE SELECTED
            if len(blanketAttributes) == 0:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s')" % (
                    selected_zipcode, blanketCategories[0]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", bid_event)

                # sb = ''
                # for i in bnameListBox.curselection():
                #     sb = bnameListBox.get(i)
                #     # sb = sb[0]

                # cur.execute(
                #     "SELECT bname FROM business WHERE bname = '%s' AND zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s')" % (
                #         sb, selected_zipcode, blanketCategories[0]))

                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}')"
                # print('SQL query = ', bid_query)
                # print(type(bid_query))

                # get_bid(bid_query)
                # bnameListBox.bind("<<ListboxSelect>>", get_bid(bid_query))

                # sb = bnameListBox.get(0)
                # # sb = sb[0]
                # print('pre-func-call', sb)
                # cur.execute(
                #     "SELECT business_id FROM business WHERE bname = '%s' AND zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s')" % (
                #         sb, selected_zipcode, blanketCategories[0]))
                # sb_id = cur.fetchall()
                # selected_business_id = StringVar(value=selected_business_id)
                # selected_business_id = str(list(sb_id[0]))
                # selected_business_id = str(sb_id)
                # selected_business_id = selected_business_id[3:-4]
                # print(type(selected_business_id))
                # print('sbid = ', selected_business_id)
                # print('bnamelist = ', bnameListBox.curselection())
            elif len(blanketAttributes) == 1:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketCategories[0], blanketAttributes[0]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True')"

                # sb_id = cur.fetchall()
                # selected_business_id = str(sb_id)
                # selected_business_id = selected_business_id[3:-4]
            elif len(blanketAttributes) == 2:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketCategories[0], blanketAttributes[0], blanketAttributes[1]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True')"
                
                # sb_id = cur.fetchall()
                # selected_business_id = str(sb_id)
                # selected_business_id = selected_business_id[3:-4]
            elif len(blanketAttributes) == 3:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketCategories[0], blanketAttributes[0], blanketAttributes[1],
                    blanketAttributes[2]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[2]}' AND value='True')"
                
                # sb_id = cur.fetchall()
                # selected_business_id = str(sb_id)
                # selected_business_id = selected_business_id[3:-4]
            elif len(blanketAttributes) == 4:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketCategories[0], blanketAttributes[0], blanketAttributes[1],
                    blanketAttributes[2], blanketAttributes[3]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[2]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[3]}' AND value='True')"
                
                # sb_id = cur.fetchall()
                # selected_business_id = str(sb_id)
                # selected_business_id = selected_business_id[3:-4]
            elif len(blanketAttributes) == 5:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketCategories[0], blanketAttributes[0], blanketAttributes[1],
                    blanketAttributes[2], blanketAttributes[3], blanketAttributes[4]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[2]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[3]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[4]}' AND value='True')"
                
                # sb_id = cur.fetchall()
                # selected_business_id = str(sb_id)
                # selected_business_id = selected_business_id[3:-4]


        ###ONE PRICE SELECTED
        elif len(blanketPrice) == 1:
            ###NO ATTRIBTUES SELECTED
            if len(blanketAttributes) == 0:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s')" % (
                    selected_zipcode, blanketPrice[0], blanketCategories[0]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}')"
                
                # sb_id = cur.fetchall()
                # selected_business_id = str(sb_id)
                # selected_business_id = selected_business_id[3:-4]
            elif len(blanketAttributes) == 1:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketPrice[0], blanketCategories[0], blanketAttributes[0]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True')"
                
                # sb_id = cur.fetchall()
                # selected_business_id = str(sb_id)
                # selected_business_id = selected_business_id[3:-4]
            elif len(blanketAttributes) == 2:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s'AND value='True')" % (
                    selected_zipcode, blanketPrice[0], blanketCategories[0], blanketAttributes[0],
                    blanketAttributes[1]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}'AND value='True')"
                
                # sb_id = cur.fetchall()
                # selected_business_id = str(sb_id)
                # selected_business_id = selected_business_id[3:-4]
            elif len(blanketAttributes) == 3:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketPrice[0], blanketCategories[0], blanketAttributes[0], blanketAttributes[1],
                    blanketAttributes[2]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[2]}' AND value='True')"
                
                # sb_id = cur.fetchall()
                # selected_business_id = str(sb_id)
                # selected_business_id = selected_business_id[3:-4]
            elif len(blanketAttributes) == 4:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s')" % (
                    selected_zipcode, blanketPrice[0], blanketCategories[0], blanketAttributes[0], blanketAttributes[1],
                    blanketAttributes[2], blanketAttributes[3]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[2]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[3]}')"
                
                # sb_id = cur.fetchall()
                # selected_business_id = str(sb_id)
                # selected_business_id = selected_business_id[3:-4]
            elif len(blanketAttributes) == 5:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketPrice[0], blanketCategories[0], blanketAttributes[0], blanketAttributes[1],
                    blanketAttributes[2], blanketAttributes[3], blanketAttributes[4]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[2]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[3]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[4]}' AND value='True')"
                
                # sb_id = cur.fetchall()
                # selected_business_id = str(sb_id)
                # selected_business_id = selected_business_id[3:-4]

    elif len(blanketCategories) == 2:
        if len(blanketPrice) == 0:
            if len(blanketAttributes) == 0:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s')" % (
                    selected_zipcode, blanketCategories[0], blanketCategories[1]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)
                # 
                # sb = bnameListBox.get(0)
                # # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}')"
                
                # sb_id = cur.fetchall()
                # selected_business_id = str(sb_id)
                # selected_business_id = selected_business_id[3:-4]
            elif len(blanketAttributes) == 1:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketCategories[0], blanketCategories[1], blanketAttributes[0]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True')"
                
#                 sb_id = cur.fetchall()
#                selected_business_id = str(sb_id)
#                selected_business_id = selected_business_id[3:-4]
            elif len(blanketAttributes) == 2:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketCategories[0], blanketCategories[1], blanketAttributes[0],
                    blanketAttributes[1]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True')"
                
#                 sb_id = cur.fetchall()
#                selected_business_id = str(sb_id)
#                selected_business_id = selected_business_id[3:-4]
            elif len(blanketAttributes) == 3:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketCategories[0], blanketCategories[1], blanketAttributes[0],
                    blanketAttributes[1], blanketAttributes[2]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[2]}' AND value='True')"
                
#                 sb_id = cur.fetchall()
#                selected_business_id = str(sb_id)
#                selected_business_id = selected_business_id[3:-4]
            elif len(blanketAttributes) == 4:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketCategories[0], blanketCategories[1], blanketAttributes[0],
                    blanketAttributes[1], blanketAttributes[2], blanketAttributes[3]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[2]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[3]}' AND value='True')"
                
#                 sb_id = cur.fetchall()
#                selected_business_id = str(sb_id)
#                selected_business_id = selected_business_id[3:-4]
            elif len(blanketAttributes) == 5:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketCategories[0], blanketCategories[1], blanketAttributes[0],
                    blanketAttributes[1], blanketAttributes[2], blanketAttributes[3], blanketAttributes[4]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[2]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[3]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[4]}' AND value='True')"
                
#                 sb_id = cur.fetchall()
#                selected_business_id = str(sb_id)
#                selected_business_id = selected_business_id[3:-4]



        elif len(blanketPrice) == 1:
            if len(blanketAttributes) == 0:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s')" % (
                    selected_zipcode, blanketPrice[0], blanketCategories[0], blanketCategories[1]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}')"
                
#                 sb_id = cur.fetchall()
#                selected_business_id = str(sb_id)
#                selected_business_id = selected_business_id[3:-4]
                # category algorithm
            elif len(blanketAttributes) == 1:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketPrice[0], blanketCategories[0], blanketCategories[1],
                    blanketAttributes[0]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True')"
                
#                 sb_id = cur.fetchall()
#                selected_business_id = str(sb_id)
#                selected_business_id = selected_business_id[3:-4]
                # category attribute algorithm
            elif len(blanketAttributes) == 2:
                # category attribute algorithm
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketPrice[0], blanketCategories[0], blanketCategories[1], blanketAttributes[0],
                    blanketAttributes[1]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True')"
                
#                 sb_id = cur.fetchall()
#                selected_business_id = str(sb_id)
#                selected_business_id = selected_business_id[3:-4]
            elif len(blanketAttributes) == 3:
                # category attribute algorithm
                # price and category query
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketPrice[0], blanketCategories[0], blanketCategories[1], blanketAttributes[0],
                    blanketAttributes[1], blanketAttributes[2]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[2]}' AND value='True')"
                
#                 sb_id = cur.fetchall()
#                selected_business_id = str(sb_id)
#                selected_business_id = selected_business_id[3:-4]
            elif len(blanketAttributes) == 4:
                # category attribute algorithm
                # price and category query
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') " % (
                    selected_zipcode, blanketPrice[0], blanketCategories[0], blanketCategories[1], blanketAttributes[0],
                    blanketAttributes[1], blanketAttributes[2], blanketAttributes[3]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[2]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[3]}' AND value='True') "
                
#                 sb_id = cur.fetchall()
#                selected_business_id = str(sb_id)
#                selected_business_id = selected_business_id[3:-4]
            elif len(blanketAttributes) == 5:
                # category attribute algorithm
                # price and category query
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketPrice[0], blanketCategories[0], blanketCategories[1], blanketAttributes[0],
                    blanketAttributes[1], blanketAttributes[2], blanketAttributes[3], blanketAttributes[4]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[2]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[3]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[4]}' AND value='True')"
                
#                 sb_id = cur.fetchall()
#                selected_business_id = str(sb_id)
#                selected_business_id = selected_business_id[3:-4]



        elif len(blanketPrice) == 2:
            if len(blanketAttributes) == 0:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s')" % (
                    selected_zipcode, blanketPrice[0], blanketPrice[1], blanketCategories[0], blanketCategories[1]))
                # category algorithm
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}')"
                
#                 sb_id = cur.fetchall()
#                selected_business_id = str(sb_id)
#                selected_business_id = selected_business_id[3:-4]
            elif len(blanketAttributes) == 1:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketPrice[0], blanketPrice[1], blanketCategories[0], blanketCategories[1],
                    blanketAttributes[0]))
                # category attribute algorithm
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True')"
                
#                 sb_id = cur.fetchall()
#                selected_business_id = str(sb_id)
#                selected_business_id = selected_business_id[3:-4]
            elif len(blanketAttributes) == 2:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') " % (
                    selected_zipcode, blanketPrice[0], blanketPrice[1], blanketCategories[0], blanketCategories[1],
                    blanketAttributes[0], blanketAttributes[1]))
                # category attribute algorithm
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True') "
                
#                 sb_id = cur.fetchall()
#                selected_business_id = str(sb_id)
#                selected_business_id = selected_business_id[3:-4]
            elif len(blanketAttributes) == 3:
                # category attribute algorithm
                # price and category query
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketPrice[0], blanketPrice[1], blanketCategories[0], blanketCategories[1],
                    blanketAttributes[0], blanketAttributes[1], blanketAttributes[2]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[2]}' AND value='True')"
                
#                 sb_id = cur.fetchall()
#                selected_business_id = str(sb_id)
#                selected_business_id = selected_business_id[3:-4]
            elif len(blanketAttributes) == 4:
                # category attribute algorithm
                # price and category query
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketPrice[0], blanketPrice[1], blanketCategories[0], blanketCategories[1],
                    blanketAttributes[0], blanketAttributes[1], blanketAttributes[2], blanketAttributes[3]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[2]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[3]}' AND value='True')"
                
#                 sb_id = cur.fetchall()
#                selected_business_id = str(sb_id)
#                selected_business_id = selected_business_id[3:-4]
            elif len(blanketAttributes) == 5:
                # category attribute algorithm
                # price and category query
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketPrice[0], blanketPrice[1], blanketCategories[0], blanketCategories[1],
                    blanketAttributes[0], blanketAttributes[1], blanketAttributes[2], blanketAttributes[3],
                    blanketAttributes[4]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[2]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[3]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[4]}' AND value='True')"
                
#                 sb_id = cur.fetchall()
#                selected_business_id = str(sb_id)
#                selected_business_id = selected_business_id[3:-4]



    elif len(blanketCategories) == 3:
        if len(blanketPrice) == 0:
            if len(blanketAttributes) == 0:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s')" % (
                    selected_zipcode, blanketCategories[0], blanketCategories[1], blanketCategories[2]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[2]}')"
                
#                 sb_id = cur.fetchall()
#                selected_business_id = str(sb_id)
#                selected_business_id = selected_business_id[3:-4]
            elif len(blanketAttributes) == 1:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketCategories[0], blanketCategories[1], blanketCategories[2],
                    blanketAttributes[0]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[2]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True')"
                
#                 sb_id = cur.fetchall()
#                selected_business_id = str(sb_id)
#                selected_business_id = selected_business_id[3:-4]
            elif len(blanketAttributes) == 2:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketCategories[0], blanketCategories[1], blanketCategories[2],
                    blanketAttributes[0], blanketAttributes[1]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[2]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True')"
                
#                 sb_id = cur.fetchall()
#                selected_business_id = str(sb_id)
#                selected_business_id = selected_business_id[3:-4]
            elif len(blanketAttributes) == 3:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketCategories[0], blanketCategories[1], blanketCategories[2],
                    blanketAttributes[0], blanketAttributes[1], blanketAttributes[2]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[2]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[2]}' AND value='True')"
                
#                 sb_id = cur.fetchall()
#                selected_business_id = str(sb_id)
#                selected_business_id = selected_business_id[3:-4]
            elif len(blanketAttributes) == 4:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketCategories[0], blanketCategories[1], blanketCategories[2],
                    blanketAttributes[0], blanketAttributes[1], blanketAttributes[2], blanketAttributes[3]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[2]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[2]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[3]}' AND value='True')"
                
#                 sb_id = cur.fetchall()
#                selected_business_id = str(sb_id)
#                selected_business_id = selected_business_id[3:-4]
            elif len(blanketAttributes) == 5:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketCategories[0], blanketCategories[1], blanketCategories[2],
                    blanketAttributes[0], blanketAttributes[1], blanketAttributes[2], blanketAttributes[3],
                    blanketAttributes[4]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[2]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[2]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[3]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[4]}' AND value='True')"
                
#                 sb_id = cur.fetchall()
#                selected_business_id = str(sb_id)
#                selected_business_id = selected_business_id[3:-4]



        elif len(blanketPrice) == 1:
            if len(blanketAttributes) == 0:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s')" % (
                    selected_zipcode, blanketPrice[0], blanketCategories[0], blanketCategories[1],
                    blanketCategories[2]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[2]}')"
                
#                 sb_id = cur.fetchall()
#                selected_business_id = str(sb_id)
#                selected_business_id = selected_business_id[3:-4]
                # category algorithm
            elif len(blanketAttributes) == 1:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketPrice[0], blanketCategories[0], blanketCategories[1], blanketCategories[2],
                    blanketAttributes[0]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[2]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True')"
                
#                 sb_id = cur.fetchall()
#                selected_business_id = str(sb_id)
#                selected_business_id = selected_business_id[3:-4]
                # category attribute algorithm
            elif len(blanketAttributes) == 2:
                # category attribute algorithm
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketPrice[0], blanketCategories[0], blanketCategories[1], blanketCategories[2],
                    blanketAttributes[0], blanketAttributes[1]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[2]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True')"
                
#                 sb_id = cur.fetchall()
#                selected_business_id = str(sb_id)
#                selected_business_id = selected_business_id[3:-4]
            elif len(blanketAttributes) == 3:
                # category attribute algorithm
                # price and category query
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketPrice[0], blanketCategories[0], blanketCategories[1], blanketCategories[2],
                    blanketAttributes[0], blanketAttributes[1], blanketAttributes[2]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[2]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[2]}' AND value='True')"
                
#                 sb_id = cur.fetchall()
#                selected_business_id = str(sb_id)
#                selected_business_id = selected_business_id[3:-4]
            elif len(blanketAttributes) == 4:
                # category attribute algorithm
                # price and category query
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') " % (
                    selected_zipcode, blanketPrice[0], blanketCategories[0], blanketCategories[1], blanketCategories[2],
                    blanketAttributes[0], blanketAttributes[1], blanketAttributes[2], blanketAttributes[3]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[2]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[2]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[3]}' AND value='True')"
                
#                 sb_id = cur.fetchall()
#                selected_business_id = str(sb_id)
#                selected_business_id = selected_business_id[3:-4]
            elif len(blanketAttributes) == 5:
                # category attribute algorithm
                # price and category query
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketPrice[0], blanketCategories[0], blanketCategories[1], blanketCategories[2],
                    blanketAttributes[0], blanketAttributes[1], blanketAttributes[2], blanketAttributes[3],
                    blanketAttributes[4]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[2]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[2]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[3]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[4]}' AND value='True')"
                
#                 sb_id = cur.fetchall()
#                selected_business_id = str(sb_id)
#                selected_business_id = selected_business_id[3:-4]

        elif len(blanketPrice) == 2:
            if len(blanketAttributes) == 0:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s')" % (
                    selected_zipcode, blanketPrice[0], blanketPrice[1], blanketCategories[0], blanketCategories[1],
                    blanketCategories[2]))
                # category algorithm
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[2]}')"
                
#                 sb_id = cur.fetchall()
#                selected_business_id = str(sb_id)
#                selected_business_id = selected_business_id[3:-4]
            elif len(blanketAttributes) == 1:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketPrice[0], blanketPrice[1], blanketCategories[0], blanketCategories[1],
                    blanketCategories[2], blanketAttributes[0]))
                # category attribute algorithm
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[2]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True')"
                
#                 sb_id = cur.fetchall()
#                selected_business_id = str(sb_id)
#                selected_business_id = selected_business_id[3:-4]
            elif len(blanketAttributes) == 2:
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') " % (
                    selected_zipcode, blanketPrice[0], blanketPrice[1], blanketCategories[0], blanketCategories[1],
                    blanketCategories[2], blanketAttributes[0], blanketAttributes[1]))
                # category attribute algorithm
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[2]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True')"
                
#                 sb_id = cur.fetchall()
#                selected_business_id = str(sb_id)
#                selected_business_id = selected_business_id[3:-4]
            elif len(blanketAttributes) == 3:
                # category attribute algorithm
                # price and category query
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketPrice[0], blanketPrice[1], blanketCategories[0], blanketCategories[1],
                    blanketCategories[2], blanketAttributes[0], blanketAttributes[1], blanketAttributes[2]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[2]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[2]}' AND value='True')"
                
#                 sb_id = cur.fetchall()
#                selected_business_id = str(sb_id)
#                selected_business_id = selected_business_id[3:-4]
            elif len(blanketAttributes) == 4:
                # category attribute algorithm
                # price and category query
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketPrice[0], blanketPrice[1], blanketCategories[0], blanketCategories[1],
                    blanketCategories[2], blanketAttributes[0], blanketAttributes[1], blanketAttributes[2],
                    blanketAttributes[3]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[2]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[2]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[3]}' AND value='True')"
                
#                 sb_id = cur.fetchall()
#                selected_business_id = str(sb_id)
#                selected_business_id = selected_business_id[3:-4]
            elif len(blanketAttributes) == 5:
                # category attribute algorithm
                # price and category query
                cur.execute(
                    "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                    selected_zipcode, blanketPrice[0], blanketPrice[1], blanketCategories[0], blanketCategories[1],
                    blanketCategories[2], blanketAttributes[0], blanketAttributes[1], blanketAttributes[2],
                    blanketAttributes[3], blanketAttributes[4]))
                nameList = cur.fetchall()
                nameVars = StringVar(value=nameList)

                bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                bnameListBox.grid(column=2, row=2, sticky='nwes')
                bnameListBox.bind("<<ListboxSelect>>", business_selected)

                # sb = bnameListBox.get(0)
                # sb = sb[0]
                bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[2]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[2]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[3]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[4]}' AND value='True')"
                
#                 sb_id = cur.fetchall()
#                selected_business_id = str(sb_id)
#                selected_business_id = selected_business_id[3:-4]


        elif len(blanketCategories) == 4:
            if len(blanketPrice) == 0:
                if len(blanketAttributes) == 0:
                    cur.execute(
                        "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s')" % (
                        selected_zipcode, blanketCategories[0], blanketCategories[1], blanketCategories[2],
                        blanketCategories[3]))
                    nameList = cur.fetchall()
                    nameVars = StringVar(value=nameList)

                    bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                    bnameListBox.grid(column=2, row=2, sticky='nwes')
                    bnameListBox.bind("<<ListboxSelect>>", business_selected)

                    # sb = bnameListBox.get(0)
                    # sb = sb[0]
                    bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[2]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[3]}')"
                    
                    # sb_id = cur.fetchall()
#                    selected_business_id = str(sb_id)
#                    selected_business_id = selected_business_id[3:-4]
                elif len(blanketAttributes) == 1:
                    cur.execute(
                        "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                        selected_zipcode, blanketCategories[0], blanketCategories[1], blanketCategories[2],
                        blanketCategories[3], blanketAttributes[0]))
                    nameList = cur.fetchall()
                    nameVars = StringVar(value=nameList)

                    bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                    bnameListBox.grid(column=2, row=2, sticky='nwes')
                    bnameListBox.bind("<<ListboxSelect>>", business_selected)

                    # sb = bnameListBox.get(0)
                    # sb = sb[0]
                    bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[2]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[3]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True')"
                    
                    # sb_id = cur.fetchall()
#                    selected_business_id = str(sb_id)
#                    selected_business_id = selected_business_id[3:-4]
                elif len(blanketAttributes) == 2:
                    cur.execute(
                        "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                        selected_zipcode, blanketCategories[0], blanketCategories[1], blanketCategories[2],
                        blanketCategories[3], blanketAttributes[0], blanketAttributes[1]))
                    nameList = cur.fetchall()
                    nameVars = StringVar(value=nameList)

                    bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                    bnameListBox.grid(column=2, row=2, sticky='nwes')
                    bnameListBox.bind("<<ListboxSelect>>", business_selected)

                    # sb = bnameListBox.get(0)
                    # sb = sb[0]
                    bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[2]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[3]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True')"
                    
                    # sb_id = cur.fetchall()
#                    selected_business_id = str(sb_id)
#                    selected_business_id = selected_business_id[3:-4]
                elif len(blanketAttributes) == 3:
                    cur.execute(
                        "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                        selected_zipcode, blanketCategories[0], blanketCategories[1], blanketCategories[2],
                        blanketCategories[3], blanketAttributes[0], blanketAttributes[1], blanketAttributes[2]))
                    nameList = cur.fetchall()
                    nameVars = StringVar(value=nameList)

                    bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                    bnameListBox.grid(column=2, row=2, sticky='nwes')
                    bnameListBox.bind("<<ListboxSelect>>", business_selected)

                    # sb = bnameListBox.get(0)
                    # sb = sb[0]
                    bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[2]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[3]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[2]}' AND value='True')"
                    
                    # sb_id = cur.fetchall()
#                    selected_business_id = str(sb_id)
#                    selected_business_id = selected_business_id[3:-4]
                elif len(blanketAttributes) == 4:
                    cur.execute(
                        "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                        selected_zipcode, blanketCategories[0], blanketCategories[1], blanketCategories[2],
                        blanketCategories[3], blanketAttributes[0], blanketAttributes[1], blanketAttributes[2],
                        blanketAttributes[3]))
                    nameList = cur.fetchall()
                    nameVars = StringVar(value=nameList)

                    bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                    bnameListBox.grid(column=2, row=2, sticky='nwes')
                    bnameListBox.bind("<<ListboxSelect>>", business_selected)

                    # sb = bnameListBox.get(0)
                    # sb = sb[0]
                    bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[2]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[3]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[2]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[3]}' AND value='True')"
                    
                    # sb_id = cur.fetchall()
#                    selected_business_id = str(sb_id)
#                    selected_business_id = selected_business_id[3:-4]
                elif len(blanketAttributes) == 5:
                    cur.execute(
                        "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                        selected_zipcode, blanketCategories[0], blanketCategories[1], blanketCategories[2],
                        blanketCategories[3], blanketAttributes[0], blanketAttributes[1], blanketAttributes[2],
                        blanketAttributes[3], blanketAttributes[4]))
                    nameList = cur.fetchall()
                    nameVars = StringVar(value=nameList)

                    bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                    bnameListBox.grid(column=2, row=2, sticky='nwes')
                    bnameListBox.bind("<<ListboxSelect>>", business_selected)

                    # sb = bnameListBox.get(0)
                    # sb = sb[0]
                    bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[2]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[3]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[2]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[3]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[4]}' AND value='True')"
                    
                    # sb_id = cur.fetchall()
#                    selected_business_id = str(sb_id)
#                    selected_business_id = selected_business_id[3:-4]



            elif len(blanketPrice) == 1:
                if len(blanketAttributes) == 0:
                    cur.execute(
                        "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s')" % (
                        selected_zipcode, blanketPrice[0], blanketCategories[0], blanketCategories[1],
                        blanketCategories[2], blanketCategories[3],))
                    nameList = cur.fetchall()
                    nameVars = StringVar(value=nameList)

                    bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                    bnameListBox.grid(column=2, row=2, sticky='nwes')
                    bnameListBox.bind("<<ListboxSelect>>", business_selected)

                    # sb = bnameListBox.get(0)
                    # sb = sb[0]
                    bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[2]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[3]}')"
                    
                    # sb_id = cur.fetchall()
#                    selected_business_id = str(sb_id)
#                    selected_business_id = selected_business_id[3:-4]
                    # category algorithm
                elif len(blanketAttributes) == 1:
                    cur.execute(
                        "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                        selected_zipcode, blanketPrice[0], blanketCategories[0], blanketCategories[1],
                        blanketCategories[2], blanketCategories[3], blanketAttributes[0]))
                    nameList = cur.fetchall()
                    nameVars = StringVar(value=nameList)

                    bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                    bnameListBox.grid(column=2, row=2, sticky='nwes')
                    bnameListBox.bind("<<ListboxSelect>>", business_selected)

                    # sb = bnameListBox.get(0)
                    # sb = sb[0]
                    bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[2]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[3]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True')"
                    
                    # sb_id = cur.fetchall()
#                    selected_business_id = str(sb_id)
#                    selected_business_id = selected_business_id[3:-4]
                    # category attribute algorithm
                elif len(blanketAttributes) == 2:
                    # category attribute algorithm
                    cur.execute(
                        "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                        selected_zipcode, blanketPrice[0], blanketCategories[0], blanketCategories[1],
                        blanketCategories[2], blanketCategories[3], blanketAttributes[0], blanketAttributes[1]))
                    nameList = cur.fetchall()
                    nameVars = StringVar(value=nameList)

                    bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                    bnameListBox.grid(column=2, row=2, sticky='nwes')
                    bnameListBox.bind("<<ListboxSelect>>", business_selected)

                    # sb = bnameListBox.get(0)
                    # sb = sb[0]
                    bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[2]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[3]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True')"
                    
                    # sb_id = cur.fetchall()
#                    selected_business_id = str(sb_id)
#                    selected_business_id = selected_business_id[3:-4]
                elif len(blanketAttributes) == 3:
                    # category attribute algorithm
                    # price and category query
                    cur.execute(
                        "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                        selected_zipcode, blanketPrice[0], blanketCategories[0], blanketCategories[1],
                        blanketCategories[2], blanketCategories[3], blanketAttributes[0], blanketAttributes[1],
                        blanketAttributes[2]))
                    nameList = cur.fetchall()
                    nameVars = StringVar(value=nameList)

                    bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                    bnameListBox.grid(column=2, row=2, sticky='nwes')
                    bnameListBox.bind("<<ListboxSelect>>", business_selected)

                    # sb = bnameListBox.get(0)
                    # sb = sb[0]
                    bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[2]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[3]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[2]}' AND value='True')"
                    
                    # sb_id = cur.fetchall()
#                    selected_business_id = str(sb_id)
#                    selected_business_id = selected_business_id[3:-4]
                elif len(blanketAttributes) == 4:
                    # category attribute algorithm
                    # price and category query
                    cur.execute(
                        "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') " % (
                        selected_zipcode, blanketPrice[0], blanketCategories[0], blanketCategories[1],
                        blanketCategories[2], blanketCategories[3], blanketAttributes[0], blanketAttributes[1],
                        blanketAttributes[2], blanketAttributes[3]))
                    nameList = cur.fetchall()
                    nameVars = StringVar(value=nameList)

                    bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                    bnameListBox.grid(column=2, row=2, sticky='nwes')
                    bnameListBox.bind("<<ListboxSelect>>", business_selected)

                    # sb = bnameListBox.get(0)
                    # sb = sb[0]
                    bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[2]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[3]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[2]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[3]}' AND value='True')"
                    
                    # sb_id = cur.fetchall()
#                    selected_business_id = str(sb_id)
#                    selected_business_id = selected_business_id[3:-4]
                elif len(blanketAttributes) == 5:
                    # category attribute algorithm
                    # price and category query
                    cur.execute(
                        "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                        selected_zipcode, blanketPrice[0], blanketCategories[0], blanketCategories[1],
                        blanketCategories[2], blanketCategories[3], blanketAttributes[0], blanketAttributes[1],
                        blanketAttributes[2], blanketAttributes[3], blanketAttributes[4]))
                    nameList = cur.fetchall()
                    nameVars = StringVar(value=nameList)

                    bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                    bnameListBox.grid(column=2, row=2, sticky='nwes')
                    bnameListBox.bind("<<ListboxSelect>>", business_selected)

                    # sb = bnameListBox.get(0)
                    # sb = sb[0]
                    bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[2]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[3]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[2]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[3]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[4]}' AND value='True')"
                    
                    # sb_id = cur.fetchall()
#                    selected_business_id = str(sb_id)
#                    selected_business_id = selected_business_id[3:-4]

            elif len(blanketPrice) == 2:
                if len(blanketAttributes) == 0:
                    cur.execute(
                        "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s')" % (
                        selected_zipcode, blanketPrice[0], blanketPrice[1], blanketCategories[0], blanketCategories[1],
                        blanketCategories[2], blanketCategories[3]))
                    # category algorithm
                    nameList = cur.fetchall()
                    nameVars = StringVar(value=nameList)

                    bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                    bnameListBox.grid(column=2, row=2, sticky='nwes')
                    bnameListBox.bind("<<ListboxSelect>>", business_selected)

                    # sb = bnameListBox.get(0)
                    # sb = sb[0]
                    bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[2]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[3]}')"
                    
                    # sb_id = cur.fetchall()
#                    selected_business_id = str(sb_id)
#                    selected_business_id = selected_business_id[3:-4]
                elif len(blanketAttributes) == 1:
                    cur.execute(
                        "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                        selected_zipcode, blanketPrice[0], blanketPrice[1], blanketCategories[0], blanketCategories[1],
                        blanketCategories[2], blanketCategories[3], blanketAttributes[0]))
                    # category attribute algorithm
                    nameList = cur.fetchall()
                    nameVars = StringVar(value=nameList)

                    bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                    bnameListBox.grid(column=2, row=2, sticky='nwes')
                    bnameListBox.bind("<<ListboxSelect>>", business_selected)

                    # sb = bnameListBox.get(0)
                    # sb = sb[0]
                    bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[2]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[3]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True')"
                    
                    # sb_id = cur.fetchall()
#                    selected_business_id = str(sb_id)
#                    selected_business_id = selected_business_id[3:-4]
                elif len(blanketAttributes) == 2:
                    cur.execute(
                        "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') " % (
                        selected_zipcode, blanketPrice[0], blanketPrice[1], blanketCategories[0], blanketCategories[1],
                        blanketCategories[2], blanketCategories[3], blanketAttributes[0], blanketAttributes[1]))
                    # category attribute algorithm
                    nameList = cur.fetchall()
                    nameVars = StringVar(value=nameList)

                    bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                    bnameListBox.grid(column=2, row=2, sticky='nwes')
                    bnameListBox.bind("<<ListboxSelect>>", business_selected)

                    # sb = bnameListBox.get(0)
                    # sb = sb[0]
                    bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[2]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[3]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True')"
                    
                    # sb_id = cur.fetchall()
#                    selected_business_id = str(sb_id)
#                    selected_business_id = selected_business_id[3:-4]
                elif len(blanketAttributes) == 3:
                    # category attribute algorithm
                    # price and category query
                    cur.execute(
                        "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                        selected_zipcode, blanketPrice[0], blanketPrice[1], blanketCategories[0], blanketCategories[1],
                        blanketCategories[2], blanketCategories[3], blanketAttributes[0], blanketAttributes[1],
                        blanketAttributes[2]))
                    nameList = cur.fetchall()
                    nameVars = StringVar(value=nameList)

                    bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                    bnameListBox.grid(column=2, row=2, sticky='nwes')
                    bnameListBox.bind("<<ListboxSelect>>", business_selected)

                    # sb = bnameListBox.get(0)
                    # sb = sb[0]
                    bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[2]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[3]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[2]}' AND value='True')"
                    
                    # sb_id = cur.fetchall()
#                    selected_business_id = str(sb_id)
#                    selected_business_id = selected_business_id[3:-4]
                elif len(blanketAttributes) == 4:
                    # category attribute algorithm
                    # price and category query
                    cur.execute(
                        "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                        selected_zipcode, blanketPrice[0], blanketPrice[1], blanketCategories[0], blanketCategories[1],
                        blanketCategories[2], blanketCategories[3], blanketAttributes[0], blanketAttributes[1],
                        blanketAttributes[2], blanketAttributes[3]))
                    nameList = cur.fetchall()
                    nameVars = StringVar(value=nameList)

                    bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                    bnameListBox.grid(column=2, row=2, sticky='nwes')
                    bnameListBox.bind("<<ListboxSelect>>", business_selected)

                    # sb = bnameListBox.get(0)
                    # sb = sb[0]
                    bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[2]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[3]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[2]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[3]}' AND value='True')"
                    
                    # sb_id = cur.fetchall()
#                    selected_business_id = str(sb_id)
#                    selected_business_id = selected_business_id[3:-4]
                elif len(blanketAttributes) == 5:
                    # category attribute algorithm
                    # price and category query
                    cur.execute(
                        "SELECT bname FROM business WHERE zipcode = '%s' AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value='%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '%s') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = '%s' AND value='True')" % (
                        selected_zipcode, blanketPrice[0], blanketPrice[1], blanketCategories[0], blanketCategories[1],
                        blanketCategories[2], blanketCategories[3], blanketAttributes[0], blanketAttributes[1],
                        blanketAttributes[2], blanketAttributes[3], blanketAttributes[4]))
                    nameList = cur.fetchall()
                    nameVars = StringVar(value=nameList)

                    bnameListBox = Listbox(root, listvariable=nameVars, height=20)
                    bnameListBox.grid(column=2, row=2, sticky='nwes')
                    bnameListBox.bind("<<ListboxSelect>>", business_selected)

                    # sb = bnameListBox.get(0)
                    # sb = sb[0]
                    bid_query = f"SELECT business_id FROM business WHERE bname = | AND zipcode = {selected_zipcode} AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[0]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name = 'RestaurantsPriceRange2' AND value= '{blanketPrice[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[0]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[1]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[2]}') AND business_id IN (SELECT business_id FROM categories WHERE category_name = '{blanketCategories[3]}') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[0]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[1]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[2]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[3]}' AND value='True') AND business_id IN (SELECT business_id FROM attributes WHERE attr_name =  '{blanketAttributes[4]}' AND value='True')"
                    
                    # sb_id = cur.fetchall()
#                    selected_business_id = str(sb_id)
#                    selected_business_id = selected_business_id[3:-4]


def price_range_filter(event):
    global filterPriceList, priceRangeListBox, bnameListBox, blanketPrice
    filterPriceList = []
    blanketPrice = []
    # priceList = []
    for i in priceRangeListBox.curselection():
        selected_price = priceRangeListBox.get(i)
        # selected_price = selected_price[0]
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
        # filterPriceList.append(selected_price)
    blanket_search()


def update_business():
    global tipEntry
    global selected_business_id
    global tipList
    selected_business_id = selected_business_id[0]
    tipToString = tipEntry.get()
    tipToStringVar = StringVar(value=tipToString)
    cur.execute("INSERT INTO tip (user_id,business_id,tipdate,tiptext,likes) SELECT '%s','%s','%s','%s','%s'" % (
    '4XChL029mKr5hydo79Ljxg', selected_business_id, '03/31/22', tipToString, '1'))
    tipVars = StringVar(value=tipList)
    tipMessage = Listbox(root, listvariable=tipVars, width=100)


def business_selected(event):
    global bidList
    global selected_business_id
    global tipList
    tips = ''

    # temp = bnameListBox.curselection()
    # sb = bnameListBox.get(temp)
    # # sb = sb[0]
    # print('temp = ', temp)
    # print('sb = ', sb)

    for i in bnameListBox.curselection():
        selected_business = bnameListBox.get(i)
        selected_business = selected_business[0]
        # cur.execute("SELECT business_id FROM business WHERE bname='%s'" %selected_business) #current one
        # selected_business_id = bnameListBox.get(i)[1]
        # print(selected_business_id)
        cur.execute("SELECT address FROM business WHERE business_id='%s'" % selected_business_id)
        bns_address = cur.fetchall()
        # print(bns_address)

        # get day of the week
        current_date = date.today()
        day_of_week = calendar.day_name[current_date.weekday()]
        # print(day_of_week)

        # get open hours of selected business
        cur.execute(
            "SELECT open FROM business, hours WHERE business.business_id = hours.business_id AND dayOfWeek='%s' AND business.business_id='%s'" % (
            day_of_week, selected_business_id))
        bns_open = cur.fetchall()

        # get close hours of selected business
        cur.execute(
            "SELECT close FROM business, hours WHERE business.business_id = hours.business_id AND dayOfWeek='%s' AND business.business_id='%s'" % (
            day_of_week, selected_business_id))
        bns_close = cur.fetchall()

        # get categories of selected business
        cur.execute(
            "SELECT category_name FROM business, categories WHERE business.business_id = categories.business_id AND business.business_id='%s'" % selected_business_id)
        bns_categories = cur.fetchall()
        # bns_categories = list(bns_categories)

        # get attributes of selected business
        cur.execute(
            "SELECT attr_name FROM business, attributes WHERE business.business_id = attributes.business_id AND business.business_id='%s'" % selected_business_id)
        bns_attributes = cur.fetchall()

        # bns_info = Label(root, text='Business Info')
        # bns_info.grid(row=0, column=10)
        bns_info = Text(root, height=12, width=40)
        bns_info.grid(row=0, column=8)
        bns_info.insert('end', 'Business Info\n\n')
        bns_info.insert('end', 'Name: ' + selected_business + '\n')
        bns_info.insert('end', 'Address: ' + str(bns_address[0][0]) + '\n')
        bns_info.insert('end', 'Opens: ' + str(bns_open[0][0]) + '\n')
        bns_info.insert('end', 'Closes: ' + str(bns_close[0][0]) + '\n')
        bns_info.insert('end', 'Categories: ' + str(bns_categories) + '\n')
        bns_info.insert('end', 'Attributes: ' + str(bns_attributes) + '\n')





        cur.execute(
            "SELECT tiptext FROM (SELECT business_id FROM business WHERE bname = '%s') AS bnames, tip WHERE tip.business_id = bnames.business_id" % selected_business)  # testing this one out
        bizIDlist = cur.fetchall()

        if not bizIDlist:
            print("Nothing should happen.")
        else:
            bizTuple = bizIDlist[0]
            bizID = bizTuple[0]

        tipList = bizIDlist
        tipVars = StringVar(value=tipList)

        tipMessage = Listbox(root, listvariable=tipVars, width=100)
        tipMessage.grid(column=0, row=5, sticky='nwes')
        tipMessage.bind("<<ListboxSelect>>")


def attribute_selected(event):
    global selected_zipcode
    global bidList, blanketAttributes, blanketPrice, blanketMeals
    global bnameListBox
    bidList = []
    nameList = []
    attributeList = []
    blanketAttributes = []
    blanketPrice = []
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
        # selected_price = selected_price[0]
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
        # categories = selected_category.split(",")
        print(selected_category)
        categoryList.append(selected_category)
        if selected_category not in blanketCategories:
            blanketCategories.append(selected_category)
    blanket_search()

    # That's enough tags for the user.


def search_clicked():
    global selected_zipcode
    global bnameList
    global bidList
    global bnameListBox
    cur.execute("SELECT bname FROM business WHERE zipcode='%s' ORDER BY bname", selected_zipcode)
    bnameList = cur.fetchall()
    bnameVars = StringVar(value=bnameList)
    # print(bnameList)
    cur.execute("SELECT business_id FROM business WHERE zipcode ='%s'" % selected_zipcode)
    bidList = cur.fetchall()
    bidVars = StringVar(value=bidList)
    bnameListBox = Listbox(root, listvariable=bnameVars, height=20)
    bnameListBox.grid(column=2, row=2, sticky='nwes')
    bnameListBox.bind("<<ListboxSelect>>", business_selected)

    global priceRangeListBox
    priceRangeList = ["$", "$$", "$$$", "$$$$"]
    priceRangeVars = StringVar(value=priceRangeList)
    priceRangeListBox = Listbox(root, listvariable=priceRangeVars, selectmode="multiple", exportselection=False)
    priceRangeListBox.grid(column=6, row=0, sticky='nwes')
    priceRangeListBox.bind("<<ListboxSelect>>", attribute_selected)
    # priceRangeListBox.bind("<<ListboxSelect>>", price_range_filter)

    attributeList = ["Accepts Credit Cards", "Takes Reservations", "Wheelchair Accessible", "Outdoor Seating",
                     "Good for Kids", "Good for Groups", "Delivery", "Take Out", "Free Wi-Fi",
                     "Bike Parking", ]  # cur.fetchall()
    attributeVars = StringVar(value=attributeList)

    global attributeListBox
    attributeListBox = Listbox(root, listvariable=attributeVars, selectmode="multiple", exportselection=False)
    attributeListBox.grid(column=6, row=1, sticky='nwes')
    attributeListBox.bind('<<ListboxSelect>>', attribute_selected)

    mealsList = ["Breakfast", "Lunch", "Brunch", "Dinner", "Dessert", "Late Night"]
    mealsVars = StringVar(value=mealsList)
    global mealsListBox
    mealsListBox = Listbox(root, listvariable=mealsVars, selectmode="multiple", exportselection=False)
    mealsListBox.grid(column=7, row=1, sticky='nwes')
    mealsListBox.bind('<<ListboxSelect>>', attribute_selected)


def zipcode_selected(event):
    global bnameListBox
    global bidList
    for i in zipCodeListBox.curselection():
        global selected_zipcode
        selected_zipcode = zipCodeListBox.get(i)
        # print(selected_zipcode)
        cur.execute(
            "SELECT DISTINCT category_name FROM business, categories WHERE business.zipcode= '%s' AND business.business_id=categories.business_id ORDER BY category_name" % selected_zipcode)
        categoryList = cur.fetchall()
        categoryVars = StringVar(value=categoryList)

        # cur.execute("SELECT DISTINCT attr_name FROM business, attributes WHERE business.zipcode= '%s' AND business.business_id=attributes.business_id ORDER BY attr_name" %selected_zipcode)

        global categoryListBox
        categoryListBox = Listbox(root, listvariable=categoryVars, selectmode="multiple", exportselection=False)
        categoryListBox.grid(column=1, row=3, sticky='nwes')
        categoryListBox.bind('<<ListboxSelect>>', category_selected)


def city_selected(event):
    for i in cityListBox.curselection():
        selected_city = str(cityListBox.get(i))
        selected_city = selected_city[2:-3]

        if stateIsSelected == True:
            cur.execute(
                "SELECT DISTINCT zipcode FROM (SELECT state FROM business WHERE state= '%s' ORDER BY city) business WHERE city= '%s' ORDER BY zipcode" % selected_state % selected_city)
        else:
            cur.execute("SELECT DISTINCT zipcode FROM business WHERE city= '%s' ORDER BY zipcode" % selected_city)
        global zipCodeListBox
        zipCodeList = cur.fetchall()
        stateListBox.grid(column=1, row=0, sticky='nwes')
        stateListBox.bind('<<ListboxSelect>>', state_selected)
        zipCodeVars = StringVar(value=zipCodeList)
        zipCodeListBox = Listbox(root, listvariable=zipCodeVars, exportselection=False)
        zipCodeListBox.grid(column=1, row=2, sticky='nwes')
        zipCodeListBox.bind('<<ListboxSelect>>', zipcode_selected)


def state_selected(event):
    stateIsSelected = True
    for i in stateListBox.curselection():
        selected_state = str(stateListBox.get(i))
        print(selected_state)
        selected_state = selected_state[2:-3]
        print(selected_state)
        cur.execute("SELECT DISTINCT city FROM business WHERE state= '%s' ORDER BY city" % selected_state)
        cityList = cur.fetchall()
        cityVars = StringVar(value=cityList)
        global cityListBox
        cityListBox = Listbox(root, listvariable=cityVars, exportselection=False)
        cityListBox.grid(column=1, row=1, sticky='nwes')
        cityListBox.bind('<<ListboxSelect>>', city_selected)


if __name__ == "__main__":

    cityListBox = stateListBox
    zipCodeListBox = cityListBox
    stateListBox.grid(column=1, row=0, sticky='nwes')
    stateListBox.bind('<<ListboxSelect>>', state_selected)
    searchButton = Button(root, text="Search in zipcode", command=search_clicked)
    searchButton.grid(row=5, column=0)
    # enterTipButton = Button(root, text="Submit tip", command=update_business)
    # enterTipButton.grid(row=8, column=2)
    stateLabel = Label(root, text="State", font=("Arial", 10)).grid(row=0, column=0)
    cityLabel = Label(root, text="City", font=("Arial", 10)).grid(row=1, column=0)
    zipLabel = Label(root, text="Zipcode", font=("Arial", 10)).grid(row=2, column=0)
    categoryLabel = Label(root, text="Categories", font=("Arial", 10)).grid(row=3, column=0)
    attributeLabel = Label(root, text="Attributes", font=("Arial", 10)).grid(row=4, column=0)
    checkinsLabel = Button(root, text="Checkins", command=business_selected_checkins).grid(row=7, column=0)

    root.mainloop()
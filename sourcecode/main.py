import datetime
from bson import ObjectId
from flask import Flask,request,render_template,redirect,session
import pymongo
from Mail import send_email
import os
from dotenv import load_dotenv
load_dotenv()

mongo_uri = os.environ.get("MONGO_URI")
dbConn = pymongo.MongoClient(mongo_uri)
my_db = dbConn["BloodBank"]


admin_col = my_db["admin"]
h_provider_col = my_db["healthCareProvider"]
donor_col = my_db["donor"]
donation_col = my_db["donation"]
blood_stock_col = my_db["bloodStock"]
request_col = my_db["requests"]
timings_col = my_db["timings"]
slots_col = my_db["slots"]




count = admin_col.count_documents({})
if count ==0:
    admin_col.insert_one({"userName":'admin',"password":'admin'})

app = Flask(__name__)
app.secret_key="app"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/alogin")
def alogin():
    return render_template("alogin.html")

@app.route("/hlogin")
def hlogin():
    return render_template("hlogin.html")

@app.route("/dlogin")
def dlogin():
    return render_template("dlogin.html")

@app.route("/adminLoginAction",methods=['post'])
def adminLoginAction():
    userName = request.form.get("userName")
    password = request.form.get("password")
    count = admin_col.count_documents({"password":password,"userName":userName})
    if count >0:
        session['role'] = 'admin'
        return redirect("/adminHome")
    else:
        return render_template("message.html",message="Invalid Login Details",color="text-danger")


@app.route("/adminHome")
def adminHome():
    bloodStocks = blood_stock_col.find({})
    timing = timings_col.find_one({})
    return render_template("adminHome.html",get_donor_by_id2=get_donor_by_id2,get_o_negative_count=get_o_negative_count,bloodStocks=bloodStocks,get_o_positive_count=get_o_positive_count,get_a_positive_count=get_a_positive_count,get_a_negative_count=get_a_negative_count,get_b_positive_count=get_b_positive_count,
                           get_b_negative_count=get_b_negative_count,get_AB_positive_count=get_AB_positive_count,get_AB_negative_count=get_AB_negative_count,timing=timing, int=int)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/hReg")
def hReg():
    return render_template("hReg.html")

@app.route("/hRegAction",methods=['post'])
def hRegAction():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")
    password2 = request.form.get("password2")
    if password!=password2:
        return render_template("message.html",message="Password and Confirm Password Must be Same",color="text-success")
    address = request.form.get("address")
    city = request.form.get('city')
    state = request.form.get('state')
    zipCode = request.form.get("zipCode")

    count = h_provider_col.count_documents({"$or":[{"email":email},{"phone":phone}]})
    if count == 0:
        h_provider_col.insert_one({"first_name":first_name, "last_name":last_name,"email":email,"password":password,"address":address,"phone":phone,"city":city,"zipCode":zipCode, "state": state})
        return render_template("message.html",message="Registered Successfully",color="text-success")
    else:
        return render_template("message.html",message="Duplicate Details",color="text-danger")


@app.route("/healthCareLoginAction",methods=['post'])
def healthCareLoginAction():
    email = request.form.get("email")
    password = request.form.get("password")
    count = h_provider_col.count_documents({"password":password,"email":email})
    if count>0:
        h_provider = h_provider_col.find_one({"password":password,"email":email})
        session['role'] = 'healthCare'
        session['healthCareId'] = str(h_provider['_id'])
        return redirect("/healthCareHome")
    else:
        return render_template("message.html", message="Invalid Login Details", color="text-danger")


@app.route("/healthCareHome")
def healthCareHome():
    healthCare = h_provider_col.find_one({"_id":ObjectId(session['healthCareId'])})
    return render_template("healthCareHome.html",healthCare=healthCare)

@app.route("/dReg")
def dReg():
    return render_template("dReg.html")


@app.route("/dRegAction",methods=['post'])
def dRegAction():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")
    password2 = request.form.get("password2")
    dob = request.form.get("dob")
    city = request.form.get("city")
    state = request.form.get("state")
    zipcode = request.form.get("zipcode")
    address = request.form.get("address")
    if password != password2:
        return render_template("message.html",message="Password and Confirm Password Must be Same",color="text-success")
    count = donor_col.count_documents({"$or":[{"email":email},{"phone":phone}]})
    if count == 0:
        donor_col.insert_one({"first_name":first_name, "last_name":last_name,"email":email,"password":password,"address":address,"phone":phone,"dob":dob, "city": city, "state":state, "zipcode": zipcode})
        return render_template("message.html",message="Donor Registered Successfully",color="text-success")
    else:
        return render_template("message.html",message="Duplicate Details",color="text-danger")


@app.route("/donorLoginAction",methods=['post'])
def donorLoginAction():
    email = request.form.get("email")
    password = request.form.get("password")
    count = donor_col.count_documents({"password":password,"email":email})
    if count>0:
        donor = donor_col.find_one({"password":password,"email":email})
        session['role'] = 'donor'
        session['donorId'] = str(donor['_id'])
        return redirect("/donorHome")
    else:
        return render_template("message.html", message="Invalid Login Details", color="text-danger")

@app.route("/donorHome")
def donorHome():
    donor = donor_col.find_one({"_id":ObjectId(session['donorId'])})
    return render_template("donorHome.html",donor=donor)

@app.route("/sendRequest")
def sendRequest():
    donorId= request.args.get("donorId")
    donor = donor_col.find_one({"_id": ObjectId(donorId)})
    return render_template("sendRequest.html",donor=donor,donorId=donorId)

@app.route("/sendRequest1")
def sendRequest1():
    slot_id = request.args.get("slot_id")
    appointment_date = request.args.get("appointment_date")
    appointment_date = datetime.datetime.strptime(appointment_date, "%Y-%m-%d")
    donorId = session['donorId']
    query = {"donorId":ObjectId(donorId), "slot_id": ObjectId(slot_id), "appointment_date": appointment_date, "status":'Requested'}
    donation_col.insert_one(query)
    donor = donor_col.find_one({"_id": ObjectId(donorId)})
    send_email("Donation Requested", "Donation Request Sent To BloodBank \n Appointment Date "+str(appointment_date.strftime('%Y=%m-%d')), donor['email'])
    return render_template("message.html",message="Donation Request Sent",color="text-primary")


@app.route("/donationRequests")
def donationRequests():
    query = {}
    appointment_date = request.args.get("appointment_date")
    slot_id = request.args.get("slot_id")
    if appointment_date==None:
        appointment_date = datetime.datetime.now().strftime("%Y-%m-%d")
    appointment_date = datetime.datetime.strptime(appointment_date, "%Y-%m-%d")
    if session['role'] =='donor':
        query = {"donorId":ObjectId(session['donorId']),"$or":[{"status":'Requested'},{"status":'Request Rejected'}]}
    elif session['role'] =='admin':
        if slot_id==None:
            query = {"$or":[{"status":'Requested', "appointment_date": appointment_date},{"status":'Request Accepted', "appointment_date": appointment_date},{"status":'Request Rejected', "appointment_date": appointment_date}]}
        else:
            query = {"slot_id": ObjectId(slot_id), "appointment_date": appointment_date}
    donations = donation_col.find(query)
    donations=list(donations)
    date2 = datetime.datetime.now().strftime("%H:%M")
    date2 = datetime.datetime.strptime(date2,"%H:%M" )
    return render_template("donationRequests.html",donations=donations,get_donor_by_id=get_donor_by_id, get_slot_by_slot_id=get_slot_by_slot_id, appointment_date=appointment_date.strftime("%Y-%m-%d"), len=len, date2=date2)

def get_donor_by_id(donorId):
    donor = donor_col.find_one({"_id":ObjectId(donorId)})
    return donor

def get_donor_by_id2(donationId):
    donation = donation_col.find_one({"_id":ObjectId(donationId)})
    donor = donor_col.find_one({"_id":ObjectId(donation['donorId'])})
    return donor
@app.route("/acceptDonorRequest",methods=['post'])
def acceptDonorRequest():
    donationId = request.form.get("donationId")
    appointment_date =  request.form.get("appointment_date")
    query = {'$set':{"status":'Request Accepted'}}
    donation_col.update_one({"_id":ObjectId(donationId)},query)
    return redirect("/donationRequests?appointment_date="+appointment_date)

@app.route("/rejectDonorRequest",methods=['post'])
def rejectDonorRequest():
    donationId = request.form.get("donationId")
    appointment_date =  request.form.get("appointment_date")
    return render_template("rejectDonorRequest.html", donationId=donationId, appointment_date=appointment_date)

@app.route("/rejectDonorRequestAction",methods=['post'])
def rejectDonorRequestAction():
    donationId = request.form.get("donationId")
    appointment_date =  request.form.get("appointment_date")
    reason = request.form.get("reason")
    query = {'$set':{"status":'Request Rejected', "reason": reason}}
    donation_col.update_one({"_id":ObjectId(donationId)},query)
    return redirect("/donationRequests?appointment_date="+appointment_date)

@app.route("/collectBlood",methods=['post'])
def collectBlood():
    donationId = request.form.get("donationId")
    return render_template("collectBlood.html",donationId=donationId)

@app.route("/collectBlood1",methods=['post'])
def collectBlood1():
    donationId = request.form.get("donationId")
    bloodGroup = request.form.get("bloodGroup")
    number_of_units = request.form.get("number_of_units")
    bloodUnitNumber = request.form.get("bloodUnitNumber")
    query = {'$set': {"status": 'Donated',"bloodUnitNumber":bloodUnitNumber,"bloodGroup":bloodGroup, "number_of_units": number_of_units}}
    donation_col.update_one({"_id": ObjectId(donationId)}, query)
    blood_stock_col.insert_one({"donationId":ObjectId(donationId),"bloodUnitNumber":bloodUnitNumber,"status":'Available',"bloodGroup":bloodGroup, "number_of_units": number_of_units, "assigned_units": 0})
    return render_template("message.html",message="Blood Collected",color="text-success")


@app.route("/donations")
def donations():
    query = {}
    if session['role'] =='donor':
        query = {"donorId":ObjectId(session['donorId']),"$or":[{"status":'Donated'}]}
    elif session['role'] =='admin':
        query = {"$or":[{"status":'Donated'}]}
    donations = donation_col.find(query)
    donations = list(donations)
    if len(donations) == 0:
        return render_template("message.html", message="Requests Not Found")
    return render_template("donations.html",donations=donations,get_donor_by_id=get_donor_by_id)

@app.route("/collectDonorBlood")
def collectDonorBlood():
    return render_template("collectDonorBlood.html")

@app.route("/collectDonorBlood1",methods=['post'])
def collectDonorBlood1():
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    bloodGroup = request.form.get("bloodGroup")
    password = request.form.get("password")
    bloodUnitNumber = request.form.get("bloodUnitNumber")
    donor = donor_col.insert_one({"name":name,"email":email,"phone":phone,"bloodGroup":bloodGroup,"password":password})
    donation = donation_col.insert_one({"donorId":ObjectId(donor.inserted_id),"bloodUnitNumber":bloodUnitNumber,"status":'Donated',"bloodGroup":bloodGroup,"date":datetime.datetime.now()})
    blood_stock_col.insert_one({"donationId":ObjectId(donation.inserted_id),"bloodUnitNumber":bloodUnitNumber,"bloodGroup":bloodGroup,"status":'Available'})
    return render_template("message.html",message="Blood Collected",color="text-primary")


@app.route("/sendBloodRequest")
def sendBloodRequest():
    healthCareId = request.args.get("healthCareId")
    return render_template("sendBloodRequest.html",healthCareId=healthCareId)

@app.route("/sendBloodRequest1",methods=['post'])
def sendBloodRequest1():
    healthCareId = request.form.get("healthCareId")
    healthCare = h_provider_col.find_one({"_id": ObjectId(healthCareId)})
    bloodGroups = request.form.getlist("bloodGroup[]")
    numberOfUnitsList = request.form.getlist("numberOfUnits[]")
    email_content = "Blood Request Sent To BloodBank\n"
    for bloodGroup, numberOfUnits in zip(bloodGroups, numberOfUnitsList):
        # Create a request for each blood group and number of units pair
        request_col.insert_one({
            "bloodGroup": bloodGroup,
            "numberOfUnits": int(numberOfUnits),
            "healthCareId": ObjectId(healthCareId),
            "status": 'Requested',
            "assigned": 0,
            "date": datetime.datetime.now()
        })
        # Update the email content
    return render_template("message.html", message="Blood Request Sent", color="text-primary")

    request_col.insert_one(
        {"bloodGroup": bloodGroup, "numberOfUnits": int(numberOfUnits), "healthCareId": ObjectId(healthCareId),
         "status": 'Requested', "assigned": 0, "date": datetime.datetime.now()})
    send_email("Blood Requested",
               "Blood Request Sent To BloodBank \n Required BloodGroup " + str(bloodGroup) + ",\n Required : " + str(
                   numberOfUnits) + " units ", healthCare['email'])
    return render_template("message.html", message="Blood Request Sent", color="text-primary")


@app.route("/healthCareRequests")
def healthCareRequests():
    query = {}
    if session['role'] =='admin':
        query = {"$or":[{"status":'Requested'},{"status":'Request Accepted'},{"status":'Request Rejected'},{"status":'Assigned'}]}
    elif session['role'] =='healthCare':
        query = {"healthCareId":ObjectId(session['healthCareId']),"$or":[{"status":'Requested'},{"status":'Request Accepted'},{"status":'Assigned'}]}
    healthCareRequests = request_col.find(query)
    healthCareRequests = list(healthCareRequests)
    if len(healthCareRequests) == 0:
        return render_template("message.html", message="Requests Not Found")
    return render_template("healthCareRequests.html",get_is_BloodAssigned_by_id=get_is_BloodAssigned_by_id,healthCareRequests=healthCareRequests,get_healthCare_by_id=get_healthCare_by_id,int=int)

def get_healthCare_by_id(healthCareId):
    healthCare = h_provider_col.find_one({"_id":ObjectId(healthCareId)})
    return healthCare

@app.route("/acceptBloodRequest",methods=['post'])
def acceptBloodRequest():
    healthCareRequestId = request.form.get("healthCareRequestId")
    query = {'$set':{"status":'Request Accepted'}}
    request_col.update_one({"_id":ObjectId(healthCareRequestId)},query)
    return redirect("/healthCareRequests")


@app.route("/rejectBloodRequest",methods=['post'])
def rejectBloodRequest():
    healthCareRequestId = request.form.get("healthCareRequestId")
    return render_template("rejectBloodRequest.html", healthCareRequestId=healthCareRequestId)
@app.route("/rejectBloodRequestAction",methods=['post'])
def rejectBloodRequestAction():
    healthCareRequestId = request.form.get("healthCareRequestId")
    reason = request.form.get("reason")
    query = {'$set':{"status":'Request Rejected', "reason": reason}}
    request_col.update_one({"_id":ObjectId(healthCareRequestId)},query)
    return redirect("/healthCareRequests")

@app.route("/assignBlood",methods=['post'])
def assignBlood():
    healthCareRequestId = request.form.get("healthCareRequestId")
    bloodGroup = request.form.get("bloodGroup")
    units_required = request.form.get("units_required")
    query = {"bloodGroup":bloodGroup,'status':'Available'}
    blood_stocks = blood_stock_col.find(query)
    return render_template("assignBlood.html",get_donor_by_id2=get_donor_by_id2,blood_stocks=blood_stocks,bloodGroup=bloodGroup,healthCareRequestId=healthCareRequestId, int=int, units_required=units_required)

@app.route("/assignBloodAction",methods=['post'])
def assignBloodAction():
    bloodStockId = request.form.get('bloodStockId')
    healthCareRequestId = request.form.get("healthCareRequestId")
    number_of_units = request.form.get("number_of_units")
    healthCare_request = request_col.find_one({"_id":ObjectId(healthCareRequestId)})
    assigned = healthCare_request['assigned']
    assigned = int(assigned)
    assigned = assigned+int(number_of_units)
    query = {"$set":{"assigned":assigned}}
    request_col.update_one({"_id":ObjectId(healthCareRequestId)},query)
    blood_stock = blood_stock_col.find_one({"_id": ObjectId(bloodStockId)})
    query2 = {"$set":{"assigned_units": int(blood_stock['assigned_units'])+ int(number_of_units)}}
    blood_stock_col.update_one({"_id":ObjectId(bloodStockId)},query2)
    return render_template("message.html",message="Blood Assigned")


def get_is_BloodAssigned_by_id(requestId,units,assigned):
    if int(units) == int(assigned):
        request_col.update_one({"_id":ObjectId(requestId)},{"$set":{"status":'Assigned'}})
        return "hiii"
    return "hello"



def get_o_negative_count():
    stocks = blood_stock_col.find({"bloodGroup":'O-'})
    available = 0
    for stock in stocks:
        available = available + int(stock['number_of_units'])-int(stock['assigned_units'])
    return available

def get_o_positive_count():
    stocks = blood_stock_col.find({"bloodGroup": 'O+'})
    available = 0
    for stock in stocks:
        available = available + int(stock['number_of_units']) - int(stock['assigned_units'])
    return available

def get_a_positive_count():
    stocks = blood_stock_col.find({"bloodGroup": 'A+'})
    available = 0
    for stock in stocks:
        available = available + int(stock['number_of_units']) - int(stock['assigned_units'])
    return available

def get_a_negative_count():
    stocks = blood_stock_col.find({"bloodGroup": 'A-'})
    available = 0
    for stock in stocks:
        available = available + int(stock['number_of_units']) - int(stock['assigned_units'])
    return available


def get_b_positive_count():
    stocks = blood_stock_col.find({"bloodGroup": 'B+'})
    available = 0
    for stock in stocks:
        available = available + int(stock['number_of_units']) - int(stock['assigned_units'])
    return available


def get_b_negative_count():
    stocks = blood_stock_col.find({"bloodGroup": 'B-'})
    available = 0
    for stock in stocks:
        available = available + int(stock['number_of_units']) - int(stock['assigned_units'])
    return available


def get_AB_positive_count():
    stocks = blood_stock_col.find({"bloodGroup": 'AB+'})
    available = 0
    for stock in stocks:
        available = available + int(stock['number_of_units']) - int(stock['assigned_units'])
    return available


def get_AB_negative_count():
    stocks = blood_stock_col.find({"bloodGroup": 'AB-'})
    available = 0
    for stock in stocks:
        available = available + int(stock['number_of_units']) - int(stock['assigned_units'])
    return available


@app.route("/rejectedRequests")
def rejectedRequests():
    query = {"healthCareId": ObjectId(session['healthCareId']),
             "$or": [{"status": 'Request Rejected'}]}
    healthCareRequests = request_col.find(query)
    return render_template("rejectedRequests.html",healthCareRequests=healthCareRequests,get_healthCare_by_id=get_healthCare_by_id)

@app.route("/update_timings")
def update_timings():
    timing = timings_col.find_one({})
    return render_template("update_timings.html", timing=timing)

@app.route("/update_timings_action")
def update_timings_action():
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")
    start_time = datetime.datetime.strptime(start_time, "%H:%M")
    end_time = datetime.datetime.strptime(end_time, "%H:%M")
    if start_time > end_time:
        return render_template("message.html", message="End Time should grater then Start time", color="text-primary")
    timings_col.delete_many({})
    slots_col.delete_many({})
    query = {"start_time": start_time, "end_time": end_time}
    timings_col.insert_one(query)
    slot_number = 1
    while start_time < end_time:
        slot_start_time = start_time
        start_time = start_time + datetime.timedelta(minutes=30)
        slot_end_time = start_time
        query = {"slot_start_time": slot_start_time, "slot_end_time":slot_end_time, "slot_number": slot_number}
        slots_col.insert_one(query)
        slot_number = slot_number + 1
        if start_time + datetime.timedelta(minutes=30) > end_time:
            break
    return redirect("/adminHome")

@app.route("/slots")
def slots():
    appointment_date = request.args.get("appointment_date")
    if appointment_date==None:
        appointment_date = datetime.datetime.now().strftime("%Y-%m-%d")
    slots = slots_col.find({})
    slots = list(slots)
    timing = timings_col.find_one({})
    return render_template("slots.html", slots=slots, appointment_date=appointment_date, timing=timing, is_slot_booked=is_slot_booked, datetime=datetime, get_appointment_date_time=get_appointment_date_time, can_book_slot_on_this_date=can_book_slot_on_this_date)
def get_appointment_date_time(appointment_date, slot_start_time):
    appointment_date_time = appointment_date+" "+slot_start_time.strftime("%H:%M")
    appointment_date_time = datetime.datetime.strptime(appointment_date_time, "%Y-%m-%d %H:%M")
    return appointment_date_time

def can_book_slot_on_this_date(appointment_date):
    appointment_date = datetime.datetime.strptime(appointment_date, "%Y-%m-%d")
    donorId = session['donorId']
    query = {"donorId": ObjectId(donorId), "appointment_date": appointment_date, "status": {"$in": ["Requested", "Request Accepted"]}}
    count = donation_col.count_documents(query)
    if count > 0:
        return False
    else:
        return True
def get_slot_by_slot_id(slot_id):
    query = {"_id": slot_id}
    slot = slots_col.find_one(query)
    return slot

@app.route("/view_donor")
def view_donor():
    donorId = request.args.get("donorId")
    query ={"_id": ObjectId(donorId)}
    donor = donor_col.find_one(query)
    return render_template("view_donor.html", donor=donor)

def is_slot_booked(slot_id, appointment_date):
    appointment_date = datetime.datetime.strptime(appointment_date, "%Y-%m-%d")
    query = {"slot_id": slot_id, "appointment_date": appointment_date, "status": {"$in": ["Requested", "Request Accepted"]}}
    count = donation_col.count_documents(query)
    if count > 0:
        return True
    else:
        return False

@app.route("/view_health_care_provider")
def view_health_care_provider():
    health_care_provider_id = request.args.get("health_care_provider_id")
    query = {"_id": ObjectId(health_care_provider_id)}
    health_care_provider = h_provider_col.find_one(query)
    return render_template("view_health_care_provider.html", health_care_provider=health_care_provider)

@app.route("/addBloodStock")
def addBloodStock():
    return render_template("addBloodStock.html")


@app.route("/addBloodStock1",methods=['post'])
def addBloodStock1():
    bloodUnitNumber = request.form.get("bloodUnitNumber")
    number_of_units = request.form.get("number_of_units")
    bloodGroup = request.form.get("bloodGroup")
    blood_stock_col.insert_one({"bloodUnitNumber":bloodUnitNumber,"status":'Available',"bloodGroup":bloodGroup, "number_of_units": number_of_units, "assigned_units": 0})
    return redirect("/adminHome")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

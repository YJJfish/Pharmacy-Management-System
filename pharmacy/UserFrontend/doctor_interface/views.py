from django.http import HttpResponse, HttpRequest, HttpResponseNotFound, Http404
from django.views.generic import RedirectView
from django.shortcuts import render, redirect, reverse
from django.utils.http import urlencode
from urllib.parse import urlparse, parse_qs
import json
import jpype
from django.views.decorators.csrf import csrf_exempt


JavaClassPath = "../DatabaseBackend/se-pharmacy/target/classes/"
JarPath = "../DatabaseBackend/se-pharmacy/bin/src/main/java/mysql-connector-java-8.0.27.jar"

if (not jpype.isJVMStarted()):
    jpype.startJVM("-ea", classpath=[JavaClassPath, JarPath])

# One instance per thread
JavaAppClass = jpype.JClass("com.example.MyJDBC")
JavaApp = JavaAppClass()

# Database interface
def getAllBranch():
    return eval(str(JavaApp.getAllBranch()))
def searchMedicine(SearchContent : str, BranchName : str, PageID : int = 1):
    if (not isinstance(PageID, int)):
        PageID = int(PageID)
    return eval(str(JavaApp.searchMedicine(SearchContent, BranchName, PageID)))
def queryMedicine(MediID : str, BranchName : str):
    return eval(str(JavaApp.queryMedicine(MediID, BranchName)))
def getShoppingCart(UserID : str, BranchName : str):
    return eval(str(JavaApp.getShoppingCart(UserID, BranchName)))
def setShoppingCart(UserID : str, MediID : str, BranchName : str, Num : int):
    if (not isinstance(Num, int)):
        Num = int(Num)
    return int(JavaApp.setShoppingCart(UserID, MediID, BranchName, Num))
def addShoppingCart(UserID : str, MediID : str, BranchName : str, Num : int):
    if (not isinstance(Num, int)):
        Num = int(Num)
    return int(JavaApp.addShoppingCart(UserID, MediID, BranchName, Num))
def deleteShoppingCart(UserID : str, MediID : str, BranchName : str, Num : int):
    if (not isinstance(Num, int)):
        Num = int(Num)
    return int(JavaApp.deleteShoppingCart(UserID, MediID, BranchName, Num))
def commitBill(UserID : str, BranchName : str):
    return int(JavaApp.commitBill(UserID, BranchName))

# Invoked by Doctor Frontend, in order to get the medicine information.
# URL: doctor_interface/querymedicine/
# Params: PageID (optional, default=1), BranchName (optional, default="玉古路店"), SearchContent (optional, default="")
#   For example: doctor_interface/querymedicine/?PageID=3
# Return: Json package of all medicine in the specified page
#   Return format:
#   {
#       "MediList" : [
#           {
#            "ID" : ID, "Brand" : Brand, "Name" : Name, "Description" : Description, "Usage" : Usage, "Taboo" : Taboo,
#            "Price" : Price, "URL" : URL, "Num" : Num, "Unit" : Unit, "Prescripted" : 0/1
#           },
#           {
#            "ID" : ID, "Brand" : Brand, "Name" : Name, "Description" : Description, "Usage" : Usage, "Taboo" : Taboo,
#            "Price" : Price, "URL" : URL, "Num" : Num, "Unit" : Unit, "Prescripted" : 0/1
#           },
#           ......
#       ],
#       "NumPages" : NumPages
#   }
def QueryMedicine(Request : HttpRequest):
    # We only accept GET package
    if (Request.method != "GET"):
        return Http404
    # Use empty keywords, to search for all medicine
    SearchContent = ""
    # Use default branch
    Branches = getAllBranch()
    BranchName = Branches[0]
    # Use default page
    PageID = 1
    # Decode URL
    if (Request.get_full_path().find("?") != -1):
        ParsedURL = urlparse(Request.get_full_path())
        Dict = parse_qs(ParsedURL.query)
        if ("PageID" in Dict):
            PageID = int(Dict["PageID"][0])
            if (PageID <= 0):
                return Http404
        if ("BranchName" in Dict):
            BranchName = Dict["BranchName"][0]
            if not (BranchName in Branches):
                return Http404
        if ("SearchContent" in Dict):
            SearchContent = Dict["SearchContent"][0]
    # Call the interface of the database
    Ret = searchMedicine(SearchContent, BranchName, PageID)
    # Return
    return HttpResponse(json.dumps(Ret))

# Invoked by Doctor Frontend, in order to add medicine to users' pharmacy cart.
# URL: doctor_interface/prescmedicine/
# Params: Json package of the bill
#   Params format:
#   {
#       "patient_id" : ... ,
#       "bill" : [
#                   {"medName": ..., "val": ...},
#                   {"medName": ..., "val": ...},
#                   {"medName": ..., "val": ...},
#                ]
#       "branch_name" : branch_name (optional, default="玉古路店")
#   }
# Return: 1 for success, 0 for failure
@csrf_exempt
def PrescMedicine(Request : HttpRequest):
    # We only accept POST package
    if (Request.method != "POST"):
        return Http404
    # Decode package body
    Data = json.loads(Request.body.decode("utf-8"))
    # Get the user id from the package body
    UserID = Data.get("patient_id") # Type: str
    # Get the content of the prescription
    Prescription = Data.get("bill") # Type: list
    # Use default branch
    Branches = getAllBranch()
    BranchName = Branches[0]
    if ("branch_name" in Data):
        BranchName = Data.get("branch_name")
        if not (BranchName in Branches):
            return HttpResponse(0)
    # Call the interface of the database
    # TODO: Rollback the whole transaction when encountering a failure
    for Item in Prescription:
        Suc = addShoppingCart(UserID, Item.get("medName"), BranchName, Item.get("val"))
        if (not Suc):
            return HttpResponse(0)
    return HttpResponse(1)

# Invoked by Doctor Frontend, in order to get users' pharmacy cart.
# URL: doctor_interface/querycart/
# Params: UserID, BranchName (optional, default="玉古路店")
#   For example: doctor_interface/querycart/?UserID=8
# Return: Json package of the user shopping cart
#   Return Format:
#   {
#       "BillList" : [
#           {
#               "ItemList" : [
#                               {
#                                "ID" : ID, "Brand" : Brand, "Name" : Name, "Description" : Description, "Usage" : Usage, "Taboo" : Taboo,
#                                "Price" : Price, "URL" : URL, "Num" : Num, "Unit" : Unit, "Prescripted" : 0/1
#                               },
#                               {
#                                "ID" : ID, "Brand" : Brand, "Name" : Name, "Description" : Description, "Usage" : Usage, "Taboo" : Taboo,
#                                "Price" : Price, "URL" : URL, "Num" : Num, "Unit" : Unit, "Prescripted" : 0/1
#                               },
#                               ......
#                            ],
#               "Date" : Date,
#               "BillID" : BillID,
#               "QueueID" : QueueID,
#               "WindowID" : WindowID
#           },
#           ......
#       ],
#   }
def QueryCart(Request : HttpRequest):
    # We only accept GET package
    if (Request.method != "GET"):
        return Http404
    # Decode URL
    ParsedURL = urlparse(Request.get_full_path())
    Dict = parse_qs(ParsedURL.query)
    if not ("UserID" in Dict):
        return Http404
    # Get the user id from the URL
    UserID = Dict["UserID"][0] # Type: str
    # Use default branch
    Branches = getAllBranch()
    BranchName = Branches[0]
    if ("BranchName" in Dict):
        BranchName = Dict["BranchName"][0]
        if not (BranchName in Branches):
            return Http404
    # Call the interface of the database
    Ret = getShoppingCart(UserID, BranchName)
    # Pack into json package
    # Return
    return HttpResponse(json.dumps(Ret))

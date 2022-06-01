from django.http import HttpResponse, HttpRequest, HttpResponseNotFound, Http404
from django.views.generic import RedirectView
from django.shortcuts import render, redirect, reverse
import json
import jpype


JavaClassPath = "../DatabaseBackend/se-pharmacy/bin/src/main/java/"
JarPath = "../DatabaseBackend/se-pharmacy/bin/src/main/java/mysql-connector-java-8.0.27.jar"

if (not jpype.isJVMStarted()):
    jpype.startJVM("-ea", classpath=[JavaClassPath, JarPath])

# One instance per thread
JavaAppClass = jpype.JClass("com.example.MyJDBC")
JavaApp = JavaAppClass()

# Database interface
def getAllBranch():
    return eval(str(JavaApp.getAllBranch()))
def searchMedicine(SearchContent : str, BranchName : str):
    return eval(str(JavaApp.searchMedicine(SearchContent, BranchName)))
def queryMedicine(MediID : str, BranchName : str):
    return eval(str(JavaApp.queryMedicine(MediID, BranchName)))[0]
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
# Params: None
# Return: Information of all medicine : string
#   Return format:
#   [
#       [ID, Brand, Name, Description, Usage, Taboo, Price, ImageURL, Stock, Units],
#       ["001","国药","阿司匹林","解热镇痛","一日三次","三高人群",25.0,"https://s2.loli.net/2022/05/06/.png",50, "盒"]
#       ["002","国药","头孢","头孢就酒，越喝越勇","一日三次","三高人群",24.0,"https://s2.loli.net/2022/05/06/.png",10, "盒"],
#   ]
def QueryMedicine(Request : HttpRequest):
    # We only accept POST package
    if (Request.method != "POST"):
        return Http404
    # Use empty keywords, to search for all medicine
    SearchContent = ""
    # Use default branch
    BranchName=getAllBranch()[0]
    # Call the interface of the database
    Ret = searchMedicine(SearchContent, BranchName)
    # Return
    return HttpResponse(str(Ret))

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
#   }
# Return: 1 for success, 0 for failure
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
    BranchName = getAllBranch()[0]
    # Call the interface of the database
    # TODO: Rollback the whole transaction when encountering a failure
    for Item in Prescription:
        Suc = addShoppingCart(UserID, Item.get("medName"), BranchName, Item.get("val"))
        if (not Suc):
            return HttpResponse(0)
    return HttpResponse(1)
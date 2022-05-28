from django.http import HttpResponse, HttpRequest, HttpResponseNotFound, Http404
from django.views.generic import RedirectView
from django.shortcuts import render, redirect, reverse
import qrcode
import base64
from io import BytesIO
import socket
import json
import time


#Get all the hospital branches from the database
def GetHospitalBranch(Request : HttpRequest):
    return ["Branch1", "Branch2", "Branch3", "Branch4"]

#Rendering the log page
def LoginPage(Request : HttpRequest):
    Request.encoding='utf-8'
    return render(Request, 'pharmacy_user/login.html') 

#Rendering home page
#Render index.html or login.html, depending on whether the user has logged.
def HomePage(Request : HttpRequest):
    Request.encoding='utf-8'
     #If haven't logged in, redirect to login page
    if not (Request.session.has_key('Logged') and Request.session['Logged']==True):
        return redirect("login")
    #Render
    Context = {"UserName_" : Request.session['NAME']}
    return render(Request, "pharmacy_user/index.html", Context)
    

#Try to log in
def TryLogin(Request : HttpRequest):
    #Validate the information. You can make this function more complex
    #e.g. fetch information from the database.
    def ValidateLogin(ID : str, NAME : str, PASSWORD : str):
        return True
    Request.encoding='utf-8'
    ID = Request.POST.get("ID")
    NAME = Request.POST.get("NAME")
    PASSWORD = Request.POST.get("PASSWORD")
    REMEMBER = Request.POST.get('REMEMBER')
    Response = redirect("home")
    if ValidateLogin(ID, NAME, PASSWORD):
        if REMEMBER:
            Response.set_cookie('ID', ID, max_age=60*5)
            Response.set_cookie('NAME', NAME, max_age=60*5)
            Response.set_cookie('PASSWORD', PASSWORD, max_age=60*5)
        Request.session['Logged'] = True
        Request.session['ID'] = ID
        Request.session['NAME'] = NAME
        Request.session['PASSWORD'] = PASSWORD
    return Response

#Contact page
def ContactPage(Request : HttpRequest):
    return render(Request, 'pharmacy_user/contact.html')

#About page
def AboutPage(Request : HttpRequest):
    return render(Request, 'pharmacy_user/about.html')

#Search page
def SearchPage(Request : HttpRequest, Selected_ : str = ""):
    #This function searches the database and returns the result.
    #You can replace it with functions you implemented by yourself.
    def Search(SearchText : str, BranchName : str):
        Result = [
            ["001","国药","头孢","头孢就酒，越喝越勇",25.0,"https://s2.loli.net/2022/05/06/Fp3MwJu1U8tbi96.png"],
            ["002","国药","阿司匹林","解热镇痛",25.0,"https://s2.loli.net/2022/05/06/q7ulP6FDjtVOMQE.png"]
        ]
        return Result
    Request.encoding='utf-8'
    #If haven't logged in, redirect to home page
    if not (Request.session.has_key('Logged') and Request.session['Logged']==True):
        return redirect("home")
    #Get all branch names
    BranchList_ = GetHospitalBranch(Request)
    #Get the current selected branch name
    if (Selected_ == ""):
        return redirect(reverse("search") + BranchList_[0])
    if (not Selected_ in BranchList_):
        raise Http404
    #Search
    if (Request.POST):
        SearchContent_ = Request.POST.get("SEARCH")
    else:
        SearchContent_ = ""
    ResultList_ = Search(SearchContent_, Selected_)
    Context = {"BranchList_" : BranchList_, "Selected_" : Selected_, "SearchContent_" : SearchContent_, "ResultList_" : ResultList_, "UserID_" : Request.session['ID']}
    return render(Request, "pharmacy_user/search.html", Context)

#Account page
def AccountPage(Request : HttpRequest):
    Request.encoding='utf-8'
    #If haven't logged in, redirect to home page
    if not (Request.session.has_key('Logged') and Request.session['Logged']==True):
        return redirect("home")
    Context = {"UserName_" : Request.session['NAME']}
    return render(Request, "pharmacy_user/account.html", Context)

#Bill page
def BillPage(Request : HttpRequest, Selected_ : str = ""):
    #Get all the bills corresponding to "UserID" and "BranchName"
    def GetShoppingCart(UserID, BranchName):
        Bill1Item = [
            ["001","国药","头孢","头孢就酒，越喝越勇",25.0,"https://s2.loli.net/2022/05/06/Fp3MwJu1U8tbi96.png", 5],
            ["002","国药","阿司匹林","解热镇痛",25.0,"https://s2.loli.net/2022/05/06/q7ulP6FDjtVOMQE.png", 10]
        ]
        Bill2Item = [
            ["001","国药","头孢","头孢就酒，越喝越勇",25.0,"https://s2.loli.net/2022/05/06/Fp3MwJu1U8tbi96.png", 20],
            ["002","国药","阿司匹林","解热镇痛",25.0,"https://s2.loli.net/2022/05/06/q7ulP6FDjtVOMQE.png", 2]
        ]
        Bill3Item = [
            ["002","国药","阿司匹林","解热镇痛",25.0,"https://s2.loli.net/2022/05/06/q7ulP6FDjtVOMQE.png", 5],
            ["001","国药","头孢","头孢就酒，越喝越勇",25.0,"https://s2.loli.net/2022/05/06/Fp3MwJu1U8tbi96.png", 6]
            
        ]
        Bills = [[Bill1Item, "", -1, -1], [Bill2Item, "U14bTQFS", 59, 3], [Bill3Item, "I12bSDBA", 121, 6]]
        return Bills
    Request.encoding='utf-8'
    #If haven't logged in, redirect to home page
    if not (Request.session.has_key('Logged') and Request.session['Logged']==True):
        return redirect("home")
    #Get all branch names
    BranchList_ = GetHospitalBranch(Request)
    #Get the current selected branch name
    if (Selected_ == ""):
        return redirect(reverse("bill") + BranchList_[0])
    if (not Selected_ in BranchList_):
        raise Http404
    #Get the bills
    Bills_ = GetShoppingCart(Request.session['ID'], Selected_)
    #Calculate sum
    for Bill_ in Bills_:
        Sum = 0
        for Item_ in Bill_[0]:
            Sum += Item_[4]*Item_[6]
        Bill_.append(Sum)
    #Return the webpage
    Context = {"BranchList_" : BranchList_, "Selected_" : Selected_, "Bills_" : Bills_, "UserID_" : Request.session['ID']}
    return render(Request, "pharmacy_user/bill.html", Context)

#Checkout page
def CheckoutPage(Request : HttpRequest, Selected_ : str = ""):
    #Generate a QR code
    def GenerateQR(UserID, BrandName, Version = 2, BoxSize = 10, Border = 5):
        QR = qrcode.QRCode(version = Version, box_size = BoxSize, border = Border)
        # Adding the data to be encoded to the QRCode object
        QR.add_data(UserID + "_" + BrandName)
        # Making the entire QR Code space utilized
        QR.make(fit = True)
        # Generating the QR Code
        Img = QR.make_image()
        # Base64 encode
        Buffer = BytesIO()
        Img.save(Buffer, format="JPEG")
        return base64.b64encode(Buffer.getvalue()).decode()
    Request.encoding='utf-8'
    #If haven't logged in, redirect to home page
    if not (Request.session.has_key('Logged') and Request.session['Logged']==True):
        return redirect("home")
    #Get all branch names
    BranchList_ = GetHospitalBranch(Request)
    #Get the current selected branch name
    if (not Selected_ in BranchList_):
        raise Http404
    #Get the base64 encoded QR image
    QRImg64 = GenerateQR(Request.session['ID'], Selected_)
    print(QRImg64)
    Context = {"QRCode64_" : QRImg64, "Selected_" : Selected_}
    return render(Request, "pharmacy_user/checkout.html", Context)

#MedicineInfo page
def MedicineInfoPage(Request : HttpRequest, Selected_ : str = "", MediID : str = ""):
    def GetMediInfo(MediID : str, BranchName : str):
        Result = [
            # ["001","国药","头孢","头孢就酒，越喝越勇",25.0,"https://s2.loli.net/2022/05/06/Fp3MwJu1U8tbi96.png"],
            # ["002","国药","阿司匹林","解热镇痛",25.0,"https://s2.loli.net/2022/05/06/q7ulP6FDjtVOMQE.png"]
            ["001","国药","头孢","头孢就酒，越喝越勇","口服。成人服用的常规剂量为一次0.1g，一日3次", \
            "对本品有休克史者禁用。对青霉素或头孢菌素有过敏史者慎用",25.0,"https://s2.loli.net/2022/05/06/Fp3MwJu1U8tbi96.png"],
            ["002","国药","阿司匹林","解热镇痛","口服。肠溶片应饭前用适量水送服", \
            "对阿司匹林或其它水杨酸盐，或药品的任何其它成份过敏者禁用",25.0,"https://s2.loli.net/2022/05/06/q7ulP6FDjtVOMQE.png"]
        ]
        MediID = int(MediID)
        if MediID == 1:
            return Result[0]
        elif MediID == 2:
            return Result[1]
        else:
            return None
    Request.encoding='utf-8'
    #If haven't logged in, redirect to home page
    if not (Request.session.has_key('Logged') and Request.session['Logged']==True):
        return redirect("home")
    #Get all branch names
    BranchList_ = GetHospitalBranch(Request)
    #Get the current selected branch name
    if (not Selected_ in BranchList_):
        raise Http404
    MediInfo_ = GetMediInfo(MediID, Selected_)
    if (MediInfo_ == None):
        raise Http404
    Context = {"MediInfo_" : MediInfo_, "Selected_" : Selected_, "UserID_" : Request.session['ID']}
    return render(Request, "pharmacy_user/mediinfo.html", Context)

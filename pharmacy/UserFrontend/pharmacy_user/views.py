from django.http import HttpResponse, HttpRequest, HttpResponseNotFound, Http404
from django.views.generic import RedirectView
from django.shortcuts import render, redirect, reverse
from django.utils.http import urlencode
from urllib.parse import urlparse, parse_qs
import qrcode
import base64
from io import BytesIO
import json
import jpype


JavaClassPath = "../DatabaseBackend/se-pharmacy/target/classes/"
JarPath = "../DatabaseBackend/se-pharmacy/bin/src/main/java/mysql-connector-java-8.0.27.jar"

if (not jpype.isJVMStarted()):
    jpype.startJVM("-ea", classpath=[JavaClassPath, JarPath])

# One instance per thread
JavaAppClass = jpype.JClass("com.example.MyJDBC")
JavaApp = JavaAppClass()

RunLocally = True
if (RunLocally):
    IPAddr = "127.0.0.1"
    Port = "8000"
else:
    IPAddr = "124.220.171.17"
    Port = "6666"

LoginAddr = "http://124.220.171.17:3000/login"

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

# Rendering the log page
def LoginPage(Request : HttpRequest):
    Request.encoding='utf-8'
    return render(Request, 'pharmacy_user/login.html') 

# Rendering home page
# Render index.html or login.html, depending on whether the user has logged.
def HomePage(Request : HttpRequest):
    Request.encoding='utf-8'
    # If the url contains user information, store it in session
    if (Request.get_full_path().find("?") != -1):
        ParsedURL = urlparse(Request.get_full_path())
        Dict = parse_qs(ParsedURL.query)
        if ("userId" in Dict and "userName" in Dict and "token" in Dict):
            Request.session['Logged'] = True
            Request.session['ID'] = Dict["userId"][0]
            Request.session['NAME'] = Dict["userName"][0]
            Request.session['TOKEN'] = Dict["token"][0]
    # If haven't logged in, redirect to login page
    if not (Request.session.has_key('Logged') and Request.session['Logged']==True):
        #return redirect("login")
        return redirect(LoginAddr+"?"+urlencode({"redir":IPAddr+":"+Port+Request.get_full_path()}))
    # Render
    Context = {"UserName_" : Request.session['NAME']}
    return render(Request, "pharmacy_user/index.html", Context)

# Contact page
def ContactPage(Request : HttpRequest):
    return render(Request, 'pharmacy_user/contact.html')

# About page
def AboutPage(Request : HttpRequest):
    return render(Request, 'pharmacy_user/about.html')

# Search page
def SearchPage(Request : HttpRequest, Selected_ : str = ""):
    Request.encoding='utf-8'
    # If haven't logged in, redirect to home page
    if not (Request.session.has_key('Logged') and Request.session['Logged']==True):
        return redirect("home")
    # Get all branch names
    BranchList_ = getAllBranch()
    # Get the current selected branch name
    if (Selected_ == ""):
        return redirect(reverse("search") + BranchList_[0])
    if (not Selected_ in BranchList_):
        raise Http404
    # Get the current page
    PageID = 1
    if (Request.get_full_path().find("?") != -1):
        ParsedURL = urlparse(Request.get_full_path())
        Dict = parse_qs(ParsedURL.query)
        if ("PageID" in Dict):
            PageID = int(Dict["PageID"][0])
            if (PageID <= 0):
                return Http404
    # Search
    if (Request.POST):
        SearchContent_ = Request.POST.get("SEARCH")
    else:
        SearchContent_ = ""
    Ret = searchMedicine(SearchContent_, Selected_, PageID)
    ResultList_ = Ret["MediList"]
    NumPages_ = Ret["NumPages"]
    if (NumPages_ <= 7):
        PageList_ = [str(i+1) for i in range(NumPages_)]
    elif (PageID <= 4):
        PageList_ = [str(i+1) for i in range(5)]+["...", str(NumPages_)]
    elif (PageID >= NumPages_-3):
        PageList_ = ["1", "..."]+[str(i+1) for i in range(NumPages_-5,NumPages_)]
    else:
        PageList_ = ["1", "..."]+[str(i+1) for i in range(PageID-3,PageID+2)]+["...", str(NumPages_)]
    Context = {"BranchList_" : BranchList_, "Selected_" : Selected_, "SearchContent_" : SearchContent_, "ResultList_" : ResultList_, "UserID_" : Request.session['ID'], "PageList_" : PageList_, "CurrPage_" : str(PageID)}
    return render(Request, "pharmacy_user/search.html", Context)

# Account page
def AccountPage(Request : HttpRequest):
    Request.encoding='utf-8'
    # If haven't logged in, redirect to home page
    if not (Request.session.has_key('Logged') and Request.session['Logged']==True):
        return redirect("home")
    Context = {"UserName_" : Request.session['NAME']}
    return render(Request, "pharmacy_user/account.html", Context)

# Bill page
def BillPage(Request : HttpRequest, Selected_ : str = ""):
    Request.encoding='utf-8'
    # If haven't logged in, redirect to home page
    if not (Request.session.has_key('Logged') and Request.session['Logged']==True):
        return redirect("home")
    # Get all branch names
    BranchList_ = getAllBranch()
    # Get the current selected branch name
    if (Selected_ == ""):
        return redirect(reverse("bill") + BranchList_[0])
    if (not Selected_ in BranchList_):
        raise Http404
    # Get the bills
    Ret = getShoppingCart(Request.session['ID'], Selected_)
    Bills_ = Ret["BillList"][::-1]
    # Return the webpage
    Context = {"BranchList_" : BranchList_, "Selected_" : Selected_, "Bills_" : Bills_, "UserID_" : Request.session['ID']}
    return render(Request, "pharmacy_user/bill.html", Context)

# Checkout page
def CheckoutPage(Request : HttpRequest, Selected_ : str = ""):
    # Generate a QR code
    def GenerateQR(UserID, BrandName, Version = 2, BoxSize = 10, Border = 5):
        QR = qrcode.QRCode(version = Version, box_size = BoxSize, border = Border)
        #  Adding the data to be encoded to the QRCode object
        QR.add_data(UserID + "_" + BrandName)
        #  Making the entire QR Code space utilized
        QR.make(fit = True)
        #  Generating the QR Code
        Img = QR.make_image()
        #  Base64 encode
        Buffer = BytesIO()
        Img.save(Buffer, format="JPEG")
        return base64.b64encode(Buffer.getvalue()).decode()
    Request.encoding='utf-8'
    # If haven't logged in, redirect to home page
    if not (Request.session.has_key('Logged') and Request.session['Logged']==True):
        return redirect("home")
    # Get all branch names
    BranchList_ = getAllBranch()
    # Get the current selected branch name
    if (not Selected_ in BranchList_):
        raise Http404
    # Get the base64 encoded QR image
    QRImg64 = GenerateQR(Request.session['ID'], Selected_)
    Context = {"QRCode64_" : QRImg64, "Selected_" : Selected_}
    return render(Request, "pharmacy_user/checkout.html", Context)

# MedicineInfo page
def MedicineInfoPage(Request : HttpRequest, Selected_ : str = "", MediID : str = ""):
    Request.encoding='utf-8'
    # If haven't logged in, redirect to home page
    if not (Request.session.has_key('Logged') and Request.session['Logged']==True):
        return redirect("home")
    # Get all branch names
    BranchList_ = getAllBranch()
    # Get the current selected branch name
    if (not Selected_ in BranchList_):
        raise Http404
    MediInfo_ = queryMedicine(MediID, Selected_)
    if (MediInfo_ == None):
        raise Http404
    Context = {"MediInfo_" : MediInfo_, "Selected_" : Selected_, "UserID_" : Request.session['ID']}
    return render(Request, "pharmacy_user/mediinfo.html", Context)



def AddItem(Request : HttpRequest):
    if (Request.method != "POST"):
        return Http404
    Data = json.loads(Request.body.decode("utf-8"))
    UserID=Data.get("UserID")
    MediID=Data.get("MediID")
    BranchName=Data.get("BranchName")
    return HttpResponse(addShoppingCart(UserID, MediID, BranchName, 1))

def SetItem(Request : HttpRequest):
    if (Request.method != "POST"):
        return Http404
    Data = json.loads(Request.body.decode("utf-8"))
    UserID=Data.get("UserID")
    MediID=Data.get("MediID")
    BranchName=Data.get("BranchName")
    Num=Data.get("Num")
    return HttpResponse(setShoppingCart(UserID, MediID, BranchName, Num))

def CommitBill(Request : HttpRequest):
    if (Request.method != "POST"):
        return Http404
    Data = json.loads(Request.body.decode("utf-8"))
    UserID=Data.get("UserID")
    BranchName=Data.get("BranchName")
    return HttpResponse(commitBill(UserID, BranchName))
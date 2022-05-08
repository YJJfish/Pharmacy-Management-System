from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect

#Rendering home page
#Render index.html or login.html, depending on whether the user has logged.
def HomePage(Request : HttpRequest):
    Request.encoding='utf-8'
    if Request.session.has_key('Logged') and Request.session['Logged']==True:
        return render(Request, 'index.html')
    else:
        return render(Request, 'login.html') 

#Try to log in
def TryLogin(Request : HttpRequest):
    #Validate the information. You can make this function more complex
    #e.g. fetch information from the database.
    def ValidateLogin(ID : str, NAME : str, PASSWORD : str):
        return (ID=="123456" and NAME=="YJJ" and PASSWORD=="YJJ")
    Request.encoding='utf-8'
    ID = Request.POST.get("ID")
    NAME = Request.POST.get("NAME")
    PASSWORD = Request.POST.get("PASSWORD")
    REMEMBER = Request.POST.get('REMEMBER')
    Response = redirect("/home")
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
    return render(Request, 'contact.html')

#About page
def AboutPage(Request : HttpRequest):
    return render(Request, 'about.html')

#Search page
def SearchPage(Request : HttpRequest):
    #This function searches the database and returns the result.
    #You can replace it with functions you implemented by yourself.
    def Search(SearchText : str):
        Result = [
            ["001","国药","头孢","头孢就酒，越喝越勇",25.0,"https://s2.loli.net/2022/05/06/Fp3MwJu1U8tbi96.png"],
            ["002","国药","阿司匹林","解热镇痛",25.0,"https://s2.loli.net/2022/05/06/q7ulP6FDjtVOMQE.png"]
        ]
        return Result
    Request.encoding='utf-8'
    #If haven't logged in, redirect to home page
    if not (Request.session.has_key('Logged') and Request.session['Logged']==True):
        return redirect("/home")
    #Otherwise, search
    if (Request.POST):
        SEARCH = Request.POST.get("SEARCH")
    else:
        SEARCH = ""
    RESULT = Search(SEARCH)
    Context = {"SearchContent_" : SEARCH, "ResultList_" : RESULT}
    return render(Request, "search.html", Context)

#Account page
def AccountPage(Request : HttpRequest):
    Context = {"UserName_" : Request.session['NAME']}
    return render(Request, "account.html", Context)

#Profile page
def ProfilePage(Request : HttpRequest):
    Context = {"UserName_" : Request.session['NAME']}
    return render(Request, "profile.html", Context)

#Bill page
def BillPage(Request : HttpRequest):
    Context = {"UserName_" : Request.session['NAME']}
    return render(Request, "bill.html", Context)
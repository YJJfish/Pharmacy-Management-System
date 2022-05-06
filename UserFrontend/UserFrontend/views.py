from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect


# 表单
def search_form(request):
    return render(request, 'search_form.html')

#接收并处理搜索数据
def Search(Request : HttpRequest):  
    Request.encoding='utf-8'
    ctx ={}
    if Request.POST:
        ctx['rlt'] = Request.POST['q']
    return render(Request, "post.html", ctx)

#Rendering home page
#Render index.html or login.html, depending on whether the user has logged.
def HomePage(Request : HttpRequest):
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
    print(REMEMBER)
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
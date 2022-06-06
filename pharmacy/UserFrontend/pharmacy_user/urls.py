from django.urls import path, include, re_path
from django.views.generic import RedirectView


from pharmacy_user import views

urlpatterns = [
    # Web pages
    path('', RedirectView.as_view(url='home')),
    path("login/", views.LoginPage, name="login"),
    path("home/", views.HomePage, name="home"),
    path('contact/', views.ContactPage, name="contact"),
    path('about/', views.AboutPage, name="about"),
    path('search/', views.SearchPage, name="search"),
    re_path(r'search/(?P<Selected_>.*)/', views.SearchPage),
    path('account/', views.AccountPage, name="account"),
    path('bill/', views.BillPage, name="bill"),
    re_path(r'bill/(?P<Selected_>.*)/', views.BillPage),
    path('checkout/', views.CheckoutPage, name="checkout"),
    re_path(r"checkout/(?P<Selected_>.*)/", views.CheckoutPage),
    path("medicineinfo/", views.MedicineInfoPage, name="medicineinfo"),
    re_path(r"medicineinfo/(?P<Selected_>.*)/(?P<MediID>[0-9]+)", views.MedicineInfoPage),

    # Invoked by javascript, in order to interact with the database
    path('additem/', views.AddItem, name='additem'),
    path('setitem/', views.SetItem, name='setitem'),
    path('commitbill/', views.CommitBill, name='commitbill'),
]

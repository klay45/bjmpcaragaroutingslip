from django.urls import path
from .import views
from django.urls import include,path
from django.contrib import admin


urlpatterns = [
    path('', views.index, name='index'),
    path('test/', views.test, name='test'),  
    path('aboutus/', views.aboutus, name='aboutus'),
    path('loginuser/', views.loginuser, name='loginuser'),
    path('logoutuser/', views.logoutuser, name='logoutuser'),
    path('registeruser/',views.registeruser, name='registeruser'),
    path('displayletter/',views.displayletter, name='displayletter'),
    path('displayletter/displaylettermore/',views.displaylettermore, name='displaylettermore'),
    path('displayletter/displaylettermore/updateletter/<int:id>', views.updateletter, name='updateletter'),
    path('displayletter/updateletter/<int:id>', views.updateletter, name='updateletter'),
    path('displayletterRCDS/',views.displayletterRCDS, name='displayletterRCDS'),
    path('displayletterRCDS/letteraction/<int:id>',views.letteraction, name='letteraction'),
    path('displayletterRCDS/displaypdf/<int:id>',views.displaypdf, name='displaypdf'),
    path('displaymsgcenter/displaypdfmsgcenter/<int:id>',views.displaypdfmsgcenter, name='displaypdfmsgcenter'),
    path('displayletterRCDS/letteractionardo/<int:id>',views.letteractionardo, name='letteractionardo'),
    path('displayletterRCDS/letteractionarda/<int:id>',views.letteractionarda, name='letteractionarda'),
    path('displayletterRCDS/letteractionrd/<int:id>',views.letteractionrd, name='letteractionrd'),
    path('displaymsgcenter/msgcenteraction/<int:id>',views.msgcenteraction, name='msgcenteraction'),
    path('displayletter/letteraction/<int:id>', views.letteraction, name='letteraction'),
    path('displayletter/displaypdf/<int:id>', views.displaypdf, name='displaypdf'),
    path('displayletter/displaylettermore/displaypdf/<int:id>', views.displaypdf, name='displaypdf'),
    path('adddivision1/', views.adddivision1, name='adddivision1'),
    path('adddivision/',views.adddivision, name='adddivision'),
    path('addletter/',views.addletter, name='addletter'),
    path('addprofileimage/',views.addprofileimage, name='addprofileimage'),
    path('profile/',views.profile, name='profile'),
    path('status/',views.status, name='status'),
    path('doanloadidapp/',views.downloadidapp, name='downloadidapp'),
    path('importidforclaim/',views.importidforclaim, name='importidforclaim'),
    path('importidforclaimadmin/',views.importidforclaimadmin, name='importidforclaimadmin'),
    path('importdeptanddesignation/',views.importdeptanddesignation, name='importdeptanddesignation'),
    path('displayid/',views.displayid, name='displayid'),
    path('displayidadmin/',views.displayidadmin, name='displayidadmin'),
    path('displayid/updateremarks/<int:id>', views.updateremarks, name='updateremarks'),
    path('displayidadmin/reapplyid/<int:id>', views.reapplyid, name='reapplyid'),
    path('displayid/searchidapplication', views.searchidapplication, name='searchidapplication'),
    path('displayletter111/searchletterarda', views.searchletterarda, name='searchletterarda'),
    path('displayletter1111/searchletterrd', views.searchletterrd, name='searchletterrd'),
    path('displayletter1/searchletter', views.searchletter, name='searchletter'),
    path('displayidadmin/searchidapplicationadmin', views.searchidapplicationadmin, name='searchidapplicationadmin'),
    path('displayid/updateremarks1/<int:id>', views.updateremarks1, name='update'),
    path('displayidadmin/updateremarks1admin/<int:id>', views.updateremarks1admin, name='updateremarks1admin'),
    path('displayid/updateremarks1/updaterecord/<int:id>', views.updaterecord, name='updaterecord'),
    path('displayidadmin/updateremarks1admin/updaterecordadmin/<int:id>', views.updaterecordadmin, name='updaterecordadmin'),
    path('displayid/refreshdata', views.refreshdata, name='refreshdata'),
    path('activeapplication/',views.activeapplication,name='activeapplication'),
    path('addid/',views.addid,name='addid'),
    path('downloadidadmin/',views.downloadidadmin,name='downloadidadmin'),
    path('displayletter/modal_view/<int:id>', views.modal_view, name="modal_view"),
    path('displayletter/modal_view_arda/<int:id>', views.modal_view_arda, name="modal_view_arda"),
    path('displayletter/modal_view_rd/<int:id>', views.modal_view_rd, name="modal_view_rd"),
    path('displayletter/modal_view_ardo/<int:id>', views.modal_view_ardo, name="modal_view_ardo"),
    path('notifications/',views.notifications, name='notifications'),
    path('notifications/notificationread/<str:id>/<str:id2>', views.notificationread, name='notificationread'),
    path('notification_count_api/',views.notification_count_api,name='notification_count_api'),

    path('register_token/', views.register_token, name='register_token'),
    path('send_notification/', views.send_notification, name='send_notification'),
    path('displaymsgcenter/',views.displaymsgcenter, name='displaymsgcenter'),

   path('displayletter/routingslip_pdf/<pk>/',views.routingslip_pdf,name='routingslip_pdf')


    
]
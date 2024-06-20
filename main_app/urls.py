from django.urls import path
from . import views

urlpatterns = [
    path('',views.home, name ='home'),
    path('signup/',views.signup, name = 'signup'),
    path('logout/',views.signout, name = 'logout'),
    path('signin/',views.signin, name = 'signin'),
    path('trapecio/',views.trapecio, name = 'trapecio'),
    path('muller/',views.muller, name = 'muller'),
    path('historial/',views.historial, name = 'historial'),
    path('historial/eliminar/<int:pk>/', views.eliminar_historial, name='eliminar_historial')
]

from django.urls import path
from . import views

app_name = 'common'

urlpatterns = [
    path('', views.index, name='index'),  # <a href="{% url 'index' %}">Home</a>.
    path('places/', views.PlaceListView.as_view(), name='places'),
    path('place/<int:pk>', views.PlaceDetailView.as_view(), name='place-detail'),
    path('suggest/', views.SuggestionView.as_view(), name='suggest-place'),
    path('suggest_data/', views.SuggestionViewData.as_view(), name='suggest-data'),
    path('user_place_data/', views.UserPlaceData.as_view(), name='user-place-data'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('export/', views.export, name='export'),
]
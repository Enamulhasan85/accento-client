from django.urls import include, path

app_name = 'identity'

urlpatterns = [
    path('v1/', include('bold_voice.identity.api.v1.urls')),
]

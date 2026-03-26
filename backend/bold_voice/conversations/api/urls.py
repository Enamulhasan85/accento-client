from django.urls import include, path

app_name = 'conversations'

urlpatterns = [
    path('v1/', include('bold_voice.conversations.api.v1.urls')),
]

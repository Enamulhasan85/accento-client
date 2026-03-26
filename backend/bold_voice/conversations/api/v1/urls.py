from django.urls import path, include
from rest_framework.routers import DefaultRouter

from bold_voice.conversations.api.v1.views import (
    CategoryViewSet,
    ScenarioViewSet,
    VoiceChatViewSet,
    PhonemeCategoryViewSet,
    PhonemeViewSet,
    PracticeSpeakingTextAPIView,
    PracticeTextBookmarkViewSet, SpeechScanSessionViewSet, AppConfigAPIView,
)

app_name = 'v1'

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'scenarios', ScenarioViewSet, basename='scenario')
router.register(r'voice-chats', VoiceChatViewSet, basename='voice-chat')
router.register(r'phoneme-categories', PhonemeCategoryViewSet, basename='phoneme-category')
router.register(r'phonemes', PhonemeViewSet, basename='phoneme')
router.register(r'practice-text-bookmarks', PracticeTextBookmarkViewSet, basename='practice-text-bookmark')
router.register(r'speech-scan-sessions', SpeechScanSessionViewSet, basename='speech-scan-session')

urlpatterns = [
    path('', include(router.urls)),
    path('app-configuration/', AppConfigAPIView.as_view(), name='app-config'),
    path('practice/speaking-text/', PracticeSpeakingTextAPIView.as_view(), name='practice-speaking-text'),
]

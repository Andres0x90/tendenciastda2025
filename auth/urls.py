from rest_framework.routers import DefaultRouter

from auth import views
from auth.front.views.AuthFrontView import AuthFrontView

router = DefaultRouter()
router.register(r'auth', views.AuthView, basename='auth')
router.register('front/auth', AuthFrontView, basename='auth_front')

urlpatterns = router.urls
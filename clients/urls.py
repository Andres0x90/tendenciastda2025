from rest_framework.routers import DefaultRouter

from clients.front.views.ClientsFrontView import ClientsFrontView
from clients.views import ClientView

router = DefaultRouter()

router.register(r'clients', ClientView, basename='clients')
router.register('front/clients', ClientsFrontView, basename='clients_front')

urlpatterns = router.urls
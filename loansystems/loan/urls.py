
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import views as auth_view
from django.views.i18n import set_language

urlpatterns = [
    # path('', include('pages.urls')),# URL for 404 handler
    path(_('admin/'), admin.site.urls),
    path('', include('pwa.urls')),
    path('', include('usermanager.urls')),
    path('reset_password/', auth_view.PasswordResetView.as_view(), name="reset_password"),
    path('reset_password_sent/', auth_view.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_view.PasswordResetConfirmView.as_view(), name="password_confirm"),
    path('reset_password_complete/', auth_view.PasswordResetCompleteView.as_view(), name="reset_password_complete"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns += i18n_patterns(
    path('', include('usermanager.urls')),
    path("__reload__/", include("django_browser_reload.urls")),
    path("__debug__/", include("debug_toolbar.urls")),
    # path('accounts/', include('django.contrib.auth.urls'))
)

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [
        re_path(r'^rosetta/', include('rosetta.urls')),
        
    ] 
# add a flag for
# handling the 404 error
handler404 = 'usermanager.views.error_404_view'
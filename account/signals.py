from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from account.models import UserLogin


@receiver(user_logged_in)
def track_user_login(sender, request, user, **kwargs):
    """
    Track user login with IP address and user agent
    """
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    UserLogin.objects.create(
        user=user,
        ip_address=ip_address,
        user_agent=user_agent
    )


def get_client_ip(request):
    """
    Get client IP address from request
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

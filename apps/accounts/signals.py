from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, pre_save
from django.conf import settings
from django.apps import apps
from apps.audits.middleware import get_current_request
from apps.utils.security.network import get_client_ip, get_user_device_info

@receiver(pre_save, sender=settings.AUTH_USER_MODEL)
def capture_user_changes(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            instance._old_instance = old_instance
        except sender.DoesNotExist:
            pass

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def log_user_save(sender, instance, created, **kwargs):
    changed_fields = None
    if not created:
        if kwargs.get('update_fields'):
            changed_fields = set(kwargs.get('update_fields'))
        elif hasattr(instance, '_old_instance'):
            changed_fields = set()
            old_instance = instance._old_instance
            for field in instance._meta.concrete_fields:
                if getattr(old_instance, field.name) != getattr(instance, field.name):
                    changed_fields.add(field.name)

        if changed_fields and len(changed_fields) == 1 and 'last_login' in changed_fields:
            return

    ActivityLog = apps.get_model('audits', 'ActivityLog')
    request = get_current_request()
    
    actor = None
    ip_address = None
    device_info = None
    
    if request:
        actor = request.user if request.user.is_authenticated else None
        ip_address = get_client_ip(request)
        device_info = get_user_device_info(request)

    if created:
        action = "USER_CREATED"
        description = f"Created user: {instance.email}"
    else:
        action = "USER_UPDATED"
        fields_str = f" (Fields: {', '.join(sorted(changed_fields))})" if changed_fields else ""
        description = f"Updated user: {instance.email}{fields_str}"

    ActivityLog.objects.create(
        actor=actor,
        module='accounts',
        action=action,
        description=description,
        ip_address=ip_address,
        user_agent=device_info
    )

@receiver(post_delete, sender=settings.AUTH_USER_MODEL)
def log_user_deletion(sender, instance, **kwargs):
    ActivityLog = apps.get_model('audits', 'ActivityLog')
    request = get_current_request()
    
    actor = None
    ip_address = None
    device_info = None
    
    if request:
        actor = request.user if request.user.is_authenticated else None
        ip_address = get_client_ip(request)
        device_info = get_user_device_info(request)
        
        if actor and actor.pk == instance.pk:
            actor = None

    ActivityLog.objects.create(
        actor=actor,
        module='accounts',
        action="USER_DELETED",
        description=f"Deleted user: {instance.email}",
        ip_address=ip_address,
        user_agent=device_info
    )
def get_client_ip(request):
    """
    ฟังก์ชันดึง IP Address ของผู้ใช้ โดยรองรับการทำงานผ่าน Proxy
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_user_device_info(request):
    """
    ดึงข้อมูลอุปกรณ์ (Device) ของผู้ใช้จาก request object
    (จำเป็นต้องมี django-user-agents middleware ติดตั้งและเปิดใช้งาน)

    Returns:
        str: ข้อความสรุปข้อมูลอุปกรณ์ เช่น "Desktop (Windows 10; Chrome 108.0.0)"
    """
    user_agent = getattr(request, 'user_agent', None)
    if not user_agent:
        return "Unknown Device"

    if user_agent.is_mobile:
        device_type = "Mobile"
    elif user_agent.is_tablet:
        device_type = "Tablet"
    elif user_agent.is_pc:
        device_type = "PC"
    else:
        device_type = "Unknown"

    os_info = f"{user_agent.os.family} {user_agent.os.version_string}".strip()
    browser_info = f"{user_agent.browser.family} {user_agent.browser.version_string}".strip()

    return f"{device_type} ({os_info}; {browser_info})"

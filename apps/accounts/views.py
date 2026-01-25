from django.shortcuts import render
from django.core.cache import cache
from django.contrib.auth import login, logout
from django.shortcuts import redirect
import logging

from apps.accounts.models import User
from apps.utils.otp.otp_manager import generate_otp
from apps.utils.redis_stream.send_otp import queue_email_task
from apps.utils.security.network import get_client_ip

logger = logging.getLogger("security_logger")


def request_otp(request):
    if request.method == "POST":
        email = request.POST.get("email")

        logger.info(f"OTP Requested: Email {email} from IP {get_client_ip(request)}")

        req_limit_key = f"otp_req_limit:{email}"
        if cache.get(req_limit_key):
            return render(request, "login.html", {
                "error": "กรุณารอ 60 วินาทีก่อนขอรหัสใหม่อีกครั้ง"
            })

        user, created = User.objects.get_or_create(email=email)
        if created:
            user.set_unusable_password()
            user.save()

        otp_code, otp_ref = generate_otp(6)
        cache.set(f"otp_code:{email}", otp_code, timeout=300)
        cache.set(f"otp_ref:{email}", otp_ref, timeout=300)

        email_context = {
            "otp_code": otp_code,
            "otp_ref": otp_ref,
        }
        queue_email_task(
            email=email,
            task_type="login_verification",
            context=email_context
        )

        cache.set(req_limit_key, True, timeout=60)
        return render(request, "verify_otp.html", {"email": email, "otp_ref": otp_ref})
    
    return render(request, "login.html")

def verify_otp(request):
    if request.method == "POST":
        email = request.POST.get("email")
        otp_input = request.POST.get("otp_code")
        otp_ref = cache.get(f"otp_ref:{email}")
        ip_addr = get_client_ip(request)
        
        block_key = f"otp_blocked:{email}"
        if cache.get(block_key):
            logger.warning(f"BLOCKED ACCESS ATTEMPT: Email {email} from IP {ip_addr}")
            return render(request, "verify_otp.html", {
                "email": email,
                "error": "คุณกรอกรหัสผิดเกินกำหนด กรุณาลองใหม่ในอีก 15 นาที",
                "otp_ref": otp_ref
            })

        otp_in_cache = cache.get(f"otp_code:{email}")
        fail_count_key = f"otp_fail_cnt:{email}"

        if otp_in_cache and otp_in_cache == otp_input:
            logger.info(f"LOGIN SUCCESS: User {email} from IP {ip_addr}")
            cache.delete(f"otp_code:{email}")
            cache.delete(f"otp_ref:{email}")
            cache.delete(fail_count_key)
            
            user = User.objects.get(email=email)
            login(request, user)
            return redirect("index")
        else:
            current_fails = cache.get(fail_count_key, 0) + 1
            logger.warning(f"INVALID OTP: Attempt by {email} from IP {ip_addr}")
            
            if current_fails >= 5:
                logger.critical(f"USER BANNED: {email} exceeded attempts from IP {ip_addr}")
                cache.set(block_key, True, timeout=900)
                cache.delete(fail_count_key)
                error_msg = "คุณกรอกรหัสผิดเกินกำหนด ระบบระงับการเข้าใช้งาน 15 นาที"
            else:
                cache.set(fail_count_key, current_fails, timeout=300)
                error_msg = f"รหัส OTP ไม่ถูกต้อง (เหลือโอกาสอีก {5 - current_fails} ครั้ง)"

            return render(request, "verify_otp.html", {
                "email": email,
                "error": error_msg,
                "otp_ref": otp_ref
            })
            
    return redirect("request_otp")

def logout_view(request):
    if request.user.is_authenticated:
        ip_addr = get_client_ip(request)
        logger.info(f"LOGOUT SUCCESS: User {request.user.email} logged out from IP {ip_addr}")
    logout(request)
    return redirect("index")
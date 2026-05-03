import hmac
import hashlib
from django.conf import settings

def verify_webhook(request):
    secret = settings.PAYCHANGU_SECRET_KEY.encode()

    payload = request.body

    signature = request.headers.get('Signature')

    if not signature:
        return False

    computed_signature = hmac.new(
        secret,
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(computed_signature, signature)
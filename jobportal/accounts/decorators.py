# from django.http import JsonResponse, HttpResponseForbidden
# from django.shortcuts import redirect
# from accounts.utils import decode_jwt
# from accounts.models import User
 
 
# def hybrid_auth_required(allowed_roles=None):
#     def decorator(view_func):
#         def wrapper(request, *args, **kwargs):
 
#             # ======================
#             # 1️⃣ JWT AUTH (API)
#             # ======================
#             auth_header = request.headers.get('Authorization')
 
#             if auth_header and auth_header.startswith('Bearer '):
#                 token = auth_header.split(' ')[1]
#                 payload = decode_jwt(token)
 
#                 if not payload:
#                     return JsonResponse({'error': 'Invalid or expired token'}, status=401)
 
#                 try:
#                     user = User.objects.get(id=payload['user_id'])
#                 except User.DoesNotExist:
#                     return JsonResponse({'error': 'User not found'}, status=404)
 
#                 if allowed_roles and user.role not in allowed_roles:
#                     return JsonResponse({'error': 'Permission denied'}, status=403)
 
#                 request.user = user
#                 return view_func(request, *args, **kwargs)
 
#             # ======================
#             # 2️⃣ SESSION AUTH (Django Template)
#             # ======================
#             if request.user.is_authenticated:
#                 if allowed_roles and request.user.role not in allowed_roles:
#                     return HttpResponseForbidden("You are not authorized")
 
#                 return view_func(request, *args, **kwargs)
 
#             # ======================
#             # 3️⃣ NOT AUTHENTICATED
#             # ======================
#             if request.headers.get('Accept') == 'application/json':
#                 return JsonResponse({'error': 'Authentication required'}, status=401)
 
#             return redirect('/accounts/login/')
 
#         return wrapper
#     return decorator
 
 
 
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import redirect
from accounts.utils import decode_jwt
from accounts.models import User
 
 
def hybrid_auth_required(allowed_roles=None):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
 
            # ======================
            # 1️⃣ JWT AUTH (API)
            # ======================
            auth_header = request.headers.get('Authorization')
 
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                payload = decode_jwt(token)
 
                if not payload:
                    return JsonResponse({'error': 'Invalid or expired token'}, status=401)
 
                try:
                    user = User.objects.get(id=payload['user_id'])
                except User.DoesNotExist:
                    return JsonResponse({'error': 'User not found'}, status=404)
 
                # ✅ SUPERUSER / ADMIN → FULL ACCESS
                if user.is_superuser or user.is_staff:
                    request.user = user
                    return view_func(request, *args, **kwargs)
 
                # ❌ Normal user → role check
                if allowed_roles and user.role not in allowed_roles:
                    return JsonResponse({'error': 'Permission denied'}, status=403)
 
                request.user = user
                return view_func(request, *args, **kwargs)
 
            # ======================
            # 2️⃣ SESSION AUTH (Templates)
            # ======================
            if request.user.is_authenticated:
 
                # ✅ SUPERUSER / ADMIN → FULL ACCESS
                if request.user.is_superuser or request.user.is_staff:
                    return view_func(request, *args, **kwargs)
 
                # ❌ Normal user → role check
                if allowed_roles and request.user.role not in allowed_roles:
                    return HttpResponseForbidden("You are not authorized")
 
                return view_func(request, *args, **kwargs)
 
            # ======================
            # 3️⃣ NOT AUTHENTICATED
            # ======================
            if request.headers.get('Accept') == 'application/json':
                return JsonResponse({'error': 'Authentication required'}, status=401)
 
            return redirect('/accounts/login/')
 
        return wrapper
    return decorator
 
from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permission


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_f(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_f
    return decorator


def admin_required(f):
    return permission_required(Permission.ADMIN)(f)

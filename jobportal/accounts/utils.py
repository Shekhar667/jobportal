def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

def is_employer(user):
    return user.is_authenticated and user.role == 'employer'

def is_jobseeker(user):
    return user.is_authenticated and user.role == 'jobseeker'

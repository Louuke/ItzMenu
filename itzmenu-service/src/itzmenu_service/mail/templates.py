def user_verification_email(token: str, host: str):
    return (f'Thank you for using ItzMenu! '
            f'Please verify your email by clicking on the following link: '
            f"<a href='{host}/auth/verify?token={token}'>confirm email</a>")


def user_reset_password_email(token: str, host: str):
    return (f'You have requested to reset your password. '
            f'Please reset your password by clicking on the following link: '
            f"<a href='{host}/auth/reset-password?token={token}'>reset password</a>")

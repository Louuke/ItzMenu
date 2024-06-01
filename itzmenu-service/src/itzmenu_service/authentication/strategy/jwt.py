from fastapi_users.authentication import JWTStrategy
from fastapi_users.jwt import SecretType, generate_jwt, decode_jwt

from itzmenu_service.persistence.models import User


class JWTPermissionStrategy(JWTStrategy):

    def __init__(self, secret: SecretType | str, lifetime_seconds: int | None, token_audience: list[str] | None = None,
                 algorithm: str = 'HS256', public_key: SecretType | None = None):
        token_audience = token_audience if token_audience is not None else ['fastapi-users:auth']
        super().__init__(secret, lifetime_seconds, token_audience, algorithm, public_key)

    async def write_token(self, user: User) -> str:
        aud = self.token_audience + list(user.permissions) + (['*:*'] if user.is_superuser else [])
        data = {'sub': str(user.id), 'aud': aud}
        return generate_jwt(data, self.encode_key, self.lifetime_seconds, algorithm=self.algorithm)

    def get_permissions(self, token: str) -> list[str]:
        token = token.split(' ')[1] if ' ' in token else []
        data = decode_jwt(token, self.decode_key, self.token_audience, algorithms=[self.algorithm])
        return data.get('aud', [])

from datetime import datetime, timedelta
from typing import Annotated

from jose import jwt, JWTError

from sqlalchemy.orm import Session

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from conf.security import verify_password
from models.__all_models import Funcionario
from env_settings import settings

SECRET_KEY: str = settings('SECRET_KEY')
ALGORITHM: str = settings('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = 300

oauth2__bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

def user_authenticate(email:str, password, db: Session) -> Funcionario:
    user = (
        db.query(Funcionario)
        .filter(
            Funcionario.email == email
        )
        .first()
    )

    if not user or not verify_password(password, user.senha):
        return False
    return user

def create_access_token(username, cpf):
    encode = {'sub': username, 'id': cpf}
    expires = datetime.now() + timedelta(ACCESS_TOKEN_EXPIRE_MINUTES)
    encode.update({'exp': expires})

    return jwt.encode(encode, key=SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: Annotated[str, oauth2__bearer]):
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=ALGORITHM)
        username: str = payload.get('sub')
        user_id: str = payload.get('id')

        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Usuário Inválido')
        
        return {'email':username, 'cpf': user_id}
    
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Usuário Inválido') from exc
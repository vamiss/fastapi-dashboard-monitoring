from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Annotated
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext

SECRET_KEY = "09d25e094faa6ca2556c818166b7a3263b93f7099f6f0f4cff6cf63b88e8d3e7"
ALGORITHM = "HS256"

# We created hashed username and password for simplicity:
# In production, I will use a proper hashing algorithm like bcrypt, that we used here like an example :)

HASHED_USERNAME = '$2b$12$/bup8/Mv5/vRzFC9cX/9o..GILSBc0JrGjdUCRbC8XGvkgIOCOaPC'
HASHED_PASSWORD = '$2b$12$JbynJzFDa3tcmZtUU/.NYeKK6Nh7M.zH3683g308iNk9bh24CUh3y'

security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def authorize(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    if not (pwd_context.verify(credentials.username, HASHED_USERNAME) and pwd_context.verify(credentials.password, HASHED_PASSWORD)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

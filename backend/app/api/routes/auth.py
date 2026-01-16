from fastapi import APIRouter, HTTPException, status, Request
from app.schemas.auth import LoginRequest, Token
from app.core.users import authenticate_user
from app.core.security import create_access_token
from app.middleware.rate_limit import limiter

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
def login(request: Request, credentials: LoginRequest):
    """
    Login endpoint - returns JWT token
    
    Default credentials:
    - username: admin, password: password123
    - username: demo, password: password123
    """
    user = authenticate_user(credentials.username, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user["username"]})
    
    return Token(access_token=access_token)

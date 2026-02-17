from fastapi import APIRouter

router = APIRouter()

@router.post("/register")
def register_user():
    pass

@router.post("/login")
def login_user():
    pass

@router.post("/refresh")
def refresh_token():
    pass

@router.post("/logout")
def logout_user():
    pass


@router.get("/oauth/{provider}/login")
def oauth_login(provider: str):
    pass

@router.get("/oauth/{provider}/callback")
def oauth_callback(provider: str):
    pass
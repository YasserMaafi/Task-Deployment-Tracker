from app.core.jwt import create_access_token, decode_access_token

data = {"sub": "1"}  # user_id as string
token = create_access_token(data)
print("Token:", token)

decoded = decode_access_token(token)
print("Decoded:", decoded)
print("User ID:", decoded["sub"])

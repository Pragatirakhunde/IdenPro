from app.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)

password = "Pragati123"

hashed = hash_password(password)

print("Hash:")
print(hashed)

print("\nPassword Verification:")
print(verify_password(password, hashed))

token = create_access_token(
    {"sub": "pragati"}
)

print("\nJWT Token:")
print(token)

print("\nDecoded Payload:")
print(decode_access_token(token))
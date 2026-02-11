from app.core.security import hash_password, verify_password

plain = "supersecret"
hashed = hash_password(plain)

print("Plain:", plain)
print("Hashed:", hashed)
print("Verify:", verify_password("supersecret", hashed))  # Should be True
print("Verify wrong:", verify_password("wrongpass", hashed))  # Should be False

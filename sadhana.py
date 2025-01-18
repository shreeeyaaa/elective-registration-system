import bcrypt

def hash_password(password: str) -> str:
    # Generate a salt
    salt = bcrypt.gensalt()
    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Verify the password
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

if __name__ == "__main__":
    password = "Sadhana"
    # Hash the password
    hashed = hash_password(password)
    print(f"Hashed Password: {hashed}")

    # Verify the password
    is_valid = verify_password("Sadhana", hashed)
    print(f"Password is valid: {is_valid}")

import hashlib

# Function to verify the password using PBKDF2
def verify_password(password: str, stored_hash: str) -> bool:
    # One-liner to verify the password with PBKDF2
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), bytes.fromhex(stored_hash.split('|')[0]), 10000).hex() == stored_hash.split(':')[1]

# Main function for testing the condition
def main():
    # Known hash generated by the hashing function (format: salt:hash)
    stored_hash = input("Enter the known hash (format: salt:hash): ")

    # Input password to be tested
    password = input("Enter the password to verify: ")

    # Verifying the password
    if not verify_password(password, stored_hash):
        print("Password is invalid!")
    else:
        print("Password is valid!")

if __name__ == "__main__":
    main()
import jwt
import hashlib


# JWT

def decode_token(token, secret_key = "YOUR_SECRET"):

    algorithms_to_try = ["HS256", "HS384", "HS512", "RS256", "RS384", "RS512", "ES256", "ES384", "ES512"]

    decoded_token = None

    for algorithm in algorithms_to_try:
        try:
            decoded_token = jwt.decode(token, secret_key, algorithms=[algorithm])
            print(f"Decoded Token using {algorithm} algorithm:", decoded_token)
            break
        except jwt.ExpiredSignatureError:
            print("Token has expired")
            break
        except jwt.InvalidTokenError:
            print(f"Failed to decode token using {algorithm} algorithm")
            continue

    if decoded_token is None:
        print("Failed to decode token using all algorithms")



# MD5

def is_md5_hash(hash_string):
    if len(hash_string) == 32 and all(c in '0123456789abcdef' for c in hash_string):
        return True
    else:
        return False
    

def md5_hash(input_string):
    hash_object = hashlib.md5(input_string.encode())
    return hash_object.hexdigest()

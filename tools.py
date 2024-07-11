import hashlib
import os.path
import time
import uuid
import datetime
import jwt
import random
import string


def api_response(code, msg, data={}, total=0):
    return {
        'code': code,
        'total': total,
        'msg': msg,
        'data': data
    }


def generate_unique_string(length=32, prefix='', suffix=''):
    """
    Generate a unique string using UUID and timestamp.

    Args:
        length (int): The desired length of the unique string (default: 10).
        prefix (str): An optional prefix to add to the string.
        suffix (str): An optional suffix to add to the string.

    Returns:
        str: The generated unique string.
    """

    random_id = str(uuid.uuid4())[:length]
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    unique_string = f"{prefix}{random_id}{timestamp}{suffix}"

    return unique_string


def generate_unique_key(length=32, prefix='', suffix=''):
    """
    Generate a unique string using UUID and timestamp.

    Args:
        length (int): The desired length of the unique string (default: 10).
        prefix (str): An optional prefix to add to the string.
        suffix (str): An optional suffix to add to the string.

    Returns:
        str: The generated unique string.
    """

    random_id = str(uuid.uuid4())[:length]
    # timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    # unique_string = f"{prefix}{random_id}{timestamp}{suffix}"
    # unique_string = f"{prefix}{random_id}{suffix}"

    return random_id.replace('-', '').upper()


def generate_jwt(user_id, username, secret_key, algorithm="HS256"):
    payload = {
        'user_id': user_id,
        'username': username,
        'iat': datetime.datetime.utcnow().timestamp(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)
    }
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def md5(data):
    _md5 = hashlib.md5()
    _md5.update(data.encode('utf-8'))

    return _md5.hexdigest()


def generate_unique_order_number(length=20, prefix=""):
    """
    Generates a unique order number with a specified length and prefix.

    Args:
        length (int, optional): The desired length of the order number (default: 20).
        prefix (str, optional): A prefix to add to the order number (default: "").

    Returns:
        str: The unique order number.
    """

    # Get current timestamp as a string without decimals
    timestamp = str(int(time.time()))

    # Generate random suffix with enough digits to reach the desired length
    suffix_length = length - len(prefix) - len(timestamp)
    random_suffix = str(random.randint(10 ** (suffix_length - 1), 10 ** suffix_length - 1))

    # Combine prefix, timestamp, and random suffix to form the order number
    order_number = prefix + timestamp + random_suffix

    # Check if the generated order number already exists (TODO)
    # Implement logic to check for existing order numbers

    return order_number


def generate_query_string(data):
    # Sort the dictionary by keys in ascending order
    sorted_data = sorted(data.items(), key=lambda x: x[0])

    # Encode each key-value pair using urlencode
    encoded_params = [
        # urllib.parse.urlencode({key: value})
        f'{key}={value}'
        for key, value in sorted_data
    ]

    # Join the encoded pairs using '&' as the delimiter
    query_string = '&'.join(encoded_params)

    # # Remove the leading '&'
    # query_string = query_string[1:]

    return query_string


def get_pagination(current, page_size):
    current = int(current)
    page_size = int(page_size)

    start_index = (current - 1) * page_size
    end_index = start_index + page_size

    return start_index, end_index


def generate_unique_invitation_code(user_id, length=8):
    """Generates an 8-character unique invitation code based on a user ID.

    Args:
        user_id (int): The unique integer user ID.
        length (int, optional): The length of the invitation code. Defaults to 8.

    Returns:
        str: The generated unique invitation code.
    """

    chars = string.ascii_uppercase + string.digits
    random.seed(user_id)  # Seed the random number generator with user ID

    code = ''.join(random.choice(chars) for _ in range(length))
    return code


def generate_card_password(length=8):
    chars = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(chars) for _ in range(length))
    return random_string




if __name__ == '__main__':
    print(generate_card_password())

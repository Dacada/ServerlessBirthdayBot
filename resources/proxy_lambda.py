import os
import json
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

DISCORD_PUBLIC_KEY = os.environ["DISCORD_PUBLIC_KEY"]
INVALID_HEADERS_ERROR = {
    "isBase64Encoded": False,
    "statusCode": 401,
    "headers": {},
    "body": "invalid headers",
}
UNSUPPORTED_OPERATION_ERROR = {
    "isBase64Encoded": False,
    "statusCode": 400,
    "headers": {},
    "body": "unsupported operation",
}


def handle_ping(**kwargs):
    return 200, {"type": 1}


def handle_interaction(**kwargs):
    return 200, {"type": 4, "data": {"content": "Hello world!", "flags": 1 << 6}}


TYPE_MAP = [
    None,
    handle_ping,
    handle_interaction,
]


class UnroutableEvent(Exception):
    pass


def verify_request(headers, body):
    if headers is None or body is None:
        print("Invalid request: no headers or no body")
        return False

    signature = headers.get("x-signature-ed25519")
    timestamp = headers.get("x-signature-timestamp")
    if signature is None or timestamp is None:
        print("Invalid request: expected headers not found")
        return False

    verify_key = VerifyKey(bytes.fromhex(DISCORD_PUBLIC_KEY))

    try:
        verify_key.verify(f"{timestamp}{body}".encode(), bytes.fromhex(signature))
    except BadSignatureError:
        print("Invalid request: failed to verify signature")
        return False

    return True


def handler(event, context):
    try:
        print("event: " + json.dumps(event))
    except json.JSONDecodeError:
        print("event: INVALID JSON DATA, " + repr(event))

    headers = event.get("headers")
    path = event.get("path")
    http_method = event.get("httpMethod")
    parameters = event.get("body")

    print(f"headers: {headers}")
    print(f"path: {path}")
    print(f"http_method: {http_method}")
    print(f"parameters: {parameters}")

    if not verify_request(headers, parameters):
        return INVALID_HEADERS_ERROR

    if path != "/" or http_method != "POST" or parameters is None:
        print("Invalid path and http method")
        return UNSUPPORTED_OPERATION_ERROR
    parameters = json.loads(parameters)

    try:
        code, response = route_event(**parameters)
    except UnroutableEvent as e:
        print(f"Unroutable event: {e}")
        return UNSUPPORTED_OPERATION_ERROR

    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": {},
        "body": json.dumps(response),
    }


def route_event(type, **kwargs):
    err = 400, {"err": f"cannot handle interaction type {type}"}
    try:
        fun = TYPE_MAP[type]
        if fun is None:
            return err
        return fun(**kwargs)
    except IndexError:
        return err

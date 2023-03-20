import time


def request_wrapper(method, *args, **kwargs):
    print(
        f"doing a {method.__name__} request with parameters args={args} kwargs={kwargs}"
    )

    r = method(*args, **kwargs)
    print(f"status code = {r.status_code}")
    print(f"headers = {r.headers}")

    try:
        text = r.text
    except:
        text = None
    print(f"content = {text}")

    if r.status_code == 429:
        data = r.json()
        print(
            f"rate limit encountered: '{data['message']}', sleeping for {data['retry_after']} seconds and retrying"
        )
        time.sleep(data["retry_after"])
        request_wrapper(method, *args, **kwargs)
        return

    r.raise_for_status()

    remaining = int(r.headers["X-RateLimit-Remaining"])
    print(f"Rate limit remaining: {remaining}")
    if remaining == 0:
        reset_after = float(r.headers["X-RateLimit-Reset-After"])
        print(
            f"Remaining is zero. Sleeping for {reset_after} seconds before continuing"
        )
        time.sleep(reset_after)

    return r

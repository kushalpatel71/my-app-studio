"""Opt-in proxy identity for public limits; the default is the socket peer."""

from ipaddress import ip_address


def trusted_proxy_ips(value):
    """Only explicit IP addresses, never wildcard ranges or hostnames."""
    return frozenset(
        str(ip_address(item.strip())) for item in value.split(",") if item.strip()
    )


def client_identity(request, trusted):
    """Walk XFF from the trusted socket inward; ignore untrusted left prefixes.

    Enable only after verifying that the edge sanitizes/appends the actual peer.
    Unknown peers, malformed/duplicate headers or an all-trusted chain fall back
    to the socket bucket. Forwarded and X-Real-IP cannot override that choice.
    """
    peer = request.client.host if request.client else "unknown"
    try:
        peer = str(ip_address(peer))
    except ValueError:
        return peer
    if peer not in trusted:
        return peer
    headers = request.headers.getlist("x-forwarded-for")
    if len(headers) != 1 or len(headers[0]) > 2048:
        return peer
    try:
        chain = [str(ip_address(item.strip())) for item in headers[0].split(",")]
    except ValueError:
        return peer
    if len(chain) > 20:
        return peer
    return next(
        (candidate for candidate in reversed(chain) if candidate not in trusted), peer
    )

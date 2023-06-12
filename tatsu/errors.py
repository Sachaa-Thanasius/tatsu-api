"""
tatsu.errors
------------

Exceptions for the Tatsu API.
"""

__all__ = (
    "TatsuException",
    "HTTPException",
    "BadRequest",
    "Forbidden",
    "NotFound",
    "TatsuServerError",
)

from typing import Any

import aiohttp


class TatsuException(Exception):
    """Base exception class for Tatsu."""


class HTTPException(TatsuException):
    """Exception that's raised when a non-200 HTTP status code is returned.

    Parameters
    ----------
    response : :class:`aiohttp.ClientResponse`
        The HTTP response from the request.
    message : :class:`str` | dict[:class:`str`, Any], optional
        The decoded response data.

    Attributes
    ----------
    response : :class:`aiohttp.ClientResponse`
        The HTTP response from the request.
    status : :class:`int`
        The HTTP status of the response.
    code : :class:`int`
        The Tatsu-specific error code.
    text : :class:`str`
        The Tatsu-specific error text.
    """

    def __init__(self, response: aiohttp.ClientResponse, message: str | dict[str, Any] | None) -> None:
        self.response = response
        self.status: int = response.status
        self.code: int = message.get("code", 0) if isinstance(message, dict) else 0
        self.text: str = message.get("message", "") if isinstance(message, dict) else (message or "")

        fmt = "{0.status} {0.reason} (error code: {1})"
        if len(self.text):
            fmt += ": {2}"

        super().__init__(fmt.format(self.response, self.code, self.text))


class BadRequest(HTTPException):
    """Exception that's raised when status code 400 occurs.

    Subclass of :exc:`HTTPException`.
    """


class Forbidden(HTTPException):
    """Exception that's raised when status code 403 occurs.

    Subclass of :exc:`HTTPException`.
    """


class NotFound(HTTPException):
    """Exception that's raised when status code 404 occurs.

    Subclass of :exc:`HTTPException`.
    """


class TatsuServerError(HTTPException):
    """Exception that's raised when a 500 range status code occurs.

    Subclass of :exc:`HTTPException`.
    """

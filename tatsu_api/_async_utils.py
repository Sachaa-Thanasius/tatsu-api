#   Copyright 2020-present Michael Hall
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from __future__ import annotations

import asyncio
from collections import deque


__all__ = ("FIFOLockout",)


class FIFOLockout:
    """Lock out an async resource for an amount of time.

    Resources may be locked out multiple times.

    Only prevents new acquires and does not cancel ongoing scopes that
    have already acquired access.

    Guarantee FIFO acquisition.

    When paired with locks, semaphores, or ratelimiters, this should
    be the last synchonization acquired and should be acquired immediately.

    Example use could look similar to:

    >>> ratelimiter = Ratelimiter(5, 1, 1)
    >>> lockout = FIFOLockout()
    >>> async def request_handler(route, parameters):
            async with ratelimiter, lockout:
                response = await some_request(route, **parameters)
                if response.code == 429:
                    if reset_after := response.headers.get('X-Ratelimit-Reset-After')
                        lockout.lock_for(reset_after)
    """

    def __init__(self) -> None:
        self._lockouts: set[asyncio.Task[None]] = set()
        self._waiters: deque[asyncio.Future[None]] = deque()

    def __repr__(self) -> str:
        res = super().__repr__()
        extra = "unlocked" if not self._lockouts else f"locked, timestamps={self._lockouts:!r}"
        return f"<{res[1:-1]} [{extra}]>"

    def lock_for(self, seconds: float, /) -> None:
        """Lock a resource for an amount of time."""
        task = asyncio.create_task(asyncio.sleep(seconds, None))
        self._lockouts.add(task)
        task.add_done_callback(self._lockouts.discard)

    async def __aenter__(self) -> None:
        if not self._lockouts and all(f.cancelled() for f in self._waiters):
            return

        fut: asyncio.Future[None] = asyncio.get_running_loop().create_future()
        self._waiters.append(fut)

        while self._lockouts:
            await asyncio.gather(*self._lockouts)

        try:
            try:
                await fut
            finally:
                self._waiters.remove(fut)
        except asyncio.CancelledError:
            if not self._lockouts:
                maybe_f = next(iter(self._waiters), None)
                if maybe_f and not maybe_f.done():
                    maybe_f.set_result(None)

    async def __aexit__(self, *_dont_care: object) -> None:
        maybe_f = next(iter(self._waiters), None)
        if maybe_f and not maybe_f.done():
            maybe_f.set_result(None)

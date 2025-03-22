from typing import List

class Observer:

    def __init__(self):
        self._subscribers: List["Subscriber"] = []

    def attach(self, subscriber: "Subscriber"):
        self._subscribers.append(subscriber)

    def detach(self, subscriber: "Subscriber"):
        self._subscribers.remove(subscriber)
        
    async def invoke(self):
        """Invoke all subscribers."""
        for subscriber in self._subscribers:
            await subscriber.onInvoke()


class Subscriber:
    def __init__(self, update_callback):
        self._update_callback = update_callback

    async def onInvoke(self):
        await self._update_callback()
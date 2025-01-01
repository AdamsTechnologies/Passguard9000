from collections import defaultdict

class PubSub:
    """Simple pub-sub class"""
    def __init__(self):
        self.subscribers = defaultdict(list)

    def subscribe(self, topic:str, callback):
        """
        Register a callback function to be invoked whenever
        the given topic is published.
        """
        self.subscribers[topic].append(callback)

    def publish(self, topic:str, *args, **kwargs):
        """
        Notifies all subscribers about an event for the given topic.
        Additional positional or keyword arguments can be passed along
        if needed.
        """
        for cb in self.subscribers[topic]:
            cb(*args, **kwargs)
class SaveDirCache:
    _dir = None

    @classmethod
    def set(cls, path: str):
        """Store the save_dir path."""
        cls._dir = path

    @classmethod
    def get(cls) -> str:
        """Retrieve the last stored save_dir path (or None)."""
        return cls._dir
    

class OutputFileNameCache:
    _filename = None

    @classmethod
    def set(cls, filename):
        cls._filename = filename

    @classmethod
    def get(cls):
        return cls._filename
    

class ClusterfileDirCache:
    cluster_dir = None

    @classmethod
    def set(cls, path: str):
        """Store the save_dir path."""
        cls.cluster_dir = path

    @classmethod
    def get(cls) -> str:
        """Retrieve the last stored save_dir path (or None)."""
        return cls.cluster_dir


class inputfileDirCache:
    input_dir = None

    @classmethod
    def set(cls, path: str):
        """Store the save_dir path."""
        cls.input_dir = path

    @classmethod
    def get(cls) -> str:
        """Retrieve the last stored save_dir path (or None)."""
        return cls.input_dir

class ConsumerListCache:
    consumer_list = []

    @classmethod
    def set(cls, consumers):
        """Store list of unique consumer numbers."""
        cls.consumer_list = consumers

    @classmethod
    def get(cls):
        """Retrieve stored consumer list."""
        return cls.consumer_list

class TimeBlockRangeCache:
    """Cache the first and last time block numbers detected in the data."""
    _range = {"first": None, "last": None}

    @classmethod
    def set(cls, first, last):
        cls._range = {"first": first, "last": last}
        print(f"[CACHE] Time block range set: first={first}, last={last}")

    @classmethod
    def get(cls):
        return cls._range

class TimeBlockRangeCacheCompareLeft:
    """Cache the first and last time block numbers detected in the data."""
    _range = {"first": None, "last": None}

    @classmethod
    def set(cls, first, last):
        cls._range = {"first": first, "last": last}
        print(f"[CACHE] Time block range set: first={first}, last={last}")

    @classmethod
    def get(cls):
        return cls._range

class TimeBlockRangeCacheCompareRight:
    """Cache the first and last time block numbers detected in the data."""
    _range = {"first": None, "last": None}

    @classmethod
    def set(cls, first, last):
        cls._range = {"first": first, "last": last}
        print(f"[CACHE] Time block range set: first={first}, last={last}")

    @classmethod
    def get(cls):
        return cls._range


class ToUDynamicityCache:
    _data = None

    @classmethod
    def set(cls, value):
        cls._data = value

    @classmethod
    def get(cls):
        return cls._data


# Example cache.py snippet
class RepProfileCache:
    _data = None

    @classmethod
    def set(cls, df):
        cls._data = df

    @classmethod
    def get(cls):
        return cls._data

class model_param_Cache:
    param_dir = None

    @classmethod
    def set(cls, path: str):
        """Store the save_dir path."""
        cls.param_dir = path

    @classmethod
    def get(cls) -> str:
        """Retrieve the last stored save_dir path (or None)."""
        return cls.param_dir


# cache.py

class TouBinsCache:
    """Cache handler for storing and retrieving selected ToU bins (hour cutoffs)."""
    _data = None

    @classmethod
    def set(cls, tou_bins):
        """Store the selected ToU bin values."""
        if not isinstance(tou_bins, (list, tuple)):
            raise ValueError("ToU bins must be a list or tuple of integers.")
        cls._data = tou_bins
        print(f"[CACHE] Stored ToU bins: {tou_bins}")

    @classmethod
    def get(cls):
        """Retrieve the currently stored ToU bin values."""
        if cls._data is None:
            print("[CACHE] No ToU bins stored yet.")
        return cls._data

    @classmethod
    def clear(cls):
        """Clear the stored ToU bin values."""
        cls._data = None
        print("[CACHE] Cleared ToU bins cache.")



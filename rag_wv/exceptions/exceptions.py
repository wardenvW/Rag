class Error(Exception):
    """Base class for other exceptions"""
    pass

class InvalidValueError(Error):
    """TOP_N value cannot be greater than TOP_K"""
    pass
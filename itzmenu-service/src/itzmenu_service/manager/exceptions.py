class ItzMenuServiceException(Exception):
    pass


class WeekMenuNotExists(ItzMenuServiceException):
    pass


class WeekMenuAlreadyExists(ItzMenuServiceException):
    pass


class WeekMenuImageNotExists(ItzMenuServiceException):
    pass

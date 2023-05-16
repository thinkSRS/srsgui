##! 
##! Coptright(c) 2022, 2023 Stanford Research Systems, All right reserved
##! Subject to the MIT License
##! 

class InstException(Exception):
    """
    Package-wide base exception
    """
    pass


class InstCommunicationError(InstException):
    """communication exception"""
    pass


class InstLoginFailureError(InstException):
    """
    Exception for TCPIP login error
    """
    pass


class InstIdError(InstException):
    """
    Exception for invalid instrument ID
    """
    pass


class InstSetError(InstException):
    """Exception for errors during set operation"""
    pass


class InstQueryError(InstException):
    """Exception for errors during query operation"""
    pass


class InstIndexError(InstException):
    """Exception for error in index operation"""
    pass

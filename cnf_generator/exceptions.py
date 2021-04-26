# -*- coding: utf-8 -*-

"""Generator and classes related exception."""


class CNFGenException(Exception):
    """General exception of the module."""


class MalformedCNFException(CNFGenException):
    """The cnf contains some weird part."""


class SymbolNotAllowed(MalformedCNFException):
    """The symbol for the literal is not allowed."""


class GenerationFailedException(CNFGenException):
    """Generation of new cnf failed."""


class NoSymbolsOrderException(CNFGenException):
    """There is no suitable order for symbols."""


class LiteralNotPossibleToAddException(CNFGenException):
    """There is no suitable order for symbols."""

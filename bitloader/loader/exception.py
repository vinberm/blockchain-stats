
import logging

class Error(Exception):
    def __init__(self, message=None):
        super(Error, self).__init__(message)

class InvalidBlock(Error):
    pass

class MerkleRootMismatch(InvalidBlock):
    def __init__(ex, block_hash, tx_hashes):
        ex.block_hash = block_hash
        ex.tx_hashes = tx_hashes
    def __str__(ex):
        return 'Block header Merkle root does not match its transactions. ' \
            'block hash=%s' % (ex.block_hash[::-1].encode('hex'),)


class NotFound(Error):
    pass

class LoadError(Error):
    pass

class Duplicate(Error):
    pass

class NotAuthorized(Error):
    pass

class NotEmpty(Error):
    pass

class Invalid(Error):
    pass

class InvalidInputException(Error):
    pass


class TimeoutException(Error):
    pass

class ExecuteError(Error):
    pass


class DBException(Error):
    """Wraps an implementation specific exception"""
    def __init__(ex, inner_exception):
        ex.inner_exception = inner_exception
        super(DBError, self).__init__(str(inner_exception))
        
    def __str__(ex):
        return 'DB handle  Error: %' (ex.inner_exception)

"""Custom exceptions and error handling utilities"""

class PaperSearchException(Exception):
    """Base exception for paper-search application"""
    pass

class PaperNotFoundException(PaperSearchException):
    """Raised when a paper is not found"""
    pass

class ScraperException(PaperSearchException):
    """Raised when scraping fails"""
    pass

class MCPException(PaperSearchException):
    """Raised when MCP server call fails"""
    pass

class ValidationException(PaperSearchException):
    """Raised when validation fails"""
    pass

class DatabaseException(PaperSearchException):
    """Raised when database operation fails"""
    pass

def handle_error(error: Exception) -> dict:
    """Standardize error response format"""
    return {
        "status": "error",
        "error_type": type(error).__name__,
        "message": str(error)
    }

def handle_success(data: any, message: str = None) -> dict:
    """Standardize success response format"""
    response = {
        "status": "success",
        "data": data
    }
    if message:
        response["message"] = message
    return response

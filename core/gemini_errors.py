class GeminiBaseError(Exception):
    """Base exception for Gemini service layer."""
    pass

class InvalidAPIKeyError(GeminiBaseError):
    """Raised when provided API Key is invalid or unauthorized."""
    pass

class QuotaExhaustedError(GeminiBaseError):
    """Raised when all API keys hit rate limits / daily quota (429)."""
    pass

class ModelSelectionError(GeminiBaseError):
    """Raised when no compatible generateContent model is found."""
    pass

class ServiceUnavailableError(GeminiBaseError):
    """Raised when Google API services fail repeatedly (5xx/Timeout)."""
    pass
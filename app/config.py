import os
from typing import Optional

class Settings:
    """Application configuration settings"""
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./paper_search.db")
    
    # API URLs
    ARXIV_API_BASE: str = os.getenv("ARXIV_API_BASE", "https://export.arxiv.org/api/query")
    BIORXIV_API_BASE: str = os.getenv("BIORXIV_API_BASE", "https://api.biorxiv.org/details/biorxiv")
    PUBMED_API_BASE: str = os.getenv("PUBMED_API_BASE", "https://eutils.ncbi.nlm.nih.gov/entrez/eutils")
    
    # API Keys
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    
    # Rate Limiting
    RATE_LIMIT_DELAY: float = 0.34  # seconds (3 requests per second)
    PUBMED_RATE_LIMIT: float = 0.34
    BIORXIV_RATE_LIMIT: float = 0.5
    
    # Defaults
    DEFAULT_MAX_RESULTS: int = 10
    DEFAULT_DAYS_BACK: int = 7
    DEFAULT_LIMIT: int = 20
    
    # Email Configuration
    EMAIL_HOST: str = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT: int = int(os.getenv("EMAIL_PORT", "587"))
    EMAIL_USER: Optional[str] = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD: Optional[str] = os.getenv("EMAIL_PASSWORD")
    
    # Processing
    MIN_ABSTRACT_LENGTH: int = 50  # Minimum length to use abstract as summary
    
    # Scheduler
    SCRAPE_SCHEDULE_HOUR: int = 6  # 6:00 AM
    PROCESS_INTERVAL_HOURS: int = 2
    REPORT_SCHEDULE_HOUR: int = 9  # 9:00 AM
    
    # MCP Servers
    MCP_SERVERS_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mcp_servers")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required settings"""
        if not cls.GOOGLE_API_KEY:
            print("Warning: GOOGLE_API_KEY not set. AI features will not work.")
            return False
        return True

settings = Settings()

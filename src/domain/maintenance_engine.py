from datetime import datetime, timedelta
from typing import Optional
from src.config import settings

class MaintenanceEngine:
    """
    Valida si la fecha de la última versión está dentro de los últimos dos años.
    """
    @staticmethod
    def is_maintained(published_at: Optional[str]) -> bool:
        if not published_at:
            return False
        try:
            date = datetime.strptime(published_at[:10], "%Y-%m-%d")
        except Exception:
            return False
        cutoff = datetime.now() - timedelta(days=365 * settings.maintenance_window_years)
        return date >= cutoff

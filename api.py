import httpx
from typing import Dict, Any

# Global variables to store session state
BASE_URL = "http://localhost:8000"
global_access_token: str | None = None
global_default_tenant_id: str | None = None
global_user_data: Dict[str, Any] | None = None

# Global theme colors and properties
global_primary_color: list[float] = [0.2, 0.6, 0.8, 1] # Default blue
global_secondary_color: list[float] = [0.9, 0.9, 0.9, 1] # Default light gray
global_accent_color: list[float] = [0.1, 0.7, 0.5, 1]
global_background_color: list[float] = [0.95, 0.95, 0.95, 1]
global_text_color: list[float] = [0.1, 0.1, 0.1, 1]
global_success_color: list[float] = [0.2, 0.8, 0.2, 1]
global_warning_color: list[float] = [1.0, 0.6, 0.0, 1]
global_error_color: list[float] = [0.8, 0.2, 0.2, 1]
global_border_radius: int = 8
global_font_size: int = 14
global_icon_style: str = "material"

async def login_user(username, password) -> Dict[str, Any]:
    """Logs in the user and returns token data."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/auth/token",
            data={"username": username, "password": password}
        )
        response.raise_for_status()
        return response.json()
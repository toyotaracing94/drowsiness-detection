from typing import Any, Optional

from pydantic import BaseModel


class StandardResponse(BaseModel):
    status: str = "ok"
    message: Optional[str] = None
    data: Optional[Any] = None
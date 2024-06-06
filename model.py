from pydantic import BaseModel, Field


class SecServerConfig(BaseModel):
    base_server_path: str = Field(..., min_length=1)
    base_local_path: str = Field(..., min_length=1)
    link_base_path: str = Field(..., min_length=1)

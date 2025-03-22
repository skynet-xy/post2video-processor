from pydantic import BaseModel

class GetOutputVideoRequest(BaseModel):
    job_code: str
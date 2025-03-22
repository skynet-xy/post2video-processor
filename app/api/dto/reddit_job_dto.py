from pydantic import BaseModel, Field

class GetOutputVideoRequest(BaseModel):
    job_code: str = Field(
        default='1234',
        description="Code of the job to get the output video path for"
    )
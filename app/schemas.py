from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(min_length=2, max_length=4000)
    use_knowledge_base: bool = True


class Source(BaseModel):
    source: str
    score: float
    excerpt: str


class AskResponse(BaseModel):
    answer: str
    model: str
    local_inference: bool = True
    sources: list[Source]
    usage: dict = {}

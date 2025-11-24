from pydantic import BaseModel, Field


class AddInput(BaseModel):
    a: int
    b: int


class AddOutput(BaseModel):
    result: int


class FilePathInput(BaseModel):
    file_path: str


class MarkdownOutput(BaseModel):
    markdown: str

class SearchInput(BaseModel):
    query: str
    max_results: int = Field(default=10, description="Maximum number of results to return")

class PythonCodeOutput(BaseModel):
    result: str

class UrlInput(BaseModel):
    url: str

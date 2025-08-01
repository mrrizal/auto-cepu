from pydantic import BaseModel
from typing import List


class FunctionLocation(BaseModel):
    start_line: int
    end_line: int


class CodeBlock(BaseModel):
    start_line: int
    end_line: int
    code: str
    line_count: int


class Summary(BaseModel):
    total_added_lines: int
    total_deleted_lines: int
    added_line_numbers: List[int]
    deleted_line_numbers: List[int]


class FunctionAnalysis(BaseModel):
    function_name: str
    function_location: FunctionLocation
    full_function_code: str
    added_code: List[CodeBlock]
    deleted_code: List[CodeBlock]
    summary: Summary


class CodeReviewRequest(BaseModel):
    file_path: str
    project_name: str
    file_path: str
    function_name: str
    function_location: FunctionLocation
    full_function_code: str
    added_code: List[CodeBlock]
    deleted_code: List[CodeBlock]
    summary: Summary


class CodeReviewResponse(BaseModel):
    duplication_review: str
    style_review: str
    summary: str
    reference: list

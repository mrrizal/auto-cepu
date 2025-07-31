import logging
import asyncio
from typing import List, Dict
from llm.prompt import PromptGenerator
from llm.code_reviewer import CodeReviewLLM
from ingestion import ChromaDBIndexingService
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi import Depends
from ingestion.normalizer import normalize_code

# Configure the root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)


app = FastAPI()

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


def get_indexing_service(project_name: str = "code_repository"):
    return ChromaDBIndexingService(collection_name=project_name)


def get_prompt_generator():
    return PromptGenerator()


def get_code_reviewer():
    return CodeReviewLLM()


@app.post("/code-review", response_model=CodeReviewResponse)
async def review_code(
    request: CodeReviewRequest,
    prompt_generator: PromptGenerator = Depends(get_prompt_generator),
    code_reviewer: CodeReviewLLM = Depends(get_code_reviewer)
):
    # code = request.code
    # project_name = request.project_name

    # indexing_service = get_indexing_service(project_name)

    # if not code.strip():
    #     raise HTTPException(status_code=400, detail="Code snippet cannot be empty.")

    # try:
    #     normalized_code = normalize_code(code)
    #     similar_code = indexing_service.query_similar_code(normalized_code)
    # except SyntaxError:
    #     similar_code = []

    logger.info("Generating review prompt for the provided code snippet.")
    review_prompt = prompt_generator.generate_coding_style_prompt_with_diff(
        added_code=request.added_code,
        deleted_code=request.deleted_code,
        full_function_code=request.full_function_code,
    )
    print("Review Prompt Generated:")
    print(review_prompt)

    # if not similar_code:
    #     logger.info("No similar code snippets found.")
    #     style_result = await code_reviewer.review(review_prompt)
    #     duplication_result = None
    # else:
    #     logger.debug(f"Found {len(similar_code)} similar code snippets.")
    #     duplicate_code_check_prompt = prompt_generator.\
    #         generate_code_duplication_check_prompt(code, similar_code)

    #     duplication_result, style_result = await asyncio.gather(
    #         code_reviewer.review(duplicate_code_check_prompt),
    #         code_reviewer.review(review_prompt)
    #     )

    # if not duplication_result:
    #     summary = style_result
    # else:
    #     summary = await code_reviewer.review(
    #         prompt_generator.generate_summary_prompt(
    #             style_result['response'], duplication_result['response']
    #         )
    #     )

    duplication_result = None
    style_result = None
    summary = None
    similar_code = []

    return CodeReviewResponse(
        duplication_review=duplication_result['response'] if duplication_result else "No duplication found.",
        style_review=style_result['response'] if style_result else "No style issues found.",
        summary=summary['response'] if summary else "No summary available.",
        reference=similar_code if similar_code else []
    )

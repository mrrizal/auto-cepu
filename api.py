import logging
import asyncio
from typing import List, Dict
from llm.prompt import CodeReviewPromptGenerator
from llm.code_reviewer import CodeReviewLLM
from ingestion import ChromaDBIndexingService
from fastapi import FastAPI, HTTPException
from fastapi import Depends
from ingestion.normalizer import normalize_code
from llm.models import (
    CodeReviewRequest,
    CodeReviewResponse
)

# Configure the root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)


app = FastAPI()


def get_indexing_service(project_name: str = "code_repository"):
    return ChromaDBIndexingService(collection_name=project_name)


def get_prompt_generator():
    return CodeReviewPromptGenerator()


def get_code_reviewer():
    return CodeReviewLLM()


@app.post("/code-review", response_model=CodeReviewResponse)
async def review_code(
    request: CodeReviewRequest,
    prompt_generator: CodeReviewPromptGenerator = Depends(get_prompt_generator),
    code_reviewer: CodeReviewLLM = Depends(get_code_reviewer)
):
    code = request.full_function_code
    project_name = request.project_name

    indexing_service = get_indexing_service(project_name)

    if not code.strip():
        raise HTTPException(status_code=400, detail="Code snippet cannot be empty.")

    duplication_result = {"response": "No duplication found."}
    style_result = {"response": "No style issues found."}
    summary = {"response": "No summary available"}
    similar_codes = []

    try:
        normalized_code = normalize_code(code)
        similar_codes = indexing_service.query_similar_code(normalized_code)
    except SyntaxError:
        similar_codes = []

    added_code = [code for code in request.added_code if code.code.strip()]
    deleted_code = [code for code in request.deleted_code if code.code.strip()]

    review_prompt = prompt_generator.generate_style_review_prompt(
        added_code=added_code,
        deleted_code=deleted_code,
        full_function_code=request.full_function_code,
        function_name=request.function_name
    )

    if not similar_codes or len(added_code) == 0:
        logger.info("No similar code snippets found.")
        style_result = await code_reviewer.review(review_prompt)
        similar_codes = []
    else:
        logger.debug(f"Found {len(similar_codes)} similar code snippets.")
        duplicate_code_check_prompt = prompt_generator.generate_duplication_check_prompt(
            code_snippet=code,
            similar_codes=similar_codes,
            function_name=request.function_name
        )

        style_result, duplication_result = await asyncio.gather(
            code_reviewer.review(review_prompt),
            code_reviewer.review(duplicate_code_check_prompt)
        )

    summary = await code_reviewer.review(
        prompt_generator.generate_summary_prompt(
            style_result['response'], duplication_result['response']
        )
    )

    return CodeReviewResponse(
        duplication_review=duplication_result['response'] if duplication_result else "No duplication found.",
        style_review=style_result['response'] if style_result else "No style issues found.",
        summary=summary['response'] if summary else "No summary available.",
        reference=similar_codes if similar_codes else []
    )

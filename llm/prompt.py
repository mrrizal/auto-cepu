from typing import List, Dict, Any, Optional
from llm.models import CodeBlock


class CodeReviewPromptGenerator:
    def __init__(self):
        pass

    def _clean_code(self, code: str) -> str:
        """Clean code while preserving indentation."""
        if not code:
            return code

        lines = code.strip().splitlines()
        if not lines:
            return ""

        # Remove common leading whitespace
        non_empty_lines = [line for line in lines if line.strip()]
        if not non_empty_lines:
            return ""

        min_indent = min(len(line) - len(line.lstrip()) for line in non_empty_lines)

        cleaned_lines = []
        for line in lines:
            if line.strip():
                cleaned_lines.append(line[min_indent:])
            else:
                cleaned_lines.append("")

        return '\n'.join(cleaned_lines)

    def generate_style_review_prompt(
        self,
        added_code: List[Dict[str, Any]],
        deleted_code: List[Dict[str, Any]],
        full_function_code: str = "",
        function_name: str = ""
    ) -> str:
        """Generate a concise code review prompt with strict format enforcement."""

        # Format added code
        added_blocks = []
        for i, chunk in enumerate(added_code, 1):
            if isinstance(chunk, CodeBlock):
                code = chunk.code
            else:
                code = chunk.get('code', '')

            clean_code = self._clean_code(code)
            if clean_code:
                # Limit code length to prevent overwhelming the model
                if len(clean_code) > 300:
                    clean_code = clean_code[:300] + "\n... [truncated]"
                added_blocks.append(f"```python\n{clean_code}\n```")

        # Format deleted code
        deleted_blocks = []
        for i, chunk in enumerate(deleted_code, 1):
            if isinstance(chunk, CodeBlock):
                code = chunk.code
            else:
                code = chunk.get('code', '')

            clean_code = self._clean_code(code)
            if clean_code:
                if len(clean_code) > 300:
                    clean_code = clean_code[:300] + "\n... [truncated]"
                deleted_blocks.append(f"```python\n{clean_code}\n```")

        # Format full function (limit size)
        full_code_section = ""
        if full_function_code:
            clean_full = self._clean_code(full_function_code)
            if len(clean_full) > 500:
                clean_full = clean_full[:500] + "\n... [truncated]"
            full_code_section = f"Full function `{function_name}`:\n```python\n{clean_full}\n```\n"

        # Build the prompt with very clear instructions
        changes_section = ""
        if added_blocks:
            changes_section += f"ADDED:\n{chr(10).join(added_blocks)}\n"
        if deleted_blocks:
            changes_section += f"REMOVED:\n{chr(10).join(deleted_blocks)}\n"

        if not changes_section:
            changes_section = "No code changes detected.\n"

        prompt = f"""You are a code reviewer. Analyze this Python code change and respond EXACTLY in the format below.

{full_code_section}{changes_section}

You MUST respond in this EXACT format (copy the headers exactly):

SUMMARY: [One sentence describing what changed]

ISSUES: [List specific bugs/problems, or write "None found"]

IMPROVEMENTS: [Suggest specific improvements, or write "None needed"]

DECISION: [Yes/No] - [One sentence reason]

Do not add extra text or explanations outside this format."""

        return prompt.strip()

    def generate_duplication_check_prompt(
        self,
        code_snippet: str,
        similar_codes: List[Dict[str, Any]],
        function_name: str = ""
    ) -> str:
        """Generate a focused duplication check prompt."""

        if not code_snippet.strip() or not similar_codes:
            return ""

        clean_snippet = self._clean_code(code_snippet)
        if len(clean_snippet) > 400:
            clean_snippet = clean_snippet[:400] + "\n... [truncated]"

        # Only use the most similar code to avoid confusion
        most_similar = similar_codes[0]
        file_path = most_similar.get('file_path', 'unknown_file')
        similar_code = most_similar.get('code', '')
        similarity_score = most_similar.get('similarity_score', 'N/A')

        clean_similar = self._clean_code(similar_code)
        if len(clean_similar) > 400:
            clean_similar = clean_similar[:400] + "\n... [truncated]"

        prompt = f"""Check for code duplication. Respond EXACTLY in the format below.

Current code from `{function_name}`:
```python
{clean_snippet}
```

Similar code from `{file_path}` ({similarity_score}% similar):
```python
{clean_similar}
```

You MUST respond in this EXACT format:

DUPLICATION LEVEL: [None/Low/Medium/High]

ANALYSIS: [Are these actual duplicates? One sentence.]

RECOMMENDATION: [What action to take? One sentence.]

Do not add extra text."""

        return prompt.strip()

    def generate_summary_prompt(
        self,
        style_result: str,
        duplication_result: str,
        function_name: str = ""
    ) -> str:
        """Generate a very focused summary prompt."""

        # Extract key info from previous results
        def extract_decision(result: str) -> str:
            if not result or "sorry" in result.lower():
                return "No review completed"

            lines = result.split('\n')
            for line in lines:
                if 'DECISION:' in line.upper():
                    return line.strip()
                elif 'ISSUES:' in line.upper():
                    if 'none found' in line.lower():
                        return "No issues found"
            return result[:100] + "..." if len(result) > 100 else result

        def extract_duplication(result: str) -> str:
            if not result or "sorry" in result.lower():
                return "No duplication check"

            lines = result.split('\n')
            for line in lines:
                if 'DUPLICATION LEVEL:' in line.upper():
                    return line.strip()
            return "No duplicates found"

        style_summary = extract_decision(style_result)
        dup_summary = extract_duplication(duplication_result)

        prompt = f"""Create a final code review summary. Respond EXACTLY in this format.

Style Review: {style_summary}
Duplication Check: {dup_summary}

You MUST respond in this EXACT format:

ISSUES FOUND: [List main problems, or write "None"]

PRIORITY: [High/Medium/Low]

RECOMMENDATION: [Approve/Request Changes/Needs Discussion]

REASON: [One sentence explanation]

Do not add extra text. Keep under 100 words total."""

        return prompt.strip()

    def generate_contextual_review_prompt(self, payload_data: Dict[str, Any]) -> str:
        """Generate a comprehensive but concise review prompt."""

        added_code = payload_data.get('added_code', [])
        deleted_code = payload_data.get('deleted_code', [])
        full_function_code = payload_data.get('full_function_code', '')
        function_name = payload_data.get('function_name', '')

        return self.generate_style_review_prompt(
            added_code=added_code,
            deleted_code=deleted_code,
            full_function_code=full_function_code,
            function_name=function_name
        )


# Even more minimal version for better model compliance
class MinimalCodeReviewPrompts:
    def __init__(self):
        pass

    def _clean_code(self, code: str) -> str:
        """Basic code cleaning."""
        return code.strip()[:400] if code else ""  # Limit length

    def generate_review_prompt(
        self,
        added_code: List[Dict[str, Any]],
        deleted_code: List[Dict[str, Any]],
        function_name: str = ""
    ) -> str:
        """Ultra-focused review prompt."""

        # Get the main code blocks
        added_text = ""
        if added_code:
            first_added = added_code[0]
            if isinstance(first_added, CodeBlock):
                added_text = first_added.code
            else:
                added_text = first_added.get('code', '')

        deleted_text = ""
        if deleted_code:
            first_deleted = deleted_code[0]
            if isinstance(first_deleted, CodeBlock):
                deleted_text = first_deleted.code
            else:
                deleted_text = first_deleted.get('code', '')

        prompt = f"""Code review for function `{function_name}`. Answer in EXACT format below.

"""

        if added_text:
            prompt += f"NEW CODE:\n```python\n{self._clean_code(added_text)}\n```\n"

        if deleted_text:
            prompt += f"REMOVED CODE:\n```python\n{self._clean_code(deleted_text)}\n```\n"

        prompt += """
Format your response EXACTLY like this:

ISSUES: [List problems or "None"]
APPROVE: [Yes/No]
REASON: [One sentence]

No other text allowed."""

        return prompt

    def generate_duplication_prompt(
        self,
        code_snippet: str,
        similar_codes: List[Dict[str, Any]]
    ) -> str:
        """Ultra-simple duplication check."""

        if not similar_codes:
            return "No similar code found.\n\nDUPLICATE: No\nACTION: None needed"

        similar_code = similar_codes[0].get('code', '') if similar_codes else ''

        return f"""Compare these code blocks:

CODE A:
```python
{self._clean_code(code_snippet)}
```

CODE B:
```python
{self._clean_code(similar_code)}
```

Response format:
DUPLICATE: [Yes/No]
ACTION: [Combine/Keep separate/Review needed]"""

    def generate_summary_prompt(self, style_result: str, duplication_result: str) -> str:
        """Ultra-simple summary."""

        return f"""Final decision based on:

Style: {style_result[:100]}
Duplication: {duplication_result[:100]}

FINAL DECISION: [APPROVE/REJECT]
MAIN REASON: [One sentence]

No additional text."""


# Factory function to choose the right prompt generator
def get_prompt_generator(model_name: str = ""):
    """Select appropriate prompt generator based on model."""
    if "deepseek" in model_name.lower() or "coder" in model_name.lower():
        return MinimalCodeReviewPrompts()
    else:
        return CodeReviewPromptGenerator()
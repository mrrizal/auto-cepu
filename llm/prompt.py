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
        """Generate a concise code review prompt."""

        # Format added code
        added_blocks = []
        for i, chunk in enumerate(added_code, 1):
            if isinstance(chunk, CodeBlock):
                code = chunk.code
            else:
                code = chunk.get('code', '')

            clean_code = self._clean_code(code)
            if clean_code:
                added_blocks.append(f"Added block {i}:\n```python\n{clean_code}\n```")

        # Format deleted code
        deleted_blocks = []
        for i, chunk in enumerate(deleted_code, 1):
            if isinstance(chunk, CodeBlock):
                code = chunk.code
            else:
                code = chunk.get('code', '')

            clean_code = self._clean_code(code)
            if clean_code:
                deleted_blocks.append(f"Deleted block {i}:\n```python\n{clean_code}\n```")

        # Format full function
        full_code_section = ""
        if full_function_code:
            clean_full = self._clean_code(full_function_code)
            full_code_section = f"\nFull function:\n```python\n{clean_full}\n```"

        # Build the prompt
        prompt = f"""Review this Python code change for function `{function_name}`:

{full_code_section}

Changes made:
{chr(10).join(added_blocks) if added_blocks else "No code added."}

{chr(10).join(deleted_blocks) if deleted_blocks else "No code deleted."}

Please respond in this format:

SUMMARY: [What this change does in 1-2 sentences]

ISSUES: [List any bugs, problems, or concerns. Write "None found" if no issues]

IMPROVEMENTS: [Suggest code quality improvements. Write "None needed" if code is good]

DECISION: [Yes/No] - [Brief reason why]

Keep each section concise and actionable."""

        return prompt.strip()

    def generate_duplication_check_prompt(
        self,
        code_snippet: str,
        similar_codes: List[Dict[str, Any]],
        function_name: str = ""
    ) -> str:
        """Generate a simple duplication check prompt."""

        if not code_snippet.strip() or not similar_codes:
            return ""

        clean_snippet = self._clean_code(code_snippet)

        # Format similar code
        similar_sections = []
        for i, similar in enumerate(similar_codes[:3], 1):  # Limit to 3 examples
            file_path = similar.get('file_path', f'file_{i}')
            code = similar.get('code', '')
            similarity = similar.get('similarity_score', 'N/A')

            clean_similar = self._clean_code(code)
            if len(clean_similar) > 500:  # Truncate long code
                clean_similar = clean_similar[:500] + "\n... [truncated]"

            similar_sections.append(f"Similar code {i} (from {file_path}, {similarity}% similar):\n```python\n{clean_similar}\n```")

        prompt = f"""Check if this code is duplicated in the codebase:

Current code from `{function_name}`:
```python
{clean_snippet}
```

Found similar code:
{chr(10).join(similar_sections)}

Respond in this format:

DUPLICATION LEVEL: [None/Low/Medium/High]

ANALYSIS: [Are these actual duplicates or just similar patterns?]

RECOMMENDATION: [Should code be consolidated? What action to take?]

Keep it brief and actionable."""

        return prompt.strip()

    def generate_summary_prompt(
        self,
        style_result: str,
        duplication_result: str,
        function_name: str = ""
    ) -> str:
        """Generate a concise summary prompt."""

        # Clean up the results if they're too verbose
        def clean_result(result: str) -> str:
            if not result or "I'm sorry" in result or "I don't have capabilities" in result:
                return "No issues found."
            return result.strip()

        cleaned_style = clean_result(style_result)
        cleaned_duplication = clean_result(duplication_result)

        return f"""Code review summary:

Style Review Results:
{cleaned_style}

Duplication Check Results:
{cleaned_duplication}

Final Summary for `{function_name}`:

1. ISSUES FOUND:
   - [List main problems if any, or "None"]

2. PRIORITY: [High/Medium/Low]

3. RECOMMENDATION: [Approve/Request Changes/Needs Discussion]

4. REASON: [Brief 1-2 sentence explanation]

Keep response under 200 words."""

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


# Alternative: Even simpler prompts for better model performance
class MinimalCodeReviewPrompts:
    def __init__(self):
        pass

    def _clean_code(self, code: str) -> str:
        """Basic code cleaning."""
        return code.strip() if code else ""

    def generate_review_prompt(
        self,
        added_code: List[Dict[str, Any]],
        deleted_code: List[Dict[str, Any]],
        function_name: str = ""
    ) -> str:
        """Ultra-simple review prompt."""

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

        prompt_parts = [f"Review this code change in function {function_name}:"]

        if added_text:
            prompt_parts.append(f"\nNew code:\n```python\n{self._clean_code(added_text)}\n```")

        if deleted_text:
            prompt_parts.append(f"\nRemoved code:\n```python\n{self._clean_code(deleted_text)}\n```")

        prompt_parts.append("\nWhat issues do you see? Should this be merged?")

        return "\n".join(prompt_parts)

    def generate_duplication_prompt(
        self,
        code_snippet: str,
        similar_codes: List[Dict[str, Any]]
    ) -> str:
        """Ultra-simple duplication check."""

        if not similar_codes:
            return ""

        similar_code = similar_codes[0].get('code', '') if similar_codes else ''

        return f"""Is this code duplicated?

Code A:
```python
{self._clean_code(code_snippet)}
```

Code B:
```python
{self._clean_code(similar_code)}
```

Are they duplicates? Should they be combined?"""

    def generate_summary_prompt(self, style_result: str, duplication_result: str) -> str:
        """Ultra-simple summary."""

        if not style_result.strip():
            style_result = "No issues found"
        if not duplication_result.strip():
            duplication_result = "No duplicates found"

        return f"""QUICK REVIEW SUMMARY:

Quality Issues: {style_result}

Duplication: {duplication_result}

DECISION: Should this code change be approved? Give a simple Yes/No with one sentence reason."""

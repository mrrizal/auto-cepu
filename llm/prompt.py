import textwrap


class PromptGenerator:
    def __init__(self):
        self.base_header = "You are an expert Python code reviewer. Analyze the following code for quality issues and improvements."

    def generate_coding_style_prompt_with_diff(
        self,
        added_code: list,
        deleted_code: list,
        full_function_code: str = ""
    ) -> str:
        """
        Generate a prompt to review code changes using added and deleted code context.
        """
        added_code_str = "\n".join(chunk.code for chunk in added_code).strip()
        deleted_code_str = "\n".join(chunk.code for chunk in deleted_code).strip()

        full_code_block = f"```python\n{full_function_code.strip()}\n```" if full_function_code else "N/A"

        header = (
            "You are an expert Python code reviewer analyzing a code change (diff) in a pull request. "
            "Your task is to evaluate the added and deleted code in context, checking for behavior changes, regressions, and quality improvements."
        )
        prompt = f"""## Instruction
{header}

- Whether the **added code improves or regresses** the logic of the deleted code
- Whether the **intent of the deleted code is preserved or broken**
- The **quality** of the new code (style, naming, structure, readability)
- Whether any logic or behavior was **accidentally removed or degraded**
- Opportunities to **simplify, refactor, or improve** the new implementation
- Any introduced **security, performance, or error-handling concerns**


## Full Function Context
{full_code_block}


## 🔼 Added Code
```python
{added_code_str}
```

## 🔽 Deleted Code
```python
{deleted_code_str}
```

## Analysis Areas
1. **Naming & Style**: Variable/function names, PEP 8 compliance
2. **Code Structure**: DRY principles, complexity, readability
3. **Design Patterns**: Appropriate pattern usage or missed opportunities
4. **SOLID Principles**: SRP, OCP, LSP, ISP, DIP violations
5. **Performance**: Potential bottlenecks or inefficiencies
6. **Error Handling**: Exception handling and edge cases
7. **Security**: Potential security vulnerabilities

## Expected Output Format
Use the following GitHub markdown format for your response:

### 🐛 Issues Found
- **[Category]** - [Specific issue with line reference if applicable]
- **[Category]** - [Specific issue with line reference if applicable]

### 💡 Recommendations
- [Specific actionable improvement]
- [Refactoring suggestion with brief example if needed]

### 📊 Severity Assessment
| Severity | Count | Description |
|----------|-------|-------------|
| 🔴 Critical | [Count] | Security vulnerabilities, logic errors |
| 🟡 Major | [Count] | SOLID violations, performance issues |
| 🟢 Minor | [Count] | Style improvements, naming conventions |

### 🎯 Overall Rating
**Rating:** `[POOR/NEEDS_IMPROVEMENT/ACCEPTABLE/GOOD/EXCELLENT]`

## Guidelines
- Be specific about line numbers when possible
- Provide actionable suggestions, not just criticism
- Focus on the most impactful improvements first
- Consider maintainability and readability
- Keep feedback concise but thorough
- Use GitHub markdown formatting with appropriate emojis and tables
"""
        return prompt.strip()


    def extract_similar_snippets(self, similar_codes: dict) -> str:
        result = ""
        for counter, similar_code in enumerate(similar_codes):
            result += f"#### Code {counter + 1}\n"
            doc = similar_code['code']
            if len(doc) > 1000:
                doc = doc[:1000] + "..."
            result += f"```python\n{doc.strip()}\n```\n\n"

        return result.strip()

    def generate_code_duplication_check_prompt(self, code_snippet: str, similar_codes: dict) -> str:
        if not code_snippet.strip():
            return ""

        similar_code = self.extract_similar_snippets(similar_codes)
        if not similar_code:
            return ""

        prompt = f"""## Code Duplication Analysis

You are a Python code reviewer AI. Analyze the target code for duplication and quality issues.

### 🎯 Target Code (from current PR)
```python
{code_snippet.strip()}
```

### 📚 Reference Code List (existing codebase)
{similar_code}

## Analysis Required
1. **Duplication Check**: Compare target code with each reference code
2. **Code Quality**: Identify potential issues in target code
3. **Recommendations**: Suggest specific improvements

## Expected Output Format
Use the following GitHub markdown format for your response:

### 🔍 Similarity Analysis
| Reference | Status | Similarity | Reason |
|-----------|--------|------------|---------|
| #1 | `[DUPLICATE/SIMILAR/DIFFERENT]` | X% | [brief explanation] |
| #2 | `[DUPLICATE/SIMILAR/DIFFERENT]` | X% | [brief explanation] |

### 🐛 Issues Found
- [List specific issues: logic errors, performance, complexity, etc.]

### 💡 Recommendations
- [Specific actionable suggestions]
- [Refactoring suggestions if duplication found]

### 📋 Summary
**Overall Status:** `[NEEDS_REFACTORING/ACCEPTABLE/GOOD]`

## Guidelines
- **DUPLICATE**: >90% similar logic, same functionality
- **SIMILAR**: 70-90% similar, shared patterns but different purpose
- **DIFFERENT**: <70% similar
- Focus on logic similarity, not variable names
- Be concise but specific
- Prioritize actionable feedback
- Use GitHub markdown formatting with tables and badges

### Example Analysis
**Target:** `def calculate_total(items): return sum(item.price for item in items)`
**Reference:** `def get_sum(products): return sum(p.cost for p in products)`

| Reference | Status | Similarity | Reason |
|-----------|--------|------------|---------|
| #1 | `SIMILAR` | 85% | Same logic pattern, different variable names and attribute names |

**Recommendations:**
- Consider consolidating similar functions
- Use consistent naming conventions
"""
        return prompt.strip()

    def generate_summary_prompt(self, coding_style_result: str, duplication_check_result: str) -> str:
        prompt = f"""## Code Review Summary Generation

You are a senior code review engineer. Synthesize the following two code analysis reports into a unified, actionable summary using GitHub markdown format.

### Input Reports

#### Duplication Analysis
{duplication_check_result}

#### Code Quality Analysis
{coding_style_result}

## Task Requirements
1. **Consolidate findings** - Merge overlapping issues, avoid redundancy
2. **Prioritize by impact** - Critical issues first, then major, then minor
3. **Provide actionable recommendations** - Specific steps for improvement
4. **Assess overall quality** - Final verdict on code readiness

## Expected Output Format
Use the following GitHub markdown format for your response:

# 🔍 Code Review Summary

## 🔴 Critical Issues (Must Fix)
- [ ] [Issue with severity justification]
- [ ] [Issue with severity justification]

## 🟡 Major Issues (Should Fix)
- [ ] [Issue with impact explanation]
- [ ] [Issue with impact explanation]

## 🟢 Minor Issues (Nice to Have)
- [ ] [Improvement suggestion]
- [ ] [Improvement suggestion]

## 🔄 Duplication Assessment
| Metric | Value |
|--------|-------|
| **Status** | `[NO_DUPLICATES/MINOR_SIMILARITY/SIGNIFICANT_DUPLICATION]` |
| **Details** | [Brief explanation of duplication findings] |
| **Action** | [Specific refactoring recommendation if needed] |

## 📋 Recommended Actions
1. **Priority 1:** [Prioritized action item]
2. **Priority 2:** [Prioritized action item]
3. **Priority 3:** [Prioritized action item]

## 📊 Overall Assessment
| Metric | Value | Notes |
|--------|-------|-------|
| **Code Quality** | `[POOR/NEEDS_IMPROVEMENT/ACCEPTABLE/GOOD/EXCELLENT]` | [Brief justification] |
| **Ready for Merge** | `[YES/NO/WITH_CHANGES]` | [Brief justification] |
| **Confidence** | `[HIGH/MEDIUM/LOW]` | [Brief justification] |

---
> **Note:** This review was generated automatically. Please address critical and major issues before merging.

## Guidelines for Response
- Use GitHub markdown with emojis, tables, and checkboxes
- Be concise but comprehensive
- Focus on actionable feedback
- Justify severity levels with brief explanations
- Avoid repeating similar points from both reports
- Prioritize maintainability and readability concerns
- Use appropriate status badges and formatting"""

        return prompt.strip()

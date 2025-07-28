import textwrap


class PromptGenerator:
    def __init__(self):
        self.base_header = "You are an expert Python code reviewer. Analyze the following code for quality issues and improvements."

    def generate_coding_style_prompt(self, code_snippet: str) -> str:
        prompt = f"""##### Instruction:
{self.base_header}

##### Code Snippet:
```python
{code_snippet.strip()}
```

##### Analysis Areas:
1. **Naming & Style**: Variable/function names, PEP 8 compliance
2. **Code Structure**: DRY principles, complexity, readability
3. **Design Patterns**: Appropriate pattern usage or missed opportunities
4. **SOLID Principles**: SRP, OCP, LSP, ISP, DIP violations
5. **Performance**: Potential bottlenecks or inefficiencies
6. **Error Handling**: Exception handling and edge cases
7. **Security**: Potential security vulnerabilities

##### Output Format:
**ISSUES FOUND:**
- [Category] - [Specific issue with line reference if applicable]
- [Category] - [Specific issue with line reference if applicable]

**RECOMMENDATIONS:**
- [Specific actionable improvement]
- [Refactoring suggestion with brief example if needed]

**SEVERITY ASSESSMENT:**
- Critical: [Count] (security, logic errors)
- Major: [Count] (SOLID violations, performance issues)
- Minor: [Count] (style, naming improvements)

**OVERALL RATING:** [POOR/NEEDS_IMPROVEMENT/ACCEPTABLE/GOOD/EXCELLENT]

##### Guidelines:
- Be specific about line numbers when possible
- Provide actionable suggestions, not just criticism
- Focus on the most impactful improvements first
- Consider maintainability and readability
- Keep feedback concise but thorough"""
        return prompt

    def extract_similar_snippets(self, similar_codes: dict) -> str:
        result = ""
        for counter, similar_code in enumerate(similar_codes):
            result += f"[Code {counter + 1}]\n"
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

        prompt = f"""You are a Python code reviewer AI. Analyze the target code for duplication and quality issues.

##### Target Code (from current PR):
```python
{code_snippet.strip()}
```

##### Reference Code List (existing codebase):
{similar_code}

##### Analysis Required:
1. **Duplication Check**: Compare target code with each reference code
2. **Code Quality**: Identify potential issues in target code
3. **Recommendations**: Suggest specific improvements

##### Output Format:
**SIMILARITY ANALYSIS:**
- Reference #1: [DUPLICATE/SIMILAR/DIFFERENT] - X% similarity
  - Reason: [brief explanation]
- Reference #2: [DUPLICATE/SIMILAR/DIFFERENT] - X% similarity
  - Reason: [brief explanation]

**ISSUES FOUND:**
- [List specific issues: logic errors, performance, complexity, etc.]

**RECOMMENDATIONS:**
- [Specific actionable suggestions]
- [Refactoring suggestions if duplication found]

**SUMMARY:**
Overall Status: [NEEDS_REFACTORING/ACCEPTABLE/GOOD]

##### Guidelines:
- DUPLICATE: >90% similar logic, same functionality
- SIMILAR: 70-90% similar, shared patterns but different purpose
- DIFFERENT: <70% similar
- Focus on logic similarity, not variable names
- Be concise but specific
- Prioritize actionable feedback

##### Example:
Target: `def calculate_total(items): return sum(item.price for item in items)`
Reference: `def get_sum(products): return sum(p.cost for p in products)`

**SIMILARITY ANALYSIS:**
- Reference #1: SIMILAR - 85% similarity
  - Reason: Same logic pattern, different variable names and attribute names

**RECOMMENDATIONS:**
- Consider consolidating similar functions
- Use consistent naming conventions
"""
        return prompt.strip()

    def generate_summary_prompt(self, coding_style_result: str, duplication_check_result: str) -> str:
        prompt = f"""You are a senior code review engineer. Synthesize the following two code analysis reports into a unified, actionable summary.

##### Input Reports:

**Duplication Analysis:**
{duplication_check_result}

**Code Quality Analysis:**
{coding_style_result}

##### Task Requirements:
1. **Consolidate findings** - Merge overlapping issues, avoid redundancy
2. **Prioritize by impact** - Critical issues first, then major, then minor
3. **Provide actionable recommendations** - Specific steps for improvement
4. **Assess overall quality** - Final verdict on code readiness

##### Output Format:

## 🔍 Code Review Summary

### Critical Issues (Must Fix)
- [Issue with severity justification]
- [Issue with severity justification]

### Major Issues (Should Fix)
- [Issue with impact explanation]
- [Issue with impact explanation]

### Minor Issues (Nice to Have)
- [Improvement suggestion]
- [Improvement suggestion]

### Duplication Assessment
- **Status**: [NO_DUPLICATES/MINOR_SIMILARITY/SIGNIFICANT_DUPLICATION]
- **Details**: [Brief explanation of duplication findings]
- **Action**: [Specific refactoring recommendation if needed]

### Recommended Actions
1. [Prioritized action item]
2. [Prioritized action item]
3. [Prioritized action item]

### Overall Assessment
- **Code Quality**: [POOR/NEEDS_IMPROVEMENT/ACCEPTABLE/GOOD/EXCELLENT]
- **Ready for Merge**: [YES/NO/WITH_CHANGES]
- **Confidence**: [HIGH/MEDIUM/LOW]

##### Guidelines:
- Be concise but comprehensive
- Focus on actionable feedback
- Justify severity levels
- Avoid repeating similar points from both reports
- Prioritize maintainability and readability concerns"""

        return prompt.strip()

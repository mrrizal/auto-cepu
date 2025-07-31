import textwrap
from typing import List, Dict, Any, Optional


class CodeChunk:
    """Represents a code chunk with metadata."""
    def __init__(self, code: str, start_line: int, end_line: int, line_count: int):
        self.code = code
        self.start_line = start_line
        self.end_line = end_line
        self.line_count = line_count


class PromptGenerator:
    def __init__(self):
        self.base_header = "You are an expert Python code reviewer. Analyze the following code for quality issues and improvements."

    def _format_code_chunks(self, code_chunks: List[Dict[str, Any]], chunk_type: str = "code") -> str:
        """Format code chunks with line number context."""
        if not code_chunks:
            return f"No {chunk_type} changes."

        formatted_chunks = []
        for i, chunk in enumerate(code_chunks, 1):
            code = chunk.code.strip()
            start_line = chunk.start_line
            end_line = chunk.end_line

            chunk_header = f"### {chunk_type.title()} Block {i} (Lines {start_line}-{end_line})"
            chunk_content = f"```python\n{code}\n```"
            formatted_chunks.append(f"{chunk_header}\n{chunk_content}")

        return "\n\n".join(formatted_chunks)

    def _extract_change_context(self, added_code: List[Dict], deleted_code: List[Dict]) -> Dict[str, Any]:
        """Extract meaningful context from code changes."""
        context = {
            'total_added_lines': sum(chunk.line_count for chunk in added_code),
            'total_deleted_lines': sum(chunk.line_count for chunk in deleted_code),
            'change_type': 'modification',
            'complexity_change': 'unknown',
            'line_ranges': {
                'added': [(chunk.start_line, chunk.end_line) for chunk in added_code],
                'deleted': [(chunk.start_line, chunk.end_line) for chunk in deleted_code]
            }
        }

        # Determine change type
        if not deleted_code and added_code:
            context['change_type'] = 'addition'
        elif deleted_code and not added_code:
            context['change_type'] = 'deletion'
        elif len(added_code) > len(deleted_code):
            context['change_type'] = 'expansion'
        elif len(added_code) < len(deleted_code):
            context['change_type'] = 'reduction'

        # Assess complexity change
        if context['total_added_lines'] > context['total_deleted_lines'] * 1.5:
            context['complexity_change'] = 'increased'
        elif context['total_added_lines'] < context['total_deleted_lines'] * 0.5:
            context['complexity_change'] = 'decreased'
        else:
            context['complexity_change'] = 'maintained'

        return context

    def generate_coding_style_prompt_with_diff(
        self,
        added_code: List[Dict[str, Any]],
        deleted_code: List[Dict[str, Any]],
        full_function_code: str = "",
        function_name: str = "",
        file_path: str = ""
    ) -> str:
        """
        Generate an enhanced prompt for code review using diff analysis.
        """
        # Extract change context
        context = self._extract_change_context(added_code, deleted_code)

        # Format code sections
        added_section = self._format_code_chunks(added_code, "Added")
        deleted_section = self._format_code_chunks(deleted_code, "Deleted")

        # Format full function context
        full_code_block = f"```python\n{full_function_code.strip()}\n```" if full_function_code else "Full function context not available."

        # Create context summary
        context_summary = f"""
**Change Summary:**
- **Type:** {context['change_type'].title()}
- **Lines Added:** {context['total_added_lines']}
- **Lines Deleted:** {context['total_deleted_lines']}
- **Complexity:** {context['complexity_change'].title()}
- **Function:** `{function_name or 'Unknown'}`
- **File:** `{file_path or 'Unknown'}`
        """.strip()

        prompt = f"""# 🔍 Code Review Analysis

## 📋 Change Context
{context_summary}

## 🎯 Review Objectives
You are analyzing a code change in a pull request. Focus on:

1. **Behavioral Impact** - Does the change preserve, improve, or break existing functionality?
2. **Code Quality** - Is the new code better structured, more readable, and maintainable?
3. **Logic Integrity** - Are there any logical errors or edge cases introduced?
4. **Best Practices** - Does the code follow Python conventions and SOLID principles?
5. **Performance Impact** - Any potential performance improvements or regressions?

## 📄 Full Function Context
{full_code_block}

## 🟢 {added_section.split('###')[0] if '###' in added_section else 'Added Code'}
{added_section}

## 🔴 {deleted_section.split('###')[0] if '###' in deleted_section else 'Deleted Code'}
{deleted_section}

## 🔍 Analysis Framework

### Code Quality Dimensions
| Dimension | Focus Areas |
|-----------|-------------|
| **Structure** | Organization, modularity, separation of concerns |
| **Readability** | Variable names, comments, code clarity |
| **Performance** | Efficiency, resource usage, scalability |
| **Security** | Input validation, error handling, vulnerabilities |
| **Maintainability** | Code complexity, documentation, testability |

## 📊 Expected Response Format

### 🔄 Change Analysis
**Intent Preservation:** `[PRESERVED/IMPROVED/BROKEN/UNCLEAR]`
**Logic Quality:** `[IMPROVED/MAINTAINED/DEGRADED]`
**Key Changes:**
- [Describe the main functional changes]
- [Highlight any behavioral differences]

### 🐛 Issues Identified
| Severity | Issue | Line Reference | Impact |
|----------|-------|----------------|---------|
| 🔴 Critical | [Issue description] | [Line range] | [Impact description] |
| 🟡 Major | [Issue description] | [Line range] | [Impact description] |
| 🟢 Minor | [Issue description] | [Line range] | [Impact description] |

### 💡 Actionable Recommendations
1. **[Priority]** - [Specific improvement with code example if needed]
2. **[Priority]** - [Specific improvement with code example if needed]
3. **[Priority]** - [Specific improvement with code example if needed]

### 📈 Quality Assessment
| Metric | Before | After | Change |
|--------|--------|--------|---------|
| **Readability** | [Score/Rating] | [Score/Rating] | [↑↓→] |
| **Complexity** | [Score/Rating] | [Score/Rating] | [↑↓→] |
| **Maintainability** | [Score/Rating] | [Score/Rating] | [↑↓→] |

### 🎯 Final Verdict
**Overall Rating:** `[EXCELLENT/GOOD/ACCEPTABLE/NEEDS_IMPROVEMENT/POOR]`
**Merge Recommendation:** `[APPROVE/REQUEST_CHANGES/NEEDS_DISCUSSION]`
**Confidence Level:** `[HIGH/MEDIUM/LOW]`

---
> 💡 **Tip:** Focus on the most impactful issues first. Provide specific, actionable feedback rather than generic observations.
"""
        return prompt.strip()

    def extract_similar_snippets(self, similar_codes: List[Dict[str, Any]]) -> str:
        """Extract and format similar code snippets with better context."""
        if not similar_codes:
            return "No similar code found in the codebase."

        result_parts = []
        for counter, similar_code in enumerate(similar_codes, 1):
            file_path = similar_code.get('file_path', 'Unknown file')
            similarity_score = similar_code.get('similarity_score', 'N/A')
            code = similar_code.get('code', '')

            # Truncate long code snippets
            if len(code) > 800:
                code = code[:800] + "\n... [truncated]"

            snippet_header = f"#### Reference #{counter}"
            if file_path != 'Unknown file':
                snippet_header += f" - `{file_path}`"
            if similarity_score != 'N/A':
                snippet_header += f" (Similarity: {similarity_score}%)"

            code_block = f"```python\n{code.strip()}\n```"
            result_parts.append(f"{snippet_header}\n{code_block}")

        return "\n\n".join(result_parts)

    def generate_code_duplication_check_prompt(
        self,
        code_snippet: str,
        similar_codes: List[Dict[str, Any]],
        function_name: str = "",
        file_path: str = ""
    ) -> str:
        """Generate an enhanced duplication analysis prompt."""
        if not code_snippet.strip():
            return ""

        similar_code_section = self.extract_similar_snippets(similar_codes)
        if not similar_code_section or "No similar code found" in similar_code_section:
            return ""

        context_info = f"**Function:** `{function_name}`\n**File:** `{file_path}`" if function_name and file_path else ""

        prompt = f"""# 🔍 Code Duplication Analysis

## 🎯 Target Code Analysis
{context_info}

### Current Implementation
```python
{code_snippet.strip()}
```

## 📚 Similar Code References
{similar_code_section}

## 🔍 Analysis Requirements

### Duplication Assessment Criteria
| Similarity Level | Threshold | Action Required |
|------------------|-----------|-----------------|
| **Duplicate** | >90% | Immediate refactoring needed |
| **High Similarity** | 70-90% | Consider consolidation |
| **Similar Pattern** | 50-70% | Review for common patterns |
| **Different** | <50% | No action needed |

### Evaluation Dimensions
1. **Functional Logic** - Core algorithm similarity
2. **Structural Pattern** - Code organization and flow
3. **Intent Alignment** - Purpose and responsibility overlap
4. **Refactoring Potential** - Opportunities for consolidation

## 📊 Expected Analysis Format

### 🔍 Similarity Matrix
| Reference | Functional | Structural | Intent | Overall | Status |
|-----------|------------|------------|---------|---------|---------|
| #1 | XX% | XX% | XX% | XX% | `[STATUS]` |
| #2 | XX% | XX% | XX% | XX% | `[STATUS]` |

### 📈 Duplication Assessment
**Primary Concern:** `[LOGIC_DUPLICATION/PATTERN_REPETITION/BOILERPLATE/NONE]`
**Risk Level:** `[HIGH/MEDIUM/LOW]`
**Refactoring Complexity:** `[SIMPLE/MODERATE/COMPLEX]`

### 🐛 Quality Issues
- **Code Structure:** [Issues with organization, complexity]
- **Naming Conventions:** [Variable/function naming problems]
- **Error Handling:** [Missing or inadequate error handling]
- **Performance:** [Potential bottlenecks or inefficiencies]

### 💡 Consolidation Recommendations
1. **[Priority Level]** - [Specific refactoring suggestion]
   ```python
   # Example improvement
   [code example if applicable]
   ```
2. **[Priority Level]** - [Specific improvement]

### 🎯 Action Plan
| Priority | Action | Effort | Impact |
|----------|--------|--------|--------|
| P1 | [High priority action] | [Low/Med/High] | [Description] |
| P2 | [Medium priority action] | [Low/Med/High] | [Description] |

### 📋 Final Recommendation
**Status:** `[NEEDS_IMMEDIATE_REFACTORING/CONSIDER_REFACTORING/ACCEPTABLE/GOOD]`
**Next Steps:** [Specific actionable recommendations]

---
> 🔧 **Note:** Focus on functional duplication over superficial similarities. Consider maintainability impact.
"""
        return prompt.strip()

    def generate_summary_prompt(
        self,
        coding_style_result: str,
        duplication_check_result: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate an enhanced summary prompt with better context integration."""

        context_section = ""
        if context:
            context_section = f"""
## 📊 Change Context
- **Function:** `{context.get('function_name', 'Unknown')}`
- **File:** `{context.get('file_path', 'Unknown')}`
- **Change Type:** {context.get('change_type', 'Unknown')}
- **Lines Modified:** +{context.get('total_added_lines', 0)} -{context.get('total_deleted_lines', 0)}
"""

        prompt = f"""# 📋 Comprehensive Code Review Summary

You are a senior engineering lead conducting a final code review assessment. Synthesize the following analysis reports into a unified, executive-ready summary.

{context_section}

## 📁 Input Analysis Reports

### 🔄 Code Quality & Diff Analysis
{coding_style_result}

### 🔍 Duplication Analysis
{duplication_check_result}

## 🎯 Synthesis Requirements

1. **Consolidate Findings** - Merge overlapping issues, eliminate redundancy
2. **Risk Assessment** - Evaluate impact on system stability and maintainability
3. **Priority Classification** - Organize by business and technical impact
4. **Action Planning** - Provide clear, prioritized remediation steps
5. **Decision Support** - Give clear merge/hold recommendation

## 📊 Expected Summary Format

# 🚨 Executive Code Review Summary

## 🔴 Blocking Issues (Must Fix Before Merge)
- [ ] **[Issue Category]** - [Specific issue with business/technical impact]
  - **Impact:** [Risk to system/users/maintainability]
  - **Action:** [Specific fix required]
- [ ] **[Issue Category]** - [Specific issue with business/technical impact]

## 🟡 High Priority (Should Address Soon)
- [ ] **[Issue Category]** - [Issue description with context]
  - **Impact:** [Medium-term consequences]
  - **Effort:** [Low/Medium/High]
- [ ] **[Issue Category]** - [Issue description with context]

## 🟢 Enhancement Opportunities (Nice to Have)
- [ ] **[Category]** - [Improvement suggestion]
- [ ] **[Category]** - [Code quality enhancement]

## 📊 Risk Assessment Matrix
| Risk Category | Level | Details | Mitigation |
|---------------|-------|---------|------------|
| **Security** | `[HIGH/MED/LOW]` | [Specific concerns] | [Required actions] |
| **Performance** | `[HIGH/MED/LOW]` | [Potential impacts] | [Optimization steps] |
| **Maintainability** | `[HIGH/MED/LOW]` | [Code quality issues] | [Refactoring needs] |
| **Duplication** | `[HIGH/MED/LOW]` | [Redundancy level] | [Consolidation plan] |

## 🔄 Code Duplication Status
| Metric | Assessment | Action Required |
|--------|------------|-----------------|
| **Duplication Level** | `[NONE/LOW/MODERATE/HIGH]` | [Specific steps if needed] |
| **Refactoring Priority** | `[P0/P1/P2/P3]` | [Timeline recommendation] |
| **Complexity Impact** | `[POSITIVE/NEUTRAL/NEGATIVE]` | [Justification] |

## 📈 Quality Metrics Summary
| Dimension | Before | After | Change | Goal |
|-----------|--------|--------|---------|------|
| **Code Quality** | [Rating] | [Rating] | [↑↓→] | [Target] |
| **Test Coverage** | [%] | [%] | [↑↓→] | [Target] |
| **Complexity** | [Score] | [Score] | [↑↓→] | [Target] |
| **Maintainability** | [Score] | [Score] | [↑↓→] | [Target] |

## 🎯 Final Recommendations

### Immediate Actions (Next 24 Hours)
1. **[Action]** - [Specific task with owner if known]
2. **[Action]** - [Specific task with owner if known]

### Short-term Actions (Next Sprint)
1. **[Action]** - [Specific task with effort estimate]
2. **[Action]** - [Specific task with effort estimate]

### Long-term Improvements (Next Quarter)
1. **[Action]** - [Strategic improvement]
2. **[Action]** - [Process enhancement]

## ✅ Merge Decision
| Criterion | Assessment | Status |
|-----------|------------|---------|
| **Functionality** | [Working/Broken/Partial] | `[✅/❌/⚠️]` |
| **Code Quality** | [Excellent/Good/Acceptable/Poor] | `[✅/❌/⚠️]` |
| **Security** | [Secure/Minor Issues/Major Issues] | `[✅/❌/⚠️]` |
| **Performance** | [Improved/Same/Degraded] | `[✅/❌/⚠️]` |
| **Test Coverage** | [Adequate/Insufficient] | `[✅/❌/⚠️]` |

### 🚦 Final Verdict
**Recommendation:** `[APPROVE/APPROVE_WITH_COMMENTS/REQUEST_CHANGES/HOLD]`
**Confidence Level:** `[HIGH/MEDIUM/LOW]`
**Risk Level:** `[LOW/MEDIUM/HIGH]`

**Rationale:** [2-3 sentence justification for the decision]

---
> 🤖 **Auto-generated Review** | Please address all blocking issues before proceeding with merge.

## 📋 Review Guidelines
- Prioritize security and functionality issues
- Consider long-term maintainability impact
- Provide specific, actionable feedback
- Balance perfectionism with delivery velocity
- Focus on business value and user impact
"""
        return prompt.strip()

    def generate_contextual_review_prompt(
        self,
        payload_data: Dict[str, Any]
    ) -> str:
        """
        Generate a comprehensive review prompt using the full payload context.
        """
        # Extract key information from payload
        added_code = payload_data.get('added_code', [])
        deleted_code = payload_data.get('deleted_code', [])
        full_function_code = payload_data.get('full_function_code', '')
        function_name = payload_data.get('function_name', '')
        file_path = payload_data.get('file_path', '')
        project_name = payload_data.get('project_name', '')
        summary = payload_data.get('summary', {})

        # Generate the main diff analysis prompt
        main_prompt = self.generate_coding_style_prompt_with_diff(
            added_code=added_code,
            deleted_code=deleted_code,
            full_function_code=full_function_code,
            function_name=function_name,
            file_path=file_path
        )

        # Add project context
        project_context = f"""
## 🏗️ Project Context
- **Project:** `{project_name}`
- **Total Lines Added:** {summary.get('total_added_lines', 0)}
- **Total Lines Deleted:** {summary.get('total_deleted_lines', 0)}
- **Modified Lines:** {len(summary.get('added_line_numbers', []))} additions, {len(summary.get('deleted_line_numbers', []))} deletions
        """.strip()

        # Combine with enhanced context
        enhanced_prompt = f"{project_context}\n\n{main_prompt}"

        return enhanced_prompt
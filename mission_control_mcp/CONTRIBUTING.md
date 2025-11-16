# 🤝 Contributing to MissionControlMCP

Thank you for considering contributing to MissionControlMCP! This document provides guidelines for contributing to the project.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)

---

## 📜 Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code:

- **Be Respectful:** Treat everyone with respect and consideration
- **Be Constructive:** Provide helpful feedback and suggestions
- **Be Collaborative:** Work together towards common goals
- **Be Professional:** Maintain professionalism in all interactions

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- Basic knowledge of Python and MCP protocol

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
```bash
git clone https://github.com/YOUR_USERNAME/CleanEye-Hackathon.git
cd CleanEye-Hackathon/mission_control_mcp
```

3. Add upstream remote:
```bash
git remote add upstream https://github.com/AlBaraa-1/CleanEye-Hackathon.git
```

---

## 💻 Development Setup

### 1. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Development Dependencies

```bash
pip install pytest black flake8 mypy
```

### 4. Run Tests

```bash
python demo.py
```

---

## 🛠️ How to Contribute

### Types of Contributions

We welcome:

1. **Bug Fixes** - Fix issues in existing tools
2. **New Tools** - Add new MCP tools
3. **Documentation** - Improve docs and examples
4. **Tests** - Add or improve test coverage
5. **Performance** - Optimize existing code
6. **Examples** - Add real-world use cases

---

## 📝 Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with these specifics:

**Formatting:**
```python
# Good
def function_name(param1: str, param2: int) -> Dict[str, Any]:
    """
    Function description.
    
    Args:
        param1: Parameter description
        param2: Parameter description
        
    Returns:
        Dictionary with results
    """
    result = {"key": "value"}
    return result

# Bad
def functionName(param1,param2):
    result={"key":"value"}
    return result
```

**Use Black for Formatting:**
```bash
black tools/your_tool.py
```

**Type Hints:**
```python
from typing import Dict, Any, List, Optional

def process_data(data: List[str], limit: Optional[int] = None) -> Dict[str, Any]:
    ...
```

**Docstrings:**
```python
def my_function(param: str) -> Dict[str, Any]:
    """
    Brief description (one line).
    
    Longer description if needed explaining the function's
    purpose, behavior, and any important details.
    
    Args:
        param: Description of parameter
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When invalid input
        FileNotFoundError: When file not found
        
    Example:
        >>> result = my_function("example")
        >>> print(result['key'])
        'value'
    """
    ...
```

---

## ✅ Testing Guidelines

### Writing Tests

All new tools must include tests:

**1. Create Test File:**
```python
# tests/test_your_tool.py
import pytest
from tools.your_tool import your_function

def test_your_function_success():
    """Test successful operation"""
    result = your_function("valid_input")
    assert result['success'] == True
    assert 'data' in result

def test_your_function_error():
    """Test error handling"""
    with pytest.raises(ValueError):
        your_function("invalid_input")
```

**2. Run Tests:**
```bash
pytest tests/test_your_tool.py -v
```

### Test Coverage

Aim for 90%+ coverage:
```bash
pytest --cov=tools tests/
```

### Test Categories

- **Unit Tests** - Test individual functions
- **Integration Tests** - Test tool combinations
- **MCP Tests** - Test MCP protocol integration

---

## 🔄 Pull Request Process

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 2. Make Changes

- Write code following style guide
- Add tests for new functionality
- Update documentation
- Run tests locally

### 3. Commit Changes

Use clear commit messages:
```bash
git add .
git commit -m "Add: New email sentiment analysis tool"
# or
git commit -m "Fix: PDF reader handling encrypted files"
# or
git commit -m "Docs: Update API reference for web fetcher"
```

**Commit Message Format:**
- `Add:` - New features
- `Fix:` - Bug fixes
- `Docs:` - Documentation changes
- `Test:` - Test additions/changes
- `Refactor:` - Code refactoring
- `Perf:` - Performance improvements

### 4. Push to Fork

```bash
git push origin feature/your-feature-name
```

### 5. Create Pull Request

1. Go to GitHub repository
2. Click "New Pull Request"
3. Select your branch
4. Fill in PR template:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- [ ] All tests pass
- [ ] New tests added
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guide
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No breaking changes
```

### 6. Code Review

- Address reviewer feedback
- Make requested changes
- Push updates to same branch

### 7. Merge

Once approved, maintainers will merge your PR.

---

## 🐛 Reporting Bugs

### Before Submitting

1. Check existing issues
2. Verify bug in latest version
3. Gather reproduction steps

### Bug Report Template

```markdown
**Bug Description**
Clear description of the bug

**To Reproduce**
Steps to reproduce:
1. Run command '...'
2. Call function '...'
3. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: Windows 11
- Python: 3.12
- MCP Version: 1.0.0

**Error Messages**
```
Paste error messages here
```

**Additional Context**
Any other relevant information
```

---

## 💡 Suggesting Features

### Feature Request Template

```markdown
**Feature Description**
What feature would you like to see?

**Use Case**
Why is this feature needed? How will it be used?

**Proposed Solution**
How should this feature work?

**Alternatives Considered**
What other approaches did you consider?

**Additional Context**
Any mockups, examples, or references
```

---

## 🏗️ Adding New Tools

### Tool Structure

```python
# tools/my_new_tool.py
"""
Tool Name - Brief description
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def my_tool_function(param: str) -> Dict[str, Any]:
    """
    Tool description.
    
    Args:
        param: Parameter description
        
    Returns:
        Dictionary with results
    """
    try:
        # Implementation
        result = process_data(param)
        
        return {
            "success": True,
            "data": result,
            "metadata": {}
        }
        
    except Exception as e:
        logger.error(f"Error in my_tool: {e}")
        raise
```

### Register Tool in MCP Server

```python
# mcp_server.py
from tools.my_new_tool import my_tool_function

# In tool registration section:
server.register_tool(
    name="my_tool",
    description="What this tool does",
    input_schema={
        "type": "object",
        "properties": {
            "param": {"type": "string", "description": "Param description"}
        },
        "required": ["param"]
    }
)
```

### Add Tests

```python
# tests/test_my_tool.py
def test_my_tool():
    result = my_tool_function("test_input")
    assert result['success'] == True
```

### Update Documentation

1. Add to README.md tool list
2. Add to API.md reference
3. Add to EXAMPLES.md with use case
4. Add sample files to examples/

---

## 📚 Documentation Guidelines

### What to Document

- **README.md** - Overview, setup, quick start
- **API.md** - Complete function signatures
- **EXAMPLES.md** - Real-world use cases
- **TESTING.md** - How to test
- **Code Comments** - Complex logic explanation

### Documentation Style

```python
# Good - Clear and concise
def calculate_total(items: List[float]) -> float:
    """Calculate the sum of item prices."""
    return sum(items)

# Bad - Over-documented
def calculate_total(items: List[float]) -> float:
    """
    This function takes a list of items and calculates the total
    by iterating through each item and adding them together using
    the built-in sum function and then returns the result.
    """
    return sum(items)
```

---

## 🎯 Development Workflow

### Typical Workflow

1. **Check Issues** - Find or create issue
2. **Discuss** - Comment on issue before starting
3. **Branch** - Create feature branch
4. **Develop** - Write code + tests
5. **Test** - Run all tests locally
6. **Document** - Update docs
7. **Commit** - Clear commit messages
8. **Push** - Push to your fork
9. **PR** - Create pull request
10. **Review** - Address feedback
11. **Merge** - Maintainer merges

### Stay in Sync

```bash
# Pull latest changes from upstream
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

---

## 🏆 Recognition

Contributors will be:
- Listed in README.md contributors section
- Mentioned in release notes
- Credited in commit history

---

## 📞 Getting Help

- **Questions:** Open a GitHub Discussion
- **Chat:** Join our Discord (link in README)
- **Issues:** GitHub Issues for bugs/features

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to MissionControlMCP!** 🚀

Every contribution, no matter how small, helps make this project better for everyone.

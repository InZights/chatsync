# Contributing to ConvoHub

First off, thank you for considering contributing to ConvoHub! It's people like you that make ConvoHub such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our commitment to providing a welcoming and inspiring community for all.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps which reproduce the problem**
* **Provide specific examples to demonstrate the steps**
* **Describe the behavior you observed after following the steps**
* **Explain which behavior you expected to see instead and why**
* **Include logs and error messages**

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title**
* **Provide a step-by-step description of the suggested enhancement**
* **Provide specific examples to demonstrate the steps**
* **Describe the current behavior and explain which behavior you expected to see instead**
* **Explain why this enhancement would be useful**

### Pull Requests

* Fill in the required template
* Do not include issue numbers in the PR title
* Follow the Python style guide (PEP 8)
* Include thoughtfully-worded, well-structured tests
* Document new code
* End all files with a newline

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/convohub.git
cd convohub

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available

# Install pre-commit hooks
pip install pre-commit
pre-commit install
```

## Development Workflow

1. **Create a branch**
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make your changes**
   * Write meaningful commit messages
   * Keep commits atomic (one logical change per commit)
   * Follow the code style guide

3. **Test your changes**
   ```bash
   # Run tests
   pytest tests/
   
   # Run linter
   flake8 src/ scripts/
   
   # Format code
   black src/ scripts/
   ```

4. **Push to your fork**
   ```bash
   git push origin feature/my-new-feature
   ```

5. **Create a Pull Request**
   * Provide a clear description of the changes
   * Reference any related issues
   * Wait for review and address feedback

## Code Style Guidelines

### Python

* Follow PEP 8
* Use type hints where appropriate
* Write docstrings for all public modules, functions, classes, and methods
* Maximum line length: 100 characters
* Use meaningful variable and function names

**Example:**
```python
def transform_message(message: Dict[str, Any], user_map: Dict[str, str]) -> Dict[str, Any]:
    """
    Transform Teams message to Slack format.
    
    Args:
        message: Teams message dictionary
        user_map: Mapping of Teams user IDs to Slack user IDs
        
    Returns:
        Slack-formatted message dictionary
    """
    # Implementation
    pass
```

### Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

**Example:**
```
Add sentiment analysis module

- Implement BERT-based sentiment classifier
- Add batch processing support
- Include unit tests and documentation

Fixes #123
```

## Testing

* Write unit tests for all new functionality
* Maintain or improve code coverage
* Test edge cases and error conditions
* Use meaningful test names

```python
def test_transform_message_preserves_thread_structure():
    """Test that parent-child relationships are maintained in transformation."""
    # Test implementation
    pass
```

## Documentation

* Update README.md if needed
* Add docstrings to new functions/classes
* Update relevant documentation in `docs/`
* Include code examples where helpful

## Project Structure

When adding new features, follow the existing structure:

```
src/teams_to_slack/     # Core library code
scripts/                # Executable scripts
tests/                  # Test files (mirror src/ structure)
docs/                   # Documentation
config/                 # Configuration files
```

## Additional Notes

### Issue and Pull Request Labels

* `bug` - Something isn't working
* `enhancement` - New feature or request
* `documentation` - Improvements or additions to documentation
* `good first issue` - Good for newcomers
* `help wanted` - Extra attention is needed
* `question` - Further information is requested

### Financial Contributions

We also welcome financial contributions. Please contact the maintainers for more information.

## Recognition

Contributors will be recognized in:
* README.md Contributors section
* Release notes
* Project documentation

Thank you for your contributions! 🎉

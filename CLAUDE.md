# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands
- Run all tests: `python -m pytest`
- Run single test: `python -m pytest app/tests/test_file.py::test_function_name`
- Run tests with verbosity: `python -m pytest -v`
- Install dependencies: `pip install -r requirements.txt`

## Code Style Guidelines
- **Imports**: Organize imports by standard library, third-party, then local imports with a blank line between groups
- **Types**: Use type hints for function parameters and return values
- **Docstrings**: Use docstrings with Parameters/Returns sections formatted with proper indentation
- **Error Handling**: Use explicit exception raising with descriptive messages
- **Naming**: Use snake_case for variables/functions, PascalCase for classes
- **Testing**: Each module should have corresponding test files in app/tests/
- **Functions**: Keep functions focused on a single responsibility
- **Dependencies**: When adding new packages, update requirements.txt
- **LLM Services**: Follow the provider factory pattern for new LLM integrations
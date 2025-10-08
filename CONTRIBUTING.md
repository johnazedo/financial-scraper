# Contributing to Financial Scraper

Thank you for your interest in contributing to the Financial Scraper project! This document provides guidelines and instructions for contributing to make the process smooth and effective for everyone involved.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment Setup](#development-environment-setup)
- [Branching Strategy](#branching-strategy)
- [Making Changes](#making-changes)
- [Pull Request Process](#pull-request-process)
- [Code Style Guidelines](#code-style-guidelines)
- [Documentation](#documentation)
- [Reporting Bugs](#reporting-bugs)
- [Feature Requests](#feature-requests)

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone. Please be considerate of others and act professionally.

## Getting Started

1. Fork the repository on GitHub.
2. Clone your fork to your local machine:
   ```bash
   git clone https://github.com/YOUR_USERNAME/web-scraping-funds-explorer.git
   cd web-scraping-funds-explorer
   ```
3. Add the original repository as an upstream remote:
   ```bash
   git remote add upstream https://github.com/johnazedo/web-scraping-funds-explorer.git
   ```
4. Keep your fork synchronized with the upstream repository:
   ```bash
   git fetch upstream
   git merge upstream/main
   ```

## Development Environment Setup

1. Ensure you have Python 3.10 or higher installed.
2. Install Poetry (dependency management tool):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```
3. Install project dependencies:
   ```bash
   poetry install
   ```
4. Activate the virtual environment:
   ```bash
   poetry shell
   ```

## Branching Strategy

- `main`: The primary branch containing stable code.
- Feature branches: Create a new branch for each feature or bug fix.

Naming conventions for branches:
- Feature: `feature/short-description`
- Bug fix: `fix/issue-description`
- Documentation: `docs/what-changed`

## Making Changes

1. Create a new branch from `main` for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes, following the code style guidelines.
3. Commit your changes with clear, descriptive commit messages:
   ```bash
   git commit -m "feat: add support for new financial data source"
   ```
4. Push your branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

## Pull Request Process

1. Ensure your code follows the style guidelines.
2. Update the README.md with details of changes if applicable.
3. Submit a pull request to the `main` branch of the original repository.
4. Include a clear description of the changes and any relevant issue numbers.
5. Wait for review from the maintainers.

## Code Style Guidelines

- Follow [PEP 8](https://peps.python.org/pep-0008/) style guide for Python code.
- Use meaningful variable and function names.
- Write docstrings for all functions, classes, and modules.
- Keep functions focused and small.
- Use type annotations where possible.

Example:
```python
def get_stock_data(ticker: str) -> dict:
    """
    Retrieve stock data for the given ticker.
    
    Args:
        ticker: The stock ticker symbol.
        
    Returns:
        A dictionary containing the stock data.
    """
    # implementation
```

## Documentation

- Update documentation for any new features or changes.
- Include examples for new functionality.
- Keep the README updated with new commands or features.

## Adding a New Data Provider

To add support for a new financial data source:

1. Create a new file in the `financial_scraper/providers/` directory.
2. Implement the necessary scraping functionality.
3. Create a corresponding service in the `services/` directory.
4. Update the main CLI commands to include the new functionality.
5. Add documentation and examples.

## Reporting Bugs

When reporting bugs, please include:

1. A clear, descriptive title.
2. Steps to reproduce the issue.
3. Expected behavior and what actually happened.
4. Your operating system, Python version, and other relevant environment details.
5. Any error messages or logs.

## Feature Requests

Feature requests are welcome! Please provide:

1. A clear description of the feature.
2. Explanation of why it would be valuable to the project.
3. Examples of how it might be used.

---

Thank you for contributing to Financial Scraper! Your efforts help improve the project for everyone.
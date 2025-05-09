# Contributing to AstroBot

Thank you for your interest in contributing to AstroBot! We welcome contributions from everyone, whether you're fixing a typo, adding a feature, improving documentation, or reporting a bug.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Community](#community)

## Code of Conduct

We expect all contributors to follow our [Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project, you agree to abide by its terms.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/astrobot.git
   cd astrobot
   ```
3. **Set up the upstream remote**:
   ```bash
   git remote add upstream https://github.com/original-owner/astrobot.git
   ```
4. **Create a branch** for your work:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Environment

### Prerequisites
- Python 3.11 or higher
- Node.js 20 or higher
- PostgreSQL database
- Discord developer account (for bot testing)

### Setup
1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Install Node.js dependencies:
   ```bash
   npm install
   ```
3. Set up environment variables (see `.env.example`)
4. Run database migrations:
   ```bash
   python -m flask db upgrade
   ```
5. Start the development server:
   ```bash
   python main.py
   ```

## Pull Request Process

1. **Update your fork** with the latest changes from upstream:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```
2. **Commit your changes** with clear, descriptive commit messages:
   ```bash
   git add .
   git commit -m "feat: Add new feature X"
   ```
   We follow [Conventional Commits](https://www.conventionalcommits.org/) for commit messages.
3. **Push your branch** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
4. **Create a Pull Request** through the GitHub interface
5. **Wait for review** and address any feedback

## Coding Standards

- **Python**: We follow [PEP 8](https://pep8.org/) coding style
- **JavaScript**: We follow [ESLint](https://eslint.org/) with the Airbnb configuration
- **HTML/CSS**: Use consistent indentation and follow BEM methodology for CSS classes

## Testing

- Write tests for your code when applicable
- Ensure all existing tests pass with your changes
- Run tests locally before submitting your PR:
  ```bash
  pytest
  ```

## Documentation

- Update documentation to reflect your changes when applicable
- Document new features, API endpoints, or significant changes
- Use clear, concise language and include examples when possible

## Community

- Join our [Discord server](https://discord.gg/your-community-link) for discussions
- Attend community meetings to share ideas and get help
- Help answer questions in issues and pull requests

Thank you for contributing to AstroBot!
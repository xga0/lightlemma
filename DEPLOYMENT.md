# Deployment Guide

This project uses GitHub Actions to automatically test and deploy to PyPI when changes are pushed to the main branch.

## Workflow Overview

The deployment workflow (`test-and-deploy.yml`) performs the following steps:

1. **Testing**: Runs the test suite across multiple Python versions (3.8-3.12)
2. **Version Bumping**: Automatically increments the patch version number
3. **Building**: Creates distribution packages
4. **Publishing**: Uploads to PyPI if all tests pass
5. **Tagging**: Creates a git tag and GitHub release

## Initial Setup

To enable automatic deployment, you need to configure the following GitHub repository secrets:

### Required Secrets

1. **PYPI_API_TOKEN**: Your PyPI API token
   - Go to [PyPI Account Settings](https://pypi.org/manage/account/token/)
   - Create a new API token with scope "Entire account"
   - Add it as a repository secret named `PYPI_API_TOKEN`

### Setting up GitHub Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the `PYPI_API_TOKEN` secret

## How Deployment Works

### Automatic Deployment

- **Trigger**: Push to `main` branch
- **Version**: Automatically bumps patch version (e.g., 0.1.2 → 0.1.3)
- **Condition**: Only deploys if all tests pass

### Manual Deployment

You can also trigger deployment manually with custom version bumping:

1. Go to **Actions** tab in your GitHub repository
2. Select **Test and Deploy to PyPI** workflow
3. Click **Run workflow**
4. Choose version bump type:
   - `patch`: 0.1.2 → 0.1.3 (default)
   - `minor`: 0.1.2 → 0.2.0
   - `major`: 0.1.2 → 1.0.0

## Workflow Files

- `.github/workflows/test-and-deploy.yml`: Main workflow configuration
- `.github/workflows/version_bump.py`: Custom version bumping script

## Testing Locally

Before pushing, you can test the package build locally:

```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
python -m pytest tests/ -v

# Test package build
python -m build
twine check dist/*
```

## Version Management

The current version is stored in `pyproject.toml` and follows semantic versioning:

- **Patch** (0.1.2 → 0.1.3): Bug fixes, small improvements
- **Minor** (0.1.2 → 0.2.0): New features, backwards compatible
- **Major** (0.1.2 → 1.0.0): Breaking changes

## Troubleshooting

### Tests Failing

If tests fail, the deployment will be automatically cancelled. Fix the issues and push again.

### PyPI Upload Errors

Common issues:
- **401 Unauthorized**: Check your `PYPI_API_TOKEN` secret
- **403 Forbidden**: Version already exists on PyPI
- **400 Bad Request**: Package validation failed

### Version Conflicts

If a version already exists on PyPI, the workflow will fail. You can:
1. Run the workflow manually with a higher version bump type
2. Or wait for the next push (which will auto-increment)

## Security Notes

- The `PYPI_API_TOKEN` should be kept secure and never exposed in logs
- The workflow only runs on the main branch to prevent unauthorized deployments
- All tests must pass before any deployment proceeds 
# Deployment Guide

This project uses a release-based deployment workflow. Here's how to release a new version:

## Steps to Release

1. **Update version numbers** in your code:
   ```bash
   # Update version in pyproject.toml
   vim pyproject.toml  # Change version = "x.y.z"
   
   # Update version in __init__.py  
   vim lightlemma/__init__.py  # Change __version__ = "x.y.z"
   ```

2. **Commit and push your changes**:
   ```bash
   git add .
   git commit -m "Prepare release x.y.z"
   git push origin main
   ```

3. **Create and push a tag**:
   ```bash
   # Create a tag (must start with 'v')
   git tag v0.1.4
   
   # Push the tag
   git push origin v0.1.4
   ```

4. **Create a GitHub Release**:
   - Go to your GitHub repository
   - Click **Releases** → **Create a new release**
   - Select the tag you just pushed (e.g., `v0.1.4`)
   - Add a release title and description
   - Click **Publish release**

## What Happens Next

When you **publish a GitHub release**:

1. **Tests run** across Python 3.8-3.12
2. **Version verification** ensures release tag matches `pyproject.toml`
3. **Package builds** if tests pass
4. **Deploys to PyPI** automatically
5. **Updates release** with PyPI package link

## Workflow Triggers

- **GitHub Release publication**: Runs tests + deploys if successful
- **Pull requests**: Runs tests only (no deployment)
- **Tag pushes**: No action (deployment waits for release)

## Version Format

- Tags must start with `v` (e.g., `v0.1.4`, `v1.0.0`)
- Version in `pyproject.toml` must match tag (without `v` prefix)
- Version in `__init__.py` should also match for consistency

## Example Release Process

```bash
# Prepare version 0.1.5
sed -i 's/version = "0.1.4"/version = "0.1.5"/' pyproject.toml
sed -i 's/__version__ = "0.1.4"/__version__ = "0.1.5"/' lightlemma/__init__.py

# Commit and tag
git add .
git commit -m "Prepare release 0.1.5"
git push origin main
git tag v0.1.5
git push origin v0.1.5

# Then create GitHub Release manually from the web interface
# selecting tag v0.1.5
```

## Benefits of This Approach

- **Full control**: You decide when to deploy by publishing releases
- **Release notes**: Add meaningful descriptions to your releases  
- **Testing first**: Tags can exist without deployment until you're ready
- **Clear history**: GitHub releases provide a clear record of all deployments

## Required Setup

To enable deployment, you need to configure the following GitHub repository secret:

### PYPI_API_TOKEN

1. Go to [PyPI Account Settings](https://pypi.org/manage/account/token/)
2. Create a new API token with scope "Entire account"
3. In your GitHub repository: **Settings** → **Secrets and variables** → **Actions**
4. Add secret named `PYPI_API_TOKEN` with your token value

## Testing Locally

Before creating a release, test locally:

```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
python -m pytest tests/ -v

# Test package build
python -m build
twine check dist/*
```

## Rolling Back

If deployment fails, you can:
1. Fix the issues in your code
2. Create a new patch version
3. Push a new tag and create a new release

**Note**: You cannot reuse the same tag/version number on PyPI.

## Troubleshooting

### Common Issues

- **Tests failing**: Fix the code and create a new version/tag/release
- **Version mismatch**: Ensure release tag version matches `pyproject.toml`
- **PyPI upload errors**: 
  - `401 Unauthorized`: Check `PYPI_API_TOKEN` secret
  - `403 Forbidden`: Version already exists on PyPI
  - `400 Bad Request`: Package validation failed

### Security Notes

- Keep `PYPI_API_TOKEN` secure and never expose in logs
- Deployment only happens when you publish releases, giving you full control
- All tests must pass before deployment proceeds
- Release publication is the trigger, not tag creation 
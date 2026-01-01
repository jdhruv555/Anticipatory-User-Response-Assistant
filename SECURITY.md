# Security Policy

## Supported Versions

Currently supported versions of AURA:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please **DO NOT** open a public issue.

Instead, please email the repository owner directly with details of the vulnerability.

## Security Best Practices

1. **Never commit API keys or credentials** to this repository
2. **Use environment variables** for all sensitive configuration
3. **Keep dependencies updated** to patch security vulnerabilities
4. **Review code changes** before merging to main branch

## Protected Information

The following should NEVER be committed:
- API keys (OpenAI, Anthropic, Google Cloud)
- Service account JSON files
- Database passwords
- Authentication tokens
- Personal information

---

**Remember**: This is a public repository. Assume all code is visible to everyone.


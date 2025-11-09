# Security Notice - Credential Rotation Required

## Critical Security Action Required

If your `.env` file contains live production credentials, you must rotate them immediately.

### Credentials to Rotate

1. **AWS Credentials (3 sets)**
   - `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`
   - `AUTH_AWS_ACCESS_KEY_ID` / `AUTH_AWS_SECRET_ACCESS_KEY`
   - `DYNAMODB_AWS_ACCESS_KEY_ID` / `DYNAMODB_AWS_SECRET_ACCESS_KEY`

2. **API Keys**
   - `OPENAI_API_KEY`
   - `ELEVENLABS_API_KEY`
   - `BROWSER_USE_API_KEY`

3. **AWS Cognito**
   - `COGNITO_CLIENT_ID` (if exposed)

### How to Rotate Credentials

#### AWS Credentials
```bash
# 1. Create new IAM access keys in AWS Console
# 2. Update .env with new keys
# 3. Delete old access keys in AWS Console
# 4. Verify services still work
```

#### OpenAI API Key
```bash
# 1. Go to https://platform.openai.com/api-keys
# 2. Create new secret key
# 3. Update OPENAI_API_KEY in .env
# 4. Revoke old key
```

#### ElevenLabs API Key
```bash
# 1. Go to https://elevenlabs.io/app/settings/api-keys
# 2. Create new API key
# 3. Update ELEVENLABS_API_KEY in .env
# 4. Revoke old key
```

### Production Best Practices

For production deployments, use **AWS Secrets Manager**:

```python
# Example: Load secrets from AWS Secrets Manager
import boto3
import json

def get_secret(secret_name):
    client = boto3.client('secretsmanager', region_name='us-east-1')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# Usage
secrets = get_secret('vpbank-voice-agent/production')
openai_api_key = secrets['OPENAI_API_KEY']
```

### Verification

After rotation, verify `.env` is never committed:
```bash
git check-ignore .env  # Should output: .env
git log --all --full-history -- .env  # Should be empty
```

### Important Notes

- ✅ `.env` is properly gitignored
- ✅ `.env` was never committed to git history
- ⚠️ If you shared `.env` via Slack/email/etc., rotate those credentials
- ⚠️ Check AWS CloudTrail for unauthorized API usage
- ⚠️ Review OpenAI API usage logs for anomalies

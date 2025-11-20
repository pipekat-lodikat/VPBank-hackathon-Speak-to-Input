# Scripts

Deployment and utility scripts for VPBank Voice Agent.

## Available Scripts

### `start-dev.sh`

Starts all services in development mode (Browser Agent, Voice Bot, Frontend).

```bash
./scripts/start-dev.sh
```

**What it does:**
- Starts Browser Agent Service on port 7863
- Starts Voice Bot Service on port 7860
- Starts Frontend on port 5173
- Opens browser to http://localhost:5173

**Requirements:**
- Python 3.11+ with virtualenv activated
- Node.js 18+ installed
- `.env` file configured in project root

### `stop.sh`

Stops all running services by killing processes on ports 7860, 7863, and 5173.

```bash
./scripts/stop.sh
```

**What it does:**
- Finds processes using ports 7860, 7863, 5173
- Terminates those processes
- Cleans up background processes

### `deploy-ecs-fargate.sh`

Deploys the application to AWS ECS Fargate.

```bash
./scripts/deploy-ecs-fargate.sh
```

**What it does:**
- Builds Docker images
- Pushes images to AWS ECR
- Updates ECS task definitions
- Deploys to ECS cluster
- Configures ALB routing

**Requirements:**
- AWS CLI installed and configured
- Docker installed
- Terraform infrastructure already deployed
- AWS credentials with ECR and ECS permissions

## Usage Notes

1. **Always start services in order:**
   - Browser Agent first (port 7863)
   - Voice Bot second (port 7860)
   - Frontend last (port 5173)

2. **Make scripts executable:**
   ```bash
   chmod +x scripts/*.sh
   ```

3. **Run from project root:**
   ```bash
   ./scripts/start-dev.sh  # Correct
   cd scripts && ./start-dev.sh  # May cause issues
   ```

## Troubleshooting

- **"Port already in use"**: Run `./scripts/stop.sh` first
- **"Permission denied"**: Run `chmod +x scripts/*.sh`
- **Services won't start**: Check `.env` file exists and is configured

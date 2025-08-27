# Omnara Commands Reference - August 26, 2025

## Installation
```bash
pip install omnara
```

## Authentication Setup
```bash
# Method 1: Interactive authentication
omnara --auth

# Method 2: Direct API key
omnara --api-key "YOUR_API_KEY_HERE"

# Method 3: Environment variable
export OMNARA_API_KEY="YOUR_API_KEY_HERE"
```

## Webhook Server Commands (All Failed)

### Default Configuration
```bash
omnara.exe serve
```

### No-Tunnel Mode (Local Only)
```bash
# Default port 6662
omnara.exe --api-key "API_KEY" serve --no-tunnel

# Custom port
omnara.exe --api-key "API_KEY" serve --no-tunnel --port 8080
omnara.exe --api-key "API_KEY" serve --no-tunnel --port 3000
```

### Tunnel Mode (External Access)
```bash
# Default port with Cloudflare tunnel
omnara.exe --api-key "API_KEY" serve

# Custom port with tunnel
omnara.exe --api-key "API_KEY" serve --port 8080
```

### With Environment Variable
```bash
export OMNARA_API_KEY="API_KEY"
omnara.exe serve --no-tunnel --port 8080
```

### From Different Directory
```bash
cd /c/Users/AdamsLaptop/source/repos/Spiral_Minimal
omnara.exe serve --no-tunnel --port 8080
```

## Headless Mode Commands

### Basic Headless
```bash
omnara.exe headless
```

### With Custom Prompt
```bash
omnara.exe headless --prompt "Custom initial message"
```

### With Project Context
```bash
omnara.exe headless --prompt "I'm ready to assist with the Spiral Minimal project - a modular Python system for generating spiral staircases in AutoCAD. The project is production-ready with all 6 modules validated. Please let me know what you'd like to work on."
```

## Diagnostic Commands

### Check Installation
```bash
omnara.exe --version
omnara.exe --help
```

### Check Git Environment
```bash
git --version
where git
which git
echo $PATH
```

### Check Current Directory
```bash
pwd
ls -la
git status
```

## Working API Key
```
eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4ODliMDY2MC1jNzU1LTQ1OGYtYWRhNy1lZGYwNjIyYzQ1NzgiLCJpYXQiOjE3NTYyNDY4ODF9.xgqSLJiBkEHfFabyhb2bLQjgMLkPwfZJGC0fT9n9F1qhiZ4-9lQPTV4OOFNNEr66t5-Tgn2jWtzU6OG5xyIxlg
```

## Alternative Approaches to Try

### MCP Mode
```bash
omnara.exe mcp
omnara.exe mcp --git-diff
```

### Different Permission Modes
```bash
omnara.exe headless --permission-mode acceptEdits
omnara.exe headless --permission-mode bypassPermissions
omnara.exe headless --permission-mode plan
omnara.exe headless --dangerously-skip-permissions
```

### Specific Agent Types
```bash
omnara.exe --agent claude headless
omnara.exe --agent amp headless
```

## Webhook URLs for Testing

### Local (No-Tunnel)
- `http://localhost:6662/webhook` (default)
- `http://localhost:8080/webhook` (custom port)
- `http://localhost:3000/webhook`
- `http://localhost:5000/webhook`

### Tunnel (External)
- Provided dynamically by Cloudflare tunnel
- Format: `https://random-subdomain.trycloudflare.com/webhook`
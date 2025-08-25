# Network Security Options for Spiral Stair Generator

## Overview

This document outlines multiple approaches to restrict the Spiral Stair Generator to network-only usage, preventing unauthorized use outside your corporate environment. Each option provides different security levels and implementation complexity.

## Security Options

### **Option 1: Domain Controller Authentication (RECOMMENDED)**

**Security Level:** ⭐⭐⭐⭐⭐ (Highest)  
**Implementation Complexity:** ⭐⭐ (Low)  
**User Impact:** ⭐ (None - Transparent)  
**Bypass Difficulty:** ⭐⭐⭐⭐⭐ (Very Difficult)

**How it Works:**
- Validates that the machine is domain-joined to your specific corporate domain
- Checks environment variables like `%USERDNSDOMAIN%` or `%LOGONSERVER%`
- Requires active domain controller access to function

**Implementation:**
```batch
REM In Launch_Spiral_Stair_Embedded.bat
if "%USERDNSDOMAIN%"=="YOURCOMPANY.LOCAL" (
    echo [OK] Authorized domain detected
) else (
    echo ERROR: Application requires corporate domain access
    echo Contact IT support for assistance
    pause
    exit /b 1
)
```

**Pros:**
- Uses existing enterprise infrastructure
- Transparent to authorized users
- Extremely difficult to bypass without domain access
- Zero ongoing maintenance

**Cons:**
- Won't work for non-domain machines
- Requires network connectivity to domain controller

---

### **Option 2: Network Share Path Validation**

**Security Level:** ⭐⭐⭐⭐ (High)  
**Implementation Complexity:** ⭐ (Very Low)  
**User Impact:** ⭐ (Minimal - Must run from network)  
**Bypass Difficulty:** ⭐⭐⭐ (Medium)

**How it Works:**
- Validates that the executable is running from an authorized network UNC path
- Blocks execution if copied to local drives or external locations
- Requires access to corporate network shares

**Implementation:**
```batch
REM Check if running from authorized network location
set SCRIPT_DIR=%~dp0
echo %SCRIPT_DIR% | findstr /C:"\\YOURSERVER\SpiralStair\" >nul
if errorlevel 1 (
    echo ERROR: Application must run from authorized network location
    echo Expected: \\YOURSERVER\SpiralStair\
    echo Current: %SCRIPT_DIR%
    pause
    exit /b 1
)
```

**Pros:**
- Simple to implement
- Prevents local copying and distribution
- Uses existing network infrastructure
- Clear error messages for troubleshooting

**Cons:**
- Can be bypassed by copying entire folder structure
- Requires consistent network path naming

---

### **Option 3: IP Address Range Validation**

**Security Level:** ⭐⭐⭐ (Medium)  
**Implementation Complexity:** ⭐⭐⭐ (Medium)  
**User Impact:** ⭐ (None for office users)  
**Bypass Difficulty:** ⭐⭐⭐ (Medium)

**How it Works:**
- Validates that the machine's IP address falls within authorized corporate ranges
- Blocks execution from external networks, home offices, or public internet
- Network-topology dependent security

**Implementation:**
```python
# In security_validation.py
import socket
import ipaddress

def validate_ip_range():
    """Check if machine IP is in authorized corporate ranges."""
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        ip = ipaddress.ip_address(local_ip)
        
        # Define authorized corporate IP ranges
        authorized_ranges = [
            ipaddress.ip_network('192.168.1.0/24'),  # Corporate LAN
            ipaddress.ip_network('10.0.0.0/8'),      # Corporate WAN
            ipaddress.ip_network('172.16.0.0/12')    # Corporate VPN
        ]
        
        for network in authorized_ranges:
            if ip in network:
                return True, f"Authorized IP: {local_ip}"
        
        return False, f"Unauthorized IP range: {local_ip}"
    
    except Exception as e:
        return False, f"IP validation error: {str(e)}"
```

**Pros:**
- Network-aware security
- Blocks remote/home usage automatically
- Can work with VPN configurations
- Flexible range definitions

**Cons:**
- Can be bypassed with VPN or network spoofing
- May block legitimate remote workers
- Requires network topology knowledge

---

### **Option 4: Internal License Server Validation**

**Security Level:** ⭐⭐⭐⭐⭐ (Highest)  
**Implementation Complexity:** ⭐⭐⭐⭐ (High)  
**User Impact:** ⭐⭐ (Slight startup delay)  
**Bypass Difficulty:** ⭐⭐⭐⭐⭐ (Very Difficult)

**How it Works:**
- Requires connection to internal license validation server
- Application requests authorization token on startup
- Server validates request and provides temporary license
- Fails if unable to contact internal server

**Implementation:**
```python
# Simple license server (license_server.py)
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime, timedelta

class LicenseHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/validate':
            # Generate temporary license token
            token = {
                'authorized': True,
                'expires': (datetime.now() + timedelta(hours=8)).isoformat(),
                'machine': self.client_address[0]
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(token).encode())
        else:
            self.send_response(404)

# Run on internal server: HTTPServer(('', 8080), LicenseHandler).serve_forever()
```

**Pros:**
- Professional licensing approach
- Centralized control and monitoring
- Scalable to multiple applications
- Real-time authorization control
- Detailed usage logging

**Cons:**
- Requires dedicated server infrastructure
- More complex setup and maintenance
- Network dependency for startup

---

### **Option 5: Machine/User Whitelist**

**Security Level:** ⭐⭐⭐⭐ (High)  
**Implementation Complexity:** ⭐⭐⭐⭐⭐ (Very High)  
**User Impact:** ⭐⭐⭐⭐ (Requires IT setup per user)  
**Bypass Difficulty:** ⭐⭐⭐⭐ (High)

**How it Works:**
- Maintains approved machine names or user accounts in encrypted whitelist
- Administrative setup required for each authorized user/machine
- Can use registry entries or encrypted configuration files

**Implementation:**
```python
# In security_validation.py
import os
import hashlib
import hmac

def validate_machine_whitelist():
    """Check if current machine/user is on approved whitelist."""
    machine_name = os.environ.get('COMPUTERNAME', '')
    username = os.environ.get('USERNAME', '')
    
    # Load encrypted whitelist (simplified example)
    authorized_machines = [
        'WORKSTATION-001', 'WORKSTATION-002', 'CAD-STATION-01'
    ]
    authorized_users = [
        'john.doe', 'jane.smith', 'cad.operator'
    ]
    
    if machine_name in authorized_machines or username in authorized_users:
        return True, f"Authorized access: {username}@{machine_name}"
    
    return False, f"Unauthorized machine/user: {username}@{machine_name}"
```

**Pros:**
- Granular access control
- Individual user/machine authorization
- Strong security when properly implemented
- Audit trail of authorized users

**Cons:**
- High maintenance overhead
- Requires IT involvement for each user
- Complex encrypted whitelist management

---

## Recommended Implementation: Dual-Layer Security

### **Primary Approach: Domain + Network Share Validation**

Combine **Option 1** (Domain Authentication) with **Option 2** (Network Share Validation) for maximum security with minimal complexity:

```batch
@echo off
REM Spiral Stair Generator - Secure Network Launcher
echo ====================================================
echo    Spiral Stair Generator - Secure Network Version
echo ====================================================

REM Layer 1: Domain Authentication
if "%USERDNSDOMAIN%"=="YOURCOMPANY.LOCAL" (
    echo [OK] Corporate domain access verified
) else (
    echo ERROR: This application requires corporate domain access
    echo Contact your IT administrator for assistance
    echo Domain detected: %USERDNSDOMAIN%
    pause
    exit /b 1
)

REM Layer 2: Network Share Validation
set SCRIPT_DIR=%~dp0
echo %SCRIPT_DIR% | findstr /C:"\\YOURSERVER\Applications\SpiralStair\" >nul
if errorlevel 1 (
    echo ERROR: Application must run from authorized network location
    echo Expected: \\YOURSERVER\Applications\SpiralStair\
    echo Current: %SCRIPT_DIR%
    echo.
    echo This prevents unauthorized copying and distribution
    pause
    exit /b 1
)

echo [OK] Network path validation passed
echo [OK] All security checks completed
echo.

REM Continue with normal application launch...
```

---

## Implementation Plan

### Phase 1: Basic Security (Immediate)
1. **Update Launcher Script** - Add domain and network path validation to `Launch_Spiral_Stair_Embedded.bat`
2. **Test Validation Logic** - Verify security checks work correctly on authorized machines
3. **Deploy to Network Share** - Place secure version on corporate network location

### Phase 2: Enhanced Security (Future)
1. **Add Python Security Module** - Create `security_validation.py` with comprehensive checks
2. **Implement Logging** - Add audit trail for all usage attempts
3. **Create License Server** - Optional internal licensing system for advanced control

### Phase 3: Enterprise Integration (Optional)
1. **Active Directory Integration** - Use AD groups for authorization
2. **Centralized Configuration** - Network-based security policy management
3. **Usage Analytics** - Detailed reporting on application usage patterns

---

## Security Benefits Summary

| Feature | Domain Auth | Network Share | IP Range | License Server | Whitelist |
|---------|-------------|---------------|----------|----------------|-----------|
| **Prevents Home Use** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Prevents Copying** | ❌ | ✅ | ❌ | ✅ | ❌ |
| **Enterprise Integration** | ✅ | ✅ | ❌ | ✅ | ⚠️ |
| **Zero User Impact** | ✅ | ✅ | ✅ | ⚠️ | ❌ |
| **Low Maintenance** | ✅ | ✅ | ⚠️ | ❌ | ❌ |
| **Bypass Difficulty** | Very High | Medium | Medium | Very High | High |

---

## Deployment Considerations

### **Network Requirements:**
- Corporate domain controller access (for domain validation)
- Authorized network share location (for path validation)
- Consistent UNC path naming across organization

### **User Impact:**
- **Authorized Users:** No change in functionality or user experience
- **Unauthorized Users:** Clear error messages explaining access restrictions
- **IT Support:** Simple troubleshooting with descriptive error messages

### **Maintenance:**
- **Domain Method:** Zero ongoing maintenance
- **Network Share:** Minimal - only if network topology changes
- **Combined Approach:** Leverages existing infrastructure

---

## Error Messages for Users

### Domain Validation Failure:
```
ERROR: Corporate domain access required

This application is licensed for use on YOURCOMPANY corporate network only.

Contact your IT administrator if you believe this is an error.
Current domain: [detected domain or "Not domain-joined"]
Required domain: YOURCOMPANY.LOCAL
```

### Network Path Validation Failure:
```
ERROR: Unauthorized application location

This application must run from the authorized network location to prevent 
unauthorized copying and ensure proper licensing compliance.

Expected location: \\YOURSERVER\Applications\SpiralStair\
Current location: [detected path]

Please access the application from the corporate network share or contact 
your IT administrator for assistance.
```

---

This comprehensive security approach ensures your Spiral Stair Generator remains protected while providing a professional, enterprise-ready deployment solution.
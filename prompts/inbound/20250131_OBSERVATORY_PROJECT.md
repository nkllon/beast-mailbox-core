# Request to beast-mailbox-core: Observatory Infrastructure Project

**Date:** 2025-01-31  
**Priority:** High  
**Status:** Planning

---

## Objective

Create a reusable "Observatory" infrastructure project that:
1. Manages Prometheus, Grafana, Pushgateway stack
2. Can be deployed locally (Herbert) and remotely (Vonnegut)
3. Is installable via PyPI (`pip install beast-observatory`)
4. Goes through SonarCloud quality gates
5. Can be tested locally before deployment

---

## Context

**Current Situation:**
- Observatory instance runs on Vonnegut
- Contains: Prometheus, Grafana, Pushgateway, and related services
- Managed via Docker containers
- Not currently documented or reusable
- Need to capture full configuration for reproducibility

**Goal:**
- Create a reusable Observatory project
- Duplicate service stack locally on Herbert for testing
- Make it installable and deployable
- Enable local testing before deployment
- Support both local and remote deployment

---

## Requirements

### 1. Discovery Phase

**Task: Interrogate Vonnegut to capture:**
- [ ] All running Docker containers
- [ ] Docker Compose configuration (if exists)
- [ ] Container configurations (environment variables, volumes, networks)
- [ ] Port mappings
- [ ] Volume mounts
- [ ] Network configurations
- [ ] Service dependencies
- [ ] Configuration files (prometheus.yml, grafana.ini, etc.)
- [ ] Initialization scripts
- [ ] Data persistence locations

**Output:** Complete inventory of Vonnegut observatory stack

---

### 2. Local Duplication

**Task: Replicate stack on Herbert:**
- [ ] Create Docker Compose configuration matching Vonnegut
- [ ] Capture all service configurations
- [ ] Set up volumes and networks
- [ ] Configure environment variables
- [ ] Document differences (if any needed for local vs remote)

**Output:** Local observatory stack that matches Vonnegut

---

### 3. Project Structure

**Task: Create Observatory project:**
- [ ] Project name: `beast-observatory` (or similar)
- [ ] Python package structure
- [ ] CLI tools for deployment/management
- [ ] Configuration management
- [ ] Docker Compose templates
- [ ] Documentation

**Project Structure:**
```
beast-observatory/
├── src/
│   └── beast_observatory/
│       ├── __init__.py
│       ├── cli.py          # CLI commands
│       ├── config.py       # Configuration management
│       ├── docker.py       # Docker/Docker Compose management
│       ├── prometheus.py   # Prometheus configuration
│       ├── grafana.py      # Grafana configuration
│       └── pushgateway.py  # Pushgateway configuration
├── docker/
│   ├── docker-compose.yml
│   ├── prometheus/
│   │   └── prometheus.yml
│   ├── grafana/
│   │   └── grafana.ini
│   └── pushgateway/
│       └── config/
├── templates/
│   └── docker-compose.yml.j2  # Jinja2 template
├── tests/
│   └── test_*.py
├── docs/
│   ├── DISCOVERY.md        # Vonnegut discovery results
│   ├── LOCAL_SETUP.md      # Herbert local setup
│   └── DEPLOYMENT.md       # Deployment guide
├── pyproject.toml
├── README.md
└── CHANGELOG.md
```

---

### 4. Features

**CLI Commands:**
- `observatory up` - Start all services
- `observatory down` - Stop all services
- `observatory status` - Check service status
- `observatory logs` - View service logs
- `observatory config` - Manage configuration
- `observatory discover` - Discover running stack (Vonnegut)
- `observatory export` - Export configuration
- `observatory import` - Import configuration

**Configuration Management:**
- Environment-based configuration (local, remote)
- Configurable ports, volumes, networks
- Service enable/disable flags
- Data persistence configuration

---

### 5. Quality Standards

**Follow beast-mailbox-core standards:**
- ✅ 90%+ code coverage
- ✅ SonarCloud Quality Gate PASSED
- ✅ Zero bugs, vulnerabilities, code smells
- ✅ Comprehensive documentation
- ✅ Integration tests
- ✅ Local testing before deployment

---

### 6. Deployment Pipeline

**CI/CD Requirements:**
- [ ] GitHub Actions workflow
- [ ] SonarCloud analysis
- [ ] Test suite execution
- [ ] PyPI publishing
- [ ] Version management

**Installation:**
```bash
pip install beast-observatory
```

**Usage:**
```bash
# Local deployment
observatory up --environment local

# Remote deployment
observatory up --environment remote --host vonnegut
```

---

## Discovery Script

**Create script to interrogate Vonnegut:**

```bash
#!/bin/bash
# scripts/discover_vonnegut.sh
# Interrogate Vonnegut to capture observatory stack configuration

HOST="${VONNEGUT_HOST:-vonnegut}"
SSH_USER="${SSH_USER:-root}"

echo "🔍 Discovering Observatory stack on $HOST..."

# 1. List all running containers
ssh $SSH_USER@$HOST "docker ps --format '{{.Names}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}'"

# 2. Get Docker Compose files
ssh $SSH_USER@$HOST "find / -name docker-compose.yml 2>/dev/null"

# 3. Get container configurations
ssh $SSH_USER@$HOST "docker inspect \$(docker ps -q) | jq '.[] | {Name: .Name, Image: .Config.Image, Env: .Config.Env, Mounts: .Mounts, Networks: .NetworkSettings.Networks}'"

# 4. Get volumes
ssh $SSH_USER@$HOST "docker volume ls"

# 5. Get networks
ssh $SSH_USER@$HOST "docker network ls"

# 6. Get configuration files
# Prometheus
ssh $SSH_USER@$HOST "docker exec prometheus cat /etc/prometheus/prometheus.yml"

# Grafana
ssh $SSH_USER@$HOST "docker exec grafana cat /etc/grafana/grafana.ini"

# ... etc
```

---

## Implementation Plan

### Phase 1: Discovery (Current)
1. Create discovery script
2. Run against Vonnegut
3. Capture all configurations
4. Document findings

### Phase 2: Local Duplication
1. Create Docker Compose matching Vonnegut
2. Set up local volumes and networks
3. Configure for Herbert environment
4. Test local boot

### Phase 3: Project Creation
1. Create Python project structure
2. Implement CLI tools
3. Implement configuration management
4. Add Docker Compose management

### Phase 4: Testing
1. Write test suite
2. Test local deployment
3. Test configuration management
4. Integration tests

### Phase 5: CI/CD
1. Set up GitHub Actions
2. Configure SonarCloud
3. Set up PyPI publishing
4. Version management

### Phase 6: Deployment
1. Package for PyPI
2. Publish to PyPI
3. Update documentation
4. Release announcement

---

## Success Criteria

- [ ] Full Vonnegut stack captured and documented
- [ ] Local Herbert stack matches Vonnegut
- [ ] Local testing works
- [ ] Project installable via `pip install beast-observatory`
- [ ] All services boot locally
- [ ] SonarCloud Quality Gate PASSED
- [ ] 90%+ code coverage
- [ ] Comprehensive documentation
- [ ] Ready for deployment

---

## Next Steps

1. **Create discovery script** (`scripts/discover_vonnegut.sh`)
2. **Run discovery** against Vonnegut
3. **Capture configurations** to `docs/discovery/`
4. **Create project structure** for `beast-observatory`
5. **Build Docker Compose** matching Vonnegut
6. **Test locally** on Herbert

---

**Status:** Ready to begin Phase 1 - Discovery


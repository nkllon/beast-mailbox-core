# Beast Observatory - Working Directory

**Status:** Development in Progress  
**Target Repo:** `github.com/nkllon/beast-observatory`  
**Current Phase:** Discovery → Local Duplication → Package Creation

---

## Purpose

This directory contains work-in-progress for the Observatory infrastructure project. Once working on Herbert (localhost Docker), it will be split into a separate repository.

**Final Goal:** `pip install beast-observatory` installable package

---

## Directory Structure

```
observatory/
├── README.md              # This file
├── docker/                # Docker Compose and service configs
│   ├── docker-compose.yml
│   ├── prometheus/
│   ├── grafana/
│   └── pushgateway/
├── configs/              # Service configurations
│   ├── prometheus.yml
│   ├── grafana.ini
│   └── pushgateway/
├── scripts/              # Management scripts
│   ├── discover_vonnegut.sh
│   ├── setup_local.sh
│   └── test_stack.sh
├── docs/                 # Documentation
│   ├── discovery/        # Vonnegut discovery results
│   ├── local_setup.md    # Herbert local setup guide
│   └── deployment.md     # Deployment guide
└── src/                  # Future Python package (when split)
    └── beast_observatory/
```

---

## PDCA Progress

### PLAN ✅
- [x] Create working directory structure
- [x] Discovery script ready
- [x] Architecture designed

### DO ✅
- [x] Create Docker Compose matching standard observability stack
- [x] Extract service configs
- [x] Set up local volumes/networks
- [x] Boot stack locally
- [x] Verify all services working
- [x] Create sync service (periodic SonarCloud → Prometheus)
- [x] Implement sync service (SonarCloud API → Pushgateway)
- [x] Fix URL encoding and metrics format issues
- [x] Design mailbox integration (optional decoupling)

### CHECK ✅
- [x] Test local boot
- [x] Verify service connectivity
- [x] Test metric push
- [x] Verify Prometheus scraping
- [x] Test sync service end-to-end (SonarCloud → Pushgateway)
- [x] Verify metrics visible in Pushgateway

### ACT/ADJUST ✅
- [x] Fix docker-compose version warning
- [x] Fix sync service 400 error (URL encoding)
- [x] Fix metrics format (non-numeric values, label escaping)
- [x] Verify full integration
- [x] Document architecture

---

## Quick Start

### 1. Discovery Phase

```bash
cd observatory
export VONNEGUT_HOST="vonnegut"  # or IP
export SSH_USER="root"  # or your user
./scripts/discover_vonnegut.sh
```

Results saved to: `docs/discovery/`

### 2. Local Duplication

```bash
# Review discovery results
cat docs/discovery/SUMMARY.md

# Create Docker Compose (after discovery)
# Edit docker/docker-compose.yml based on discovery

# Boot locally
cd docker
docker compose up -d
```

### 3. Verification

```bash
# Check services
docker compose ps

# Test Prometheus
curl http://localhost:9090/api/v1/status/config

# Test Grafana
curl http://localhost:3000/api/health

# Test Pushgateway
curl http://localhost:9091/metrics
```

---

## Next Steps

1. **Run discovery** against Vonnegut
2. **Review results** and extract configurations
3. **Create Docker Compose** matching Vonnegut
4. **Boot locally** on Herbert
5. **Test and verify** all services
6. **Package** for separate repo when working

---

## Migration to Separate Repo

When ready to split:

1. Create new repo: `github.com/nkllon/beast-observatory`
2. Move `observatory/` contents to new repo root
3. Create Python package structure
4. Add CI/CD (SonarCloud, PyPI)
5. Test installation: `pip install beast-observatory`

---

**Status:** Discovery phase starting


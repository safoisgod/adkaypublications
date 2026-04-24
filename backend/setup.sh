#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Publishing House — Local Development Setup Script
# Run once after cloning the repository.
# Usage: bash setup.sh
# ─────────────────────────────────────────────────────────────────────────────

set -e  # Exit on any error

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log()    { echo -e "${GREEN}✓ $1${NC}"; }
warn()   { echo -e "${YELLOW}⚠ $1${NC}"; }
error()  { echo -e "${RED}✗ $1${NC}"; exit 1; }
section(){ echo -e "\n${YELLOW}── $1 ──────────────────────${NC}"; }

section "A-D Kay Publication — Setup"

# ── Python check ───────────────────────────────────────────────────────────
python3 --version >/dev/null 2>&1 || error "Python 3.10+ is required."
log "Python found: $(python3 --version)"

# ── Virtual environment ────────────────────────────────────────────────────
section "Virtual Environment"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    log "Virtual environment created."
else
    warn "Virtual environment already exists — skipping."
fi

source venv/bin/activate
log "Virtual environment activated."

# ── Dependencies ───────────────────────────────────────────────────────────
section "Installing Dependencies"
pip install --upgrade pip --quiet
pip install -r requirements/development.txt --quiet
log "Dependencies installed."

# ── Environment file ───────────────────────────────────────────────────────
section "Environment Configuration"
if [ ! -f ".env" ]; then
    cp .env.example .env
    log ".env file created from .env.example"
    warn "Please edit .env and set your DB credentials before continuing."
    echo ""
    echo "  Required settings:"
    echo "    DB_NAME, DB_USER, DB_PASSWORD"
    echo "    SECRET_KEY"
    echo ""
    read -p "Press ENTER when .env is configured..." _
else
    warn ".env already exists — skipping."
fi

# ── Database ────────────────────────────────────────────────────────────────
section "Database Setup"
python manage.py migrate --settings=config.settings.development
log "Migrations applied."

# ── Seed data ───────────────────────────────────────────────────────────────
section "Sample Data"
read -p "Seed the database with sample data? [Y/n]: " seed_answer
if [ "$seed_answer" != "n" ] && [ "$seed_answer" != "N" ]; then
    python manage.py seed_data --settings=config.settings.development
    log "Sample data loaded."
fi

# ── Static files ────────────────────────────────────────────────────────────
section "Static Files"
python manage.py collectstatic --noinput --settings=config.settings.development --quiet
log "Static files collected."

# ── Done ────────────────────────────────────────────────────────────────────
section "Setup Complete"
echo ""
echo -e "${GREEN}┌─────────────────────────────────────────────┐${NC}"
echo -e "${GREEN}│  Publishing House API is ready!             │${NC}"
echo -e "${GREEN}│                                             │${NC}"
echo -e "${GREEN}│  Start server:                              │${NC}"
echo -e "${GREEN}│    python manage.py runserver               │${NC}"
echo -e "${GREEN}│                                             │${NC}"
echo -e "${GREEN}│  API:      http://localhost:8000/api/v1/    │${NC}"
echo -e "${GREEN}│  Admin:    http://localhost:8000/admin/     │${NC}"
echo -e "${GREEN}│  API Docs: http://localhost:8000/api/docs/  │${NC}"
echo -e "${GREEN}│                                             │${NC}"
echo -e "${GREEN}│  Admin credentials (if seeded):             │${NC}"
echo -e "${GREEN}│    Email:    admin@publishinghouse.com      │${NC}"
echo -e "${GREEN}│    Password: Admin1234!                     │${NC}"
echo -e "${GREEN}└─────────────────────────────────────────────┘${NC}"
echo ""

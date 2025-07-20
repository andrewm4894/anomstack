#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Function to print colored output
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# Function to get user confirmation
confirm() {
    local message="$1"
    local default="${2:-n}"
    
    if [[ "$default" == "y" ]]; then
        prompt="[Y/n]"
    else
        prompt="[y/N]"
    fi
    
    read -p "$(echo -e "${YELLOW}$message $prompt${NC} ")" -n 1 -r
    echo
    
    if [[ "$default" == "y" ]]; then
        [[ $REPLY =~ ^[Nn]$ ]] && return 1 || return 0
    else
        [[ $REPLY =~ ^[Yy]$ ]] && return 0 || return 1
    fi
}

# Function to show data sizes
show_data_sizes() {
    print_info "Current data usage:"
    
    if [ -d "$PROJECT_ROOT/tmp" ] && [ "$(ls -A "$PROJECT_ROOT/tmp" 2>/dev/null)" ]; then
        echo -e "  📁 tmp/ directory: $(du -sh "$PROJECT_ROOT/tmp" 2>/dev/null | cut -f1 || echo "empty")"
    fi
    
    if [ -d "$PROJECT_ROOT/dagster_home/storage" ] && [ "$(ls -A "$PROJECT_ROOT/dagster_home/storage" 2>/dev/null)" ]; then
        echo -e "  🗄️  dagster_home/storage: $(du -sh "$PROJECT_ROOT/dagster_home/storage" 2>/dev/null | cut -f1 || echo "empty")"
    fi
    
    if [ -d "$PROJECT_ROOT/dagster_home/history" ] && [ "$(ls -A "$PROJECT_ROOT/dagster_home/history" 2>/dev/null)" ]; then
        echo -e "  📚 dagster_home/history: $(du -sh "$PROJECT_ROOT/dagster_home/history" 2>/dev/null | cut -f1 || echo "empty")"
    fi
    
    # Show Docker volumes
    volumes=$(docker volume ls -q | grep -E "anomstack" 2>/dev/null || echo "")
    if [ -n "$volumes" ]; then
        print_info "Docker volumes:"
        echo "$volumes" | while read -r volume; do
            echo -e "  🐳 $volume"
        done
    fi
    echo
}

# Function to show what will be preserved
show_preserved() {
    print_success "What will be PRESERVED:"
    echo -e "  💾 Source code (anomstack/, dashboard/, metrics/)"
    echo -e "  ⚙️  Configuration files (.env, docker-compose files)"
    echo -e "  🛠️  Git repository and history"
    echo
}

# Reset level functions
gentle_reset() {
    print_info "🔄 GENTLE RESET: Rebuilding containers with fresh images"
    show_preserved
    
    if confirm "Proceed with gentle reset?"; then
        cd "$PROJECT_ROOT"
        print_info "Stopping containers..."
        make docker-down
        
        print_info "Building fresh images..."
        make docker-dev-build --no-cache
        
        print_info "Starting containers..."
        make docker-dev
        
        print_success "Gentle reset complete! 🎉"
    else
        print_info "Reset cancelled."
    fi
}

medium_reset() {
    print_info "🧹 MEDIUM RESET: Remove containers and networks, keep data volumes"
    
    show_data_sizes
    show_preserved
    print_success "Docker volumes will be PRESERVED (your data is safe)"
    echo
    
    if confirm "Proceed with medium reset?"; then
        cd "$PROJECT_ROOT"
        print_info "Removing containers and networks..."
        make docker-rm || docker-compose down --remove-orphans
        
        print_info "Building fresh images..."
        make docker-dev-build
        
        print_info "Starting fresh containers..."
        make docker-dev
        
        print_success "Medium reset complete! 🎉"
    else
        print_info "Reset cancelled."
    fi
}

nuclear_reset() {
    print_info "☢️  NUCLEAR RESET: Remove containers, volumes, and local data"
    
    show_data_sizes
    show_preserved
    print_error "⚠️  ALL DATA WILL BE LOST:"
    echo -e "  🗑️  All Docker volumes (metrics, database)"
    echo -e "  🗑️  All local run data (tmp/, storage/, history/)"
    echo -e "  🗑️  All Dagster run history and logs"
    echo
    
    if confirm "Are you absolutely sure you want to delete ALL data?" "n"; then
        if confirm "This cannot be undone. Really proceed?" "n"; then
            cd "$PROJECT_ROOT"
            
            print_info "Stopping and removing containers with volumes..."
            make docker-prune || {
                docker-compose down -v --remove-orphans
                docker system prune -f
            }
            
            print_info "Removing local data directories..."
            [ -d "tmp" ] && rm -rf tmp/* && print_success "Cleared tmp/ directory"
            [ -d "dagster_home/storage" ] && rm -rf dagster_home/storage/* && print_success "Cleared dagster storage"
            [ -d "dagster_home/history" ] && rm -rf dagster_home/history/* && print_success "Cleared dagster history"
            [ -d "dagster_home/.logs_queue" ] && rm -rf dagster_home/.logs_queue/* && print_success "Cleared logs queue"
            [ -d "dagster_home/logs" ] && rm -rf dagster_home/logs/* && print_success "Cleared logs"
            [ -d "dagster_home/.nux" ] && rm -rf dagster_home/.nux/* && print_success "Cleared nux cache"
            [ -d "dagster_home/.telemetry" ] && rm -rf dagster_home/.telemetry/* && print_success "Cleared telemetry"
            
            print_info "Building fresh images..."
            make docker-dev-build
            
            print_info "Starting completely fresh setup..."
            make docker-dev
            
            print_success "Nuclear reset complete! Everything is fresh and clean 🎉"
            print_info "Your setup is now like a brand new installation"
        else
            print_info "Reset cancelled."
        fi
    else
        print_info "Reset cancelled."
    fi
}

full_nuclear_reset() {
    print_info "💥 FULL NUCLEAR RESET: Everything + Docker system cleanup"
    
    show_data_sizes
    show_preserved
    print_error "⚠️  EVERYTHING DOCKER WILL BE CLEANED:"
    echo -e "  🗑️  All data (same as nuclear reset)"
    echo -e "  🗑️  ALL unused Docker images, networks, build cache"
    echo -e "  🗑️  Docker system prune (frees maximum disk space)"
    echo
    
    if confirm "Are you absolutely sure? This is the most destructive option!" "n"; then
        if confirm "This will clean up ALL Docker resources. Really proceed?" "n"; then
            cd "$PROJECT_ROOT"
            
            # Do nuclear reset first
            print_info "Performing nuclear data cleanup..."
            make docker-prune || {
                docker-compose down -v --remove-orphans
                docker system prune -f
            }
            
            print_info "Removing local data directories..."
            [ -d "tmp" ] && rm -rf tmp/* && print_success "Cleared tmp/ directory"
            [ -d "dagster_home/storage" ] && rm -rf dagster_home/storage/* && print_success "Cleared dagster storage"
            [ -d "dagster_home/history" ] && rm -rf dagster_home/history/* && print_success "Cleared dagster history"
            [ -d "dagster_home/.logs_queue" ] && rm -rf dagster_home/.logs_queue/* && print_success "Cleared logs queue"
            [ -d "dagster_home/logs" ] && rm -rf dagster_home/logs/* && print_success "Cleared logs"
            
            print_info "Performing full Docker system cleanup..."
            docker system prune -a -f
            
            print_info "Building completely fresh images..."
            make docker-dev-build
            
            print_info "Starting pristine setup..."
            make docker-dev
            
            print_success "Full nuclear reset complete! Maximum cleanup achieved 🎉"
            print_info "You've reclaimed maximum disk space and have a pristine setup"
        else
            print_info "Reset cancelled."
        fi
    else
        print_info "Reset cancelled."
    fi
}

# Main script
usage() {
    echo "Usage: $0 [gentle|medium|nuclear|full-nuclear]"
    echo
    echo "Reset levels:"
    echo "  gentle      - Rebuild containers with fresh images (safest)"
    echo "  medium      - Remove containers, keep data volumes"
    echo "  nuclear     - Remove everything including local data"
    echo "  full-nuclear - Nuclear + full Docker system cleanup"
    echo
    echo "If no argument provided, interactive mode will guide you."
}

main() {
    cd "$PROJECT_ROOT"
    
    print_info "🐳 Anomstack Docker Reset Tool"
    echo
    
    case "${1:-}" in
        "gentle")
            gentle_reset
            ;;
        "medium")
            medium_reset
            ;;
        "nuclear")
            nuclear_reset
            ;;
        "full-nuclear")
            full_nuclear_reset
            ;;
        "-h"|"--help")
            usage
            ;;
        "")
            # Interactive mode
            print_info "Select reset level:"
            echo "1) 🔄 Gentle - Rebuild containers (safest)"
            echo "2) 🧹 Medium - Remove containers, keep data"
            echo "3) ☢️  Nuclear - Remove all data and containers"
            echo "4) 💥 Full Nuclear - Nuclear + full Docker cleanup"
            echo "5) ❌ Cancel"
            echo
            
            read -p "Choose option [1-5]: " -n 1 -r choice
            echo
            
            case $choice in
                1) gentle_reset ;;
                2) medium_reset ;;
                3) nuclear_reset ;;
                4) full_nuclear_reset ;;
                5|*) print_info "Cancelled." ;;
            esac
            ;;
        *)
            print_error "Invalid option: $1"
            usage
            exit 1
            ;;
    esac
}

main "$@" 
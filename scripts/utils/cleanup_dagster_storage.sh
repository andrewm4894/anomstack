#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Function to analyze current storage
analyze_storage() {
    print_info "📊 Analyzing Dagster storage usage..."
    
    cd "$PROJECT_ROOT"
    
    # Count run directories
    run_dirs=0
    if [ -d "tmp" ]; then
        run_dirs=$(find tmp/ -maxdepth 1 -type d -name "*-*-*-*-*" 2>/dev/null | wc -l | tr -d ' ')
    fi
    
    # Calculate sizes
    tmp_size="0B"
    storage_size="0B"
    history_size="0B"
    
    [ -d "tmp" ] && tmp_size=$(du -sh tmp/ 2>/dev/null | cut -f1 || echo "0B")
    [ -d "dagster_home/storage" ] && storage_size=$(du -sh dagster_home/storage/ 2>/dev/null | cut -f1 || echo "0B")
    [ -d "dagster_home/history" ] && history_size=$(du -sh dagster_home/history/ 2>/dev/null | cut -f1 || echo "0B")
    
    print_info "Current Dagster storage usage:"
    echo -e "  🗂️  Run directories: ${run_dirs}"
    echo -e "  📁 tmp/ directory: ${tmp_size}"
    echo -e "  🗄️  dagster_home/storage: ${storage_size}"
    echo -e "  📚 dagster_home/history: ${history_size}"
    
    # Estimate potential savings
    if [ "$run_dirs" -gt 1000 ]; then
        print_warning "🚨 EXCESSIVE RUN DIRECTORIES DETECTED!"
        print_warning "You have ${run_dirs} run directories - this will cause disk space issues!"
        echo
    fi
}

# Function to show cleanup options
show_cleanup_options() {
    print_info "🧹 Cleanup Options Available:"
    echo
    echo "1. 🔧 Minimal Cleanup - Remove old compute logs only"
    echo "   • Cleans compute logs older than 7 days"
    echo "   • Preserves all run metadata and artifacts"
    echo "   • Safe for production use"
    echo
    echo "2. 🧹 Standard Cleanup - Remove old runs and logs"
    echo "   • Removes runs older than 30 days"
    echo "   • Cleans associated compute logs and artifacts"
    echo "   • Keeps recent runs for debugging"
    echo
    echo "3. 🔥 Aggressive Cleanup - Remove most old data"
    echo "   • Removes runs older than 7 days"
    echo "   • Aggressive log cleanup"
    echo "   • Only keeps very recent data"
    echo
    echo "4. ☢️  Nuclear Cleanup - Remove almost everything"
    echo "   • Removes all but the last 24 hours of runs"
    echo "   • Clears most storage directories"
    echo "   • Use only if disk space is critical"
    echo
    echo "5. 🛠️  CLI-based cleanup using Dagster commands"
    echo "   • Uses built-in 'dagster run wipe' commands"
    echo "   • Most thorough database cleanup"
    echo "   • Recommended for severe cases"
}

# Cleanup functions
cleanup_minimal() {
    print_info "🔧 Performing minimal cleanup..."
    
    cd "$PROJECT_ROOT"
    
    # Clean old compute logs (older than 7 days)
    if [ -d "tmp" ]; then
        print_info "Cleaning compute logs older than 7 days..."
        find tmp/ -name "*.log" -mtime +7 -delete 2>/dev/null || true
        find tmp/ -name "compute_logs" -type d -exec find {} -name "*.log" -mtime +7 -delete \; 2>/dev/null || true
    fi
    
    # Clean old log files in dagster_home
    if [ -d "dagster_home/logs" ]; then
        find dagster_home/logs/ -name "*.log" -mtime +7 -delete 2>/dev/null || true
    fi
    
    print_success "Minimal cleanup completed"
}

cleanup_standard() {
    print_info "🧹 Performing standard cleanup..."
    
    cd "$PROJECT_ROOT"
    
    if [ -d "tmp" ]; then
        # Remove run directories older than 30 days
        print_info "Removing run directories older than 30 days..."
        find tmp/ -maxdepth 1 -type d -name "*-*-*-*-*" -mtime +30 -exec rm -rf {} \; 2>/dev/null || true
        
        # Clean compute logs older than 14 days
        find tmp/ -name "*.log" -mtime +14 -delete 2>/dev/null || true
        find tmp/ -name "compute_logs" -type d -exec find {} -name "*.log" -mtime +14 -delete \; 2>/dev/null || true
    fi
    
    # Clean old storage files
    if [ -d "dagster_home/storage" ]; then
        find dagster_home/storage/ -type f -mtime +30 -delete 2>/dev/null || true
    fi
    
    print_success "Standard cleanup completed"
}

cleanup_aggressive() {
    print_info "🔥 Performing aggressive cleanup..."
    
    cd "$PROJECT_ROOT"
    
    if [ -d "tmp" ]; then
        # Count total directories to clean for progress tracking
        print_info "📊 Counting directories to clean..."
        total_dirs=$(find tmp/ -maxdepth 1 -type d -name "*-*-*-*-*" -mtime +7 2>/dev/null | wc -l | tr -d ' ')
        
        if [ "$total_dirs" -gt 0 ]; then
            print_info "🗂️  Found $total_dirs run directories older than 7 days to clean"
            print_info "⏱️  Starting cleanup (this may take several minutes)..."
            
            # Enhanced removal with progress tracking
            count=0
            batch_size=100
            start_time=$(date +%s)
            
            # Use find with -print0 and process in batches for better performance
            find tmp/ -maxdepth 1 -type d -name "*-*-*-*-*" -mtime +7 -print0 2>/dev/null | \
            while IFS= read -r -d '' dir; do
                # Remove directory
                rm -rf "$dir" 2>/dev/null || true
                
                # Increment counter
                count=$((count + 1))
                
                # Show progress every batch_size directories
                if [ $((count % batch_size)) -eq 0 ] || [ "$count" -eq "$total_dirs" ]; then
                    # Calculate progress percentage
                    progress=$((count * 100 / total_dirs))
                    
                    # Calculate elapsed time and estimate remaining
                    current_time=$(date +%s)
                    elapsed=$((current_time - start_time))
                    
                    if [ "$count" -gt 0 ] && [ "$elapsed" -gt 0 ]; then
                        rate=$((count * 60 / elapsed))  # dirs per minute
                        remaining_dirs=$((total_dirs - count))
                        
                        if [ "$rate" -gt 0 ]; then
                            eta_minutes=$((remaining_dirs / rate))
                            print_info "🗂️  Progress: $count/$total_dirs (${progress}%) | Rate: ${rate}/min | ETA: ${eta_minutes}min"
                        else
                            print_info "🗂️  Progress: $count/$total_dirs (${progress}%) | Elapsed: ${elapsed}s"
                        fi
                    else
                        print_info "🗂️  Progress: $count/$total_dirs (${progress}%)"
                    fi
                    
                    # Show current directory being processed (truncated for readability)
                    dir_name=$(basename "$dir")
                    if [ ${#dir_name} -gt 50 ]; then
                        dir_display="${dir_name:0:25}...${dir_name: -20}"
                    else
                        dir_display="$dir_name"
                    fi
                    print_info "📁 Processing: $dir_display"
                fi
            done
            
            print_success "✅ Removed $total_dirs run directories"
        else
            print_info "🎉 No run directories older than 7 days found"
        fi
        
        # Clean all old logs with progress
        print_info "🧹 Cleaning old log files..."
        log_count=$(find tmp/ -name "*.log" -mtime +3 2>/dev/null | wc -l | tr -d ' ')
        if [ "$log_count" -gt 0 ]; then
            print_info "📄 Found $log_count log files to clean"
            find tmp/ -name "*.log" -mtime +3 -delete 2>/dev/null || true
            print_success "✅ Cleaned $log_count log files"
        fi
        
        # Clean compute logs with progress
        compute_log_count=$(find tmp/ -name "compute_logs" -type d -exec find {} -name "*.log" -mtime +3 \; 2>/dev/null | wc -l | tr -d ' ')
        if [ "$compute_log_count" -gt 0 ]; then
            print_info "💾 Found $compute_log_count compute log files to clean"
            find tmp/ -name "compute_logs" -type d -exec find {} -name "*.log" -mtime +3 -delete \; 2>/dev/null || true
            print_success "✅ Cleaned $compute_log_count compute log files"
        fi
    fi
    
    # Aggressive storage cleanup with progress
    if [ -d "dagster_home/storage" ]; then
        print_info "🗄️  Cleaning dagster_home/storage..."
        storage_files=$(find dagster_home/storage/ -type f -mtime +7 2>/dev/null | wc -l | tr -d ' ')
        if [ "$storage_files" -gt 0 ]; then
            print_info "📦 Found $storage_files storage files to clean"
            find dagster_home/storage/ -type f -mtime +7 -delete 2>/dev/null || true
            print_success "✅ Cleaned $storage_files storage files"
        fi
    fi
    
    # Clean old history with progress
    if [ -d "dagster_home/history" ]; then
        print_info "📚 Cleaning dagster_home/history..."
        history_files=$(find dagster_home/history/ -type f -mtime +7 2>/dev/null | wc -l | tr -d ' ')
        if [ "$history_files" -gt 0 ]; then
            print_info "📋 Found $history_files history files to clean"
            find dagster_home/history/ -type f -mtime +7 -delete 2>/dev/null || true
            print_success "✅ Cleaned $history_files history files"
        fi
    fi
    
    # Final cleanup summary
    print_info "📊 Final storage analysis..."
    final_dirs=$(find tmp/ -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
    final_size=$(du -sh tmp/ 2>/dev/null | cut -f1 || echo "0B")
    
    print_success "🔥 Aggressive cleanup completed!"
    print_info "📈 Remaining directories: $final_dirs"
    print_info "💾 Remaining tmp/ size: $final_size"
}

cleanup_nuclear() {
    print_info "☢️  Performing nuclear cleanup..."
    
    cd "$PROJECT_ROOT"
    
    if [ -d "tmp" ]; then
        # Remove run directories older than 1 day
        print_info "Removing run directories older than 24 hours..."
        find tmp/ -maxdepth 1 -type d -name "*-*-*-*-*" -mtime +1 -exec rm -rf {} \; 2>/dev/null || true
        
        # Remove all logs older than 1 day
        find tmp/ -name "*.log" -mtime +1 -delete 2>/dev/null || true
    fi
    
    # Nuclear storage cleanup
    if [ -d "dagster_home/storage" ]; then
        find dagster_home/storage/ -type f -mtime +1 -delete 2>/dev/null || true
    fi
    
    if [ -d "dagster_home/history" ]; then
        find dagster_home/history/ -type f -mtime +1 -delete 2>/dev/null || true
    fi
    
    # Clean up empty directories
    find tmp/ -type d -empty -delete 2>/dev/null || true
    find dagster_home/storage/ -type d -empty -delete 2>/dev/null || true
    find dagster_home/history/ -type d -empty -delete 2>/dev/null || true
    
    print_success "Nuclear cleanup completed"
}

cleanup_cli_based() {
    print_info "🛠️  Performing CLI-based cleanup using Dagster commands..."
    
    cd "$PROJECT_ROOT"
    
    print_warning "This will use Dagster's built-in cleanup commands"
    print_warning "This requires a running Dagster instance"
    
    if confirm "Do you want to wipe all run history from the database?"; then
        print_info "Wiping run history..."
        # Note: This requires DAGSTER_HOME to be set correctly
        export DAGSTER_HOME="$PROJECT_ROOT/dagster_home"
        
        # Try to wipe runs (requires instance to be accessible)
        if command -v dagster >/dev/null 2>&1; then
            dagster run wipe --yes 2>/dev/null && print_success "Run history wiped" || print_warning "Could not wipe runs (instance may not be running)"
        else
            print_warning "Dagster CLI not available"
        fi
        
        # Clean local storage manually as backup
        cleanup_aggressive
    else
        print_info "CLI cleanup cancelled"
    fi
}

# Show current configuration status
show_config_status() {
    print_info "🔧 Current Dagster Configuration Status"
    
    cd "$PROJECT_ROOT"
    
    # Check if retention policies are configured
    if grep -q "retention:" dagster_docker.yaml 2>/dev/null; then
        print_success "✅ Retention policies are configured in dagster_docker.yaml"
    else
        print_warning "⚠️  No retention policies found in dagster_docker.yaml"
        print_info "   Add retention policies to prevent storage buildup"
    fi
    
    # Check concurrent runs setting
    if grep -q "max_concurrent_runs: 10" dagster_docker.yaml 2>/dev/null; then
        print_success "✅ Concurrent runs limited to 10 (good for storage)"
    elif grep -q "max_concurrent_runs:" dagster_docker.yaml 2>/dev/null; then
        concurrent_runs=$(grep "max_concurrent_runs:" dagster_docker.yaml | head -1 | awk '{print $2}')
        if [ "$concurrent_runs" -gt 15 ]; then
            print_warning "⚠️  High concurrent runs ($concurrent_runs) may cause storage issues"
        else
            print_info "ℹ️  Concurrent runs set to $concurrent_runs"
        fi
    fi
    
    # Check run monitoring
    if grep -q "run_monitoring:" dagster_docker.yaml 2>/dev/null; then
        print_success "✅ Run monitoring is configured"
    else
        print_warning "⚠️  Run monitoring not configured - may miss stuck runs"
    fi
}

# Main menu
main_menu() {
    while true; do
        clear
        print_info "🗂️  Dagster Storage Cleanup Tool"
        echo
        
        analyze_storage
        echo
        
        show_cleanup_options
        echo
        
        echo "Additional Options:"
        echo "6. 🔧 Show Dagster configuration status"
        echo "7. 📊 Re-analyze storage (refresh)"
        echo "8. ❌ Exit"
        echo
        
        read -p "Choose cleanup option [1-8]: " -n 1 -r choice
        echo
        
        case $choice in
            1)
                cleanup_minimal
                ;;
            2)
                if confirm "Proceed with standard cleanup? (removes data older than 30 days)"; then
                    cleanup_standard
                fi
                ;;
            3)
                if confirm "Proceed with aggressive cleanup? (removes data older than 7 days)"; then
                    cleanup_aggressive
                fi
                ;;
            4)
                print_error "⚠️  NUCLEAR CLEANUP WARNING"
                print_error "This will remove almost all run data (except last 24 hours)!"
                if confirm "Are you absolutely sure?" "n"; then
                    if confirm "Really proceed with nuclear cleanup?" "n"; then
                        cleanup_nuclear
                    fi
                fi
                ;;
            5)
                cleanup_cli_based
                ;;
            6)
                show_config_status
                ;;
            7)
                continue  # Will re-analyze at top of loop
                ;;
            8)
                print_info "Exiting cleanup tool"
                exit 0
                ;;
            *)
                print_error "Invalid option: $choice"
                ;;
        esac
        
        echo
        print_info "Press any key to continue..."
        read -n 1 -s
    done
}

# Help function
usage() {
    echo "Usage: $0 [minimal|standard|aggressive|nuclear|cli|status|menu]"
    echo
    echo "Options:"
    echo "  minimal    - Clean old compute logs only"
    echo "  standard   - Remove runs older than 30 days"
    echo "  aggressive - Remove runs older than 7 days"
    echo "  nuclear    - Remove almost all data"
    echo "  cli        - Use Dagster CLI cleanup commands"
    echo "  status     - Show Dagster configuration status"
    echo "  menu       - Interactive menu (default)"
    echo
}

# Main execution
case "${1:-menu}" in
    "minimal")
        analyze_storage
        cleanup_minimal
        ;;
    "standard")
        analyze_storage
        if confirm "Proceed with standard cleanup?"; then
            cleanup_standard
        fi
        ;;
    "aggressive")
        analyze_storage
        if confirm "Proceed with aggressive cleanup?"; then
            cleanup_aggressive
        fi
        ;;
    "nuclear")
        analyze_storage
        if confirm "Proceed with nuclear cleanup?" "n"; then
            cleanup_nuclear
        fi
        ;;
    "cli")
        cleanup_cli_based
        ;;
    "status")
        show_config_status
        ;;
    "menu"|"")
        main_menu
        ;;
    "-h"|"--help")
        usage
        ;;
    *)
        print_error "Invalid option: $1"
        usage
        exit 1
        ;;
esac 
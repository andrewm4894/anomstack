# Utilities Directory

This directory contains general utility scripts for system management and maintenance.

## Scripts

### `reset_docker.sh`

Comprehensive Docker reset utility for Anomstack with multiple cleanup levels and safety checks.

#### Features

- 🔄 **Interactive Mode**: Guided menu with clear options
- 📊 **Data Size Display**: Shows current disk usage before cleanup
- ⚠️ **Safety Confirmations**: Multiple confirmations for destructive operations
- 🎨 **Colorful Output**: Clear visual feedback with emojis and colors
- 🛡️ **Fallback Handling**: Works even if Makefile targets fail

#### Reset Levels

##### 1. Gentle Reset (`gentle`)
**Safest option** - Rebuilds containers with fresh images
- ✅ **Preserves**: All data, volumes, local files
- 🔄 **Rebuilds**: Docker images from scratch
- 🎯 **Use when**: You want fresh containers but keep all data

```bash
# Via Makefile
make reset-gentle

# Direct script usage
./scripts/utils/reset_docker.sh gentle
```

##### 2. Medium Reset (`medium`)
**Balanced option** - Removes containers but preserves data
- ✅ **Preserves**: Docker volumes, local data files
- 🗑️ **Removes**: Containers, networks
- 🎯 **Use when**: Container issues but want to keep data

```bash
# Via Makefile
make reset-medium

# Direct script usage
./scripts/utils/reset_docker.sh medium
```

##### 3. Nuclear Reset (`nuclear`)
**Destructive option** - Removes all data and containers
- ⚠️ **Removes**: Docker volumes, all local data (63GB+ in your case)
- 🗑️ **Cleans**: tmp/, storage/, history/, logs/, telemetry/
- 🎯 **Use when**: You want a completely fresh start

```bash
# Via Makefile
make reset-nuclear

# Direct script usage
./scripts/utils/reset_docker.sh nuclear
```

##### 4. Full Nuclear Reset (`full-nuclear`)
**Maximum cleanup** - Nuclear reset + full Docker system cleanup
- ⚠️ **Removes**: Everything from nuclear reset
- 🗑️ **Plus**: All unused Docker images, networks, build cache
- 💾 **Frees**: Maximum possible disk space
- 🎯 **Use when**: You want absolute maximum cleanup

```bash
# Via Makefile
make reset-full-nuclear

# Direct script usage
./scripts/utils/reset_docker.sh full-nuclear
```

#### Interactive Mode

Run without arguments for a guided experience:

```bash
# Via Makefile (recommended)
make reset-interactive

# Direct script usage
./scripts/utils/reset_docker.sh
```

**Example Interactive Session:**
```
🐳 Anomstack Docker Reset Tool

ℹ️  Select reset level:
1) 🔄 Gentle - Rebuild containers (safest)
2) 🧹 Medium - Remove containers, keep data
3) ☢️  Nuclear - Remove all data and containers
4) 💥 Full Nuclear - Nuclear + full Docker cleanup
5) ❌ Cancel

Choose option [1-5]:
```

#### What's Always Preserved

Regardless of reset level, these are **always preserved**:
- 💾 Source code (`anomstack/`, `dashboard/`, `metrics/`)
- ⚙️ Configuration files (`.env`, `docker-compose.yaml`, etc.)
- 🛠️ Git repository and history
- 📝 Documentation and README files

#### Safety Features

- **Double Confirmation**: Destructive operations require two confirmations
- **Data Size Display**: Shows exactly how much data will be deleted
- **Detailed Warnings**: Clear indication of what will be lost
- **Graceful Fallback**: Works even if Makefile targets are broken
- **Error Handling**: Continues operation even if individual steps fail

#### Usage Tips

1. **Start Conservative**: Begin with `gentle` reset if unsure
2. **Check Data Size**: Script shows current usage before cleanup
3. **Use Interactive Mode**: Provides the best guidance for choosing reset level
4. **Free Disk Space**: `full-nuclear` provides maximum space recovery
5. **Fresh Installation Feel**: `nuclear` or `full-nuclear` gives you a brand new setup

#### Examples

**Quick gentle reset:**
```bash
make reset-gentle
```

**Interactive guided reset:**
```bash
make reset-interactive
```

**Nuclear reset for maximum cleanup (your 63GB case):**
```bash
make reset-nuclear
```

**Maximum possible disk space recovery:**
```bash
make reset-full-nuclear
```

#### Script Output

The script provides colorful, informative output:
- 🔵 **Info**: General information and progress
- 🟢 **Success**: Completed operations
- 🟡 **Warning**: Important notices and confirmations  
- 🔴 **Error**: Critical warnings about data loss

This makes it easy to understand what's happening at each step of the reset process.

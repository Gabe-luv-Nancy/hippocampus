# User Configuration for Hippocampus
# 
# Edit this file to customize memory behavior
# Changes take effect after running: /hip config reload

# ============================================
# Trigger Settings
# ============================================

# Save to Chronicle after this many conversation rounds
ROUND_THRESHOLD = 25

# Save to Chronicle after this many hours (time-based trigger)
TIME_HOURS = 6

# Save to Monograph when tokens exceed this threshold
TOKEN_THRESHOLD = 10000

# ============================================
# Storage Settings  
# ============================================

# Base directory for all memory files
# Relative paths are relative to the skill folder
# Absolute paths starting with / are also supported
BASE_PATH = ./assets/hippocampus

# Subdirectory names (usually no need to change)
CHRONICLE_DIR = chronicle
MONOGRAPH_DIR = monograph
INDEX_DIR = index

# ============================================
# Special Needs (Advanced)
# ============================================

# Special memory types for before/after answer execution
# These are loaded into context when relevant triggers fire

# BEFORE_ANSWER: Memory loaded before each response
# Format: topic_name (will load from monograph)
# Example: user_preferences, language_rules, style_guide
BEFORE_ANSWER = 

# AFTER_ANSWER: Memory to check/process after each response
# Format: topic_name (will be updated after each exchange)
# Example: conversation_summary, key_points
AFTER_ANSWER = 

# ============================================
# File Organization
# ============================================

# Enable automatic file detection in memory
FILE_ORG_ENABLED = true

# Auto-move files without asking (NOT RECOMMENDED)
FILE_ORG_AUTO_MOVE = false

# Paths to scan for related files (comma-separated)
FILE_SCAN_PATHS = ./workspace

# Paths to exclude from scanning (comma-separated)
FILE_EXCLUDE_PATHS = .openclaw,node_modules,.git

# ============================================
# Keyword & Association
# ============================================

# Maximum number of keywords to extract
KEYWORD_COUNT = 20

# Association generation depth
ASSOCIATION_DEPTH = 3

# ============================================
# Auto-Save
# ============================================

# Enable automatic memory saving (required for cron to work)
AUTO_SAVE = true

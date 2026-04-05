# Changelog

All notable changes to Hippocampus will be documented in this file.

## [3.2.0] - 2026-04-05

### Added

#### Memory Capture Module (`capture.py`)
- Automatic scanning of AI memory files from multiple sources
- Support for: OpenClaw, 豆包, 元宝, 讯飞星火, Kimi, 通义千问, DeepSeek
- Configurable capture paths via YAML
- Manifest generation for captured files

#### Local Analyzer (`analyzer.py`)
- SQLite-based vector database (TF-IDF keyword search)
- Memory indexing and retrieval
- Summary report generation (JSON/Markdown)
- Local model interface (Ollama/LM Studio support)

#### USB Product Support (`usb_manager.py`)
- Auto-detection of Hippocampus USB drive
- Cross-platform autorun scripts (Windows/macOS/Linux)
- OpenClaw bridge protocol for host communication
- Activity logging

#### U-Disk Product Structure (`U/`)
- `autorun.bat` - Windows automatic execution
- `autorun.sh` - macOS/Linux automatic execution
- `HIPPOCAMPUS_Marker.txt` - Product identification

### Changed
- Dual storage architecture (Chronicle + Monograph) maintained
- Enhanced keyword extraction algorithm
- Improved search relevance scoring

### Deprecated
- None

### Fixed
- None (new release)

---

## [3.0.0] - 2026-03-21

### Added
- Photon branding and new philosophy
- Command prefix changed from `/hip` to `/photon`
- `/photon graph` for knowledge graph visualization
- Achievement/Reward system design (planned)

### Changed
- Complete rewrite of memory engine
- Improved SQLite indexing

---

## [2.2.0] - 2026-03-14

### Added
- Dual storage architecture
- Monograph system for important events
- Keyword index files

---

## [2.0.0] - 2026-03-01

### Added
- SQLite database for indexing
- File organization features
- Association generator

---

## [1.0.0] - 2026-02-15

### Added
- Initial release
- Basic chronicle functionality
- Markdown file storage

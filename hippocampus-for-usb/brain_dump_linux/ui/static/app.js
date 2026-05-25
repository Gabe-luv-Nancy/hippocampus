/**
 * Hippocampus BrainDump Frontend
 * v3.1
 */

// API Base URL (same origin)
const API_BASE = '';

// Global State
let currentSource = 'all';
let detectedTools = [];
let scanResults = [];
let selectedFiles = new Set();
let selectedSources = new Set();

// ============================================================================
// API Calls
// ============================================================================

async function api(endpoint, options = {}) {
    try {
        const url = API_BASE + endpoint;
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        return { success: false, error: error.message };
    }
}

async function getStats() {
    return await api('/api/stats');
}

async function getFiles(source = null) {
    const url = source && source !== 'all' ? `/api/files?source=${encodeURIComponent(source)}` : '/api/files';
    return await api(url);
}

async function getCaptures() {
    return await api('/api/captures');
}

async function detectTools() {
    return await api('/api/detect');
}

async function scanTools(tools) {
    return await api('/api/scan', {
        method: 'POST',
        body: JSON.stringify({ tools })
    });
}

async function backupFiles(files, source) {
    return await api('/api/backup', {
        method: 'POST',
        body: JSON.stringify({ files, source })
    });
}

async function getFileContent(relativePath) {
    return await api(`/api/file/${encodeURIComponent(relativePath)}`);
}

// ============================================================================
// UI Updates
// ============================================================================

function setStatus(text) {
    document.getElementById('status-text').textContent = text;
    document.getElementById('status-time').textContent = new Date().toLocaleTimeString('zh-CN');
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

function formatDate(dateStr) {
    if (!dateStr) return '--';
    const d = new Date(dateStr);
    if (d.getFullYear() < 2000) return '从未';
    return d.toLocaleDateString('zh-CN') + ' ' + d.toLocaleTimeString('zh-CN', {hour: '2-digit', minute: '2-digit'});
}

async function refreshStats() {
    const result = await getStats();
    if (!result.success) return;
    
    document.getElementById('stat-files').textContent = result.total_files || 0;
    document.getElementById('stat-size').textContent = formatBytes(result.total_size || 0);
    document.getElementById('stat-captures').textContent = result.total_captures || 0;
    document.getElementById('stat-sources').textContent = result.sources ? result.sources.length : 0;
    
    // Update source filter
    updateSourceFilter(result.sources || []);
}

async function refreshFiles() {
    const container = document.getElementById('file-list');
    
    if (currentSource === 'all') {
        container.innerHTML = '<div class="loading">加载中...</div>';
        const result = await getFiles();
        renderFiles(result.files || []);
    } else {
        container.innerHTML = '<div class="loading">加载中...</div>';
        const result = await getFiles(currentSource);
        renderFiles(result.files || []);
    }
}

function renderFiles(files) {
    const container = document.getElementById('file-list');
    
    if (!files || files.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📭</div>
                <p>暂无记忆文件</p>
                <p style="font-size: 12px; margin-top: 8px;">切换到「主机检测」扫描并备份文件</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = files.map(file => `
        <div class="file-item" onclick="showFilePreview('${escapeHtml(file.relative_path || file.file_name)}')">
            <div class="file-icon">📄</div>
            <div class="file-info">
                <div class="file-name">${escapeHtml(file.file_name)}</div>
                <div class="file-meta">
                    <span class="file-source">${escapeHtml(file.source_ai)}</span>
                    <span>${formatBytes(file.size_bytes || 0)}</span>
                    <span>${formatDate(file.modified_at)}</span>
                </div>
            </div>
        </div>
    `).join('');
}

function updateSourceFilter(sources) {
    const filter = document.getElementById('source-filter');
    const currentActive = filter.querySelector('.filter-btn.active');
    const currentSource = currentActive ? currentActive.dataset.source : 'all';
    
    filter.innerHTML = `<button class="filter-btn ${currentSource === 'all' ? 'active' : ''}" data-source="all" onclick="filterBySource('all')">全部</button>`;
    
    sources.forEach(s => {
        filter.innerHTML += `
            <button class="filter-btn ${currentSource === s.name ? 'active' : ''}" 
                    data-source="${escapeHtml(s.name)}" 
                    onclick="filterBySource('${escapeHtml(s.name)}')">
                ${escapeHtml(s.name)} (${s.count})
            </button>
        `;
    });
}

async function refreshHistory() {
    const container = document.getElementById('history-list');
    container.innerHTML = '<div class="loading">加载中...</div>';
    
    const result = await getCaptures();
    const captures = result.captures || [];
    
    if (captures.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📜</div>
                <p>暂无抓取历史</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = captures.map(c => `
        <div class="history-item">
            <div class="history-date">${formatDate(c.capture_date)}</div>
            <div class="history-stats">
                <span>📁 ${c.total_files || 0} 个文件</span>
                <span>💾 ${formatBytes(c.total_size_bytes || 0)}</span>
            </div>
            ${c.host_computer ? `<div class="history-host">来自: ${escapeHtml(c.host_computer)}</div>` : ''}
            ${c.notes ? `<div class="history-host">${escapeHtml(c.notes)}</div>` : ''}
        </div>
    `).join('');
}

async function refreshAll() {
    setStatus('刷新中...');
    await Promise.all([
        refreshStats(),
        refreshFiles(),
        refreshHistory()
    ]);
    setStatus('就绪');
}

// ============================================================================
// Tab Navigation
// ============================================================================

function switchTab(tabName) {
    // Update buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });
    
    // Update panels
    document.querySelectorAll('.tab-panel').forEach(panel => {
        panel.classList.toggle('active', panel.id === `tab-${tabName}`);
    });
    
    // Refresh content
    if (tabName === 'browser') refreshFiles();
    else if (tabName === 'history') refreshHistory();
}

// ============================================================================
// File Browser
// ============================================================================

function filterBySource(source) {
    currentSource = source;
    
    // Update filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.source === source);
    });
    
    refreshFiles();
}

// ============================================================================
// File Preview
// ============================================================================

async function showFilePreview(relativePath) {
    const modal = document.getElementById('preview-modal');
    const title = document.getElementById('preview-title');
    const content = document.getElementById('preview-content');
    
    title.textContent = relativePath.split('/').pop();
    content.textContent = '加载中...';
    modal.style.display = 'flex';
    
    const result = await getFileContent(relativePath);
    
    if (result.success) {
        content.textContent = result.content;
    } else {
        content.textContent = `加载失败: ${result.error}`;
    }
}

function closePreview() {
    document.getElementById('preview-modal').style.display = 'none';
}

// ============================================================================
// Host Detection
// ============================================================================

async function detectTools() {
    const btn = document.getElementById('detect-btn-text');
    const container = document.getElementById('detected-tools');
    
    btn.textContent = '检测中...';
    container.innerHTML = '<div class="loading">正在检测主机...</div>';
    
    const result = await detectTools();
    
    btn.textContent = '重新检测';
    
    if (!result.success || result.tools.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <p>未检测到支持的 AI 工具</p>
                <p style="font-size: 12px; margin-top: 8px; color: var(--text-muted);">
                    请确保已安装 OpenClaw、豆包、Kimi 等 AI 工具
                </p>
            </div>
        `;
        return;
    }
    
    detectedTools = result.tools;
    
    container.innerHTML = result.tools.map(tool => `
        <div class="tool-item">
            <div class="tool-icon">${getToolIcon(tool.name)}</div>
            <div class="tool-info">
                <div class="tool-name">${escapeHtml(tool.display_name)}</div>
                ${tool.found_paths && tool.found_paths.length > 0 ? 
                    `<div class="tool-paths">${escapeHtml(tool.found_paths[0])}</div>` : ''}
            </div>
            <div class="tool-status" title="已安装"></div>
        </div>
    `).join('');
    
    // Show scan section
    document.getElementById('scan-section').style.display = 'block';
    
    // Populate scan source buttons
    const scanSources = document.getElementById('scan-sources');
    scanSources.innerHTML = result.tools.map(tool => `
        <button class="scan-source-btn selected" 
                data-source="${escapeHtml(tool.name)}" 
                onclick="toggleSource('${escapeHtml(tool.name)}')">
            ${escapeHtml(tool.display_name)}
        </button>
    `).join('');
    
    selectedSources = new Set(result.tools.map(t => t.name));
}

function getToolIcon(name) {
    const icons = {
        'openclaw': '🦅',
        'doubao': '🫛',
        'kimi': '🌙',
        'qwen': '🐴',
        'yuanbao': '👾',
        'xfyun': '⭐',
        'deepseek': '🔮',
        'claude': '🧑‍🎨',
        'chatgpt': '💬',
        'gemini': '✨'
    };
    return icons[name] || '🤖';
}

function toggleSource(source) {
    if (selectedSources.has(source)) {
        selectedSources.delete(source);
    } else {
        selectedSources.add(source);
    }
    
    document.querySelectorAll('.scan-source-btn').forEach(btn => {
        btn.classList.toggle('selected', selectedSources.has(btn.dataset.source));
    });
    
    document.getElementById('scan-all').checked = selectedSources.size === detectedTools.length;
}

function toggleScanAll() {
    const checked = document.getElementById('scan-all').checked;
    
    if (checked) {
        selectedSources = new Set(detectedTools.map(t => t.name));
        document.querySelectorAll('.scan-source-btn').forEach(btn => {
            btn.classList.add('selected');
        });
    } else {
        selectedSources.clear();
        document.querySelectorAll('.scan-source-btn').forEach(btn => {
            btn.classList.remove('selected');
        });
    }
}

async function startScan() {
    const btn = document.getElementById('scan-btn-text');
    const resultsSection = document.getElementById('scan-results');
    const resultsList = document.getElementById('result-list');
    
    if (selectedSources.size === 0) {
        setStatus('请选择至少一个来源');
        return;
    }
    
    btn.textContent = '扫描中...';
    btn.disabled = true;
    setStatus(`正在扫描 ${selectedSources.size} 个来源...`);
    
    const tools = Array.from(selectedSources);
    const result = await scanTools(tools);
    
    btn.textContent = '🔍 重新扫描';
    btn.disabled = false;
    
    if (!result.success) {
        setStatus(`扫描失败: ${result.error}`);
        return;
    }
    
    scanResults = result.files || [];
    selectedFiles.clear();
    
    resultsSection.style.display = 'block';
    document.getElementById('result-count').textContent = `${scanResults.length} 个文件`;
    
    if (scanResults.length === 0) {
        resultsList.innerHTML = `
            <div class="empty-state">
                <p>未找到记忆文件</p>
            </div>
        `;
        document.getElementById('backup-btn').disabled = true;
        return;
    }
    
    resultsList.innerHTML = scanResults.map((file, idx) => `
        <div class="result-item">
            <input type="checkbox" 
                   id="file-${idx}" 
                   onchange="toggleFileSelection(${idx})"
                   checked>
            <div class="file-info" style="flex: 1;">
                <div class="file-name">${escapeHtml(file.file_name)}</div>
                <div class="file-meta">
                    <span class="file-source">${escapeHtml(file.source_ai)}</span>
                    <span>${formatBytes(file.size)}</span>
                    <span>${escapeHtml(file.path)}</span>
                </div>
            </div>
        </div>
    `).join('');
    
    // Auto-select all
    scanResults.forEach((_, idx) => selectedFiles.add(idx));
    updateBackupButton();
    setStatus(`找到 ${scanResults.length} 个记忆文件`);
}

function toggleFileSelection(idx) {
    if (selectedFiles.has(idx)) {
        selectedFiles.delete(idx);
    } else {
        selectedFiles.add(idx);
    }
    updateBackupButton();
}

function selectAll() {
    scanResults.forEach((_, idx) => selectedFiles.add(idx));
    document.querySelectorAll('.result-item input[type="checkbox"]').forEach((cb, idx) => {
        cb.checked = true;
    });
    updateBackupButton();
}

function selectNone() {
    selectedFiles.clear();
    document.querySelectorAll('.result-item input[type="checkbox"]').forEach(cb => {
        cb.checked = false;
    });
    updateBackupButton();
}

function updateBackupButton() {
    const btn = document.getElementById('backup-btn');
    const count = selectedFiles.size;
    btn.disabled = count === 0;
    btn.innerHTML = count > 0 ? `💾 备份选中文件 (${count})` : '💾 备份选中文件';
}

async function backupSelected() {
    if (selectedFiles.size === 0) return;
    
    const btn = document.getElementById('backup-btn');
    btn.disabled = true;
    btn.textContent = '备份中...';
    setStatus('正在备份文件...');
    
    // Get selected files
    const filesToBackup = Array.from(selectedFiles).map(idx => scanResults[idx]);
    
    // Group by source
    const bySource = {};
    filesToBackup.forEach(f => {
        if (!bySource[f.source_ai]) bySource[f.source_ai] = [];
        bySource[f.source_ai].push(f.path);
    });
    
    let totalImported = 0;
    let hasError = false;
    
    for (const [source, paths] of Object.entries(bySource)) {
        const result = await backupFiles(paths, source);
        if (result.success) {
            totalImported += result.imported;
        }
        if (result.errors && result.errors.length > 0) {
            hasError = true;
            console.error('Backup errors:', result.errors);
        }
    }
    
    btn.textContent = '💾 备份完成';
    btn.disabled = false;
    
    setStatus(`备份完成：${totalImported} 个文件已保存`);
    
    // Refresh after backup
    setTimeout(async () => {
        await refreshAll();
        // Reset button
        setTimeout(() => {
            btn.textContent = '💾 备份选中文件';
            updateBackupButton();
        }, 2000);
    }, 1000);
}

// ============================================================================
// Expandable Sections
// ============================================================================

function toggleSection(sectionId) {
    const content = document.getElementById(sectionId);
    const icon = document.getElementById(sectionId + '-icon');
    
    const isHidden = content.style.display === 'none';
    content.style.display = isHidden ? 'block' : 'none';
    icon.classList.toggle('expanded', isHidden);
}

// ============================================================================
// Utilities
// ============================================================================

function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// ============================================================================
// Initialization
// ============================================================================

document.addEventListener('DOMContentLoaded', async () => {
    // Close modal on escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closePreview();
    });
    
    // Close modal on backdrop click
    document.getElementById('preview-modal').addEventListener('click', (e) => {
        if (e.target.id === 'preview-modal') closePreview();
    });
    
    // Initial load
    setStatus('加载中...');
    await refreshStats();
    await refreshFiles();
    await refreshHistory();
    setStatus('就绪');
});

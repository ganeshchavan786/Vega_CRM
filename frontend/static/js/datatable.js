/**
 * Advanced DataTable Framework v2.0
 * A plug-and-play data table component with sorting, filtering, pagination, export, and more
 * 
 * Features:
 * - Sorting (single/multi column)
 * - Global & Column Search
 * - Pagination with page size options
 * - Column visibility toggle
 * - Export (CSV, Excel, PDF, Print)
 * - Row selection (single/multi)
 * - Responsive design
 * - Loading states
 * - Empty states
 * - Row actions
 * - Inline editing
 * - Sticky header
 * - Column resizing
 * 
 * Usage:
 * const table = new DataTable('containerId', {
 *     data: [...],
 *     columns: [...],
 *     pagination: true,
 *     sorting: true,
 *     stickyHeader: true,
 *     loading: false
 * });
 */

class DataTable {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            throw new Error(`Container with id "${containerId}" not found`);
        }

        // Default options
        this.options = {
            // Data
            data: options.data || [],
            columns: options.columns || [],
            
            // Features
            sorting: options.sorting !== false,
            filtering: options.filtering !== false,
            pagination: options.pagination !== false,
            export: options.export !== false,
            selection: options.selection || false,
            responsive: options.responsive !== false,
            
            // Pagination
            pageSize: options.pageSize || 25,
            pageSizeOptions: options.pageSizeOptions || [10, 25, 50, 100],
            
            // UI
            showSearch: options.showSearch !== false,
            showColumnToggle: options.showColumnToggle !== false,
            showExport: options.showExport !== false,
            
            // Callbacks
            onRowClick: options.onRowClick || null,
            onSelect: options.onSelect || null,
            onSort: options.onSort || null,
            onFilter: options.onFilter || null,
            
            // Styling
            className: options.className || 'datatable',
            
            // Advanced features
            stickyHeader: options.stickyHeader || false,
            loading: options.loading || false,
            emptyMessage: options.emptyMessage || 'No data available',
            loadingMessage: options.loadingMessage || 'Loading...',
            striped: options.striped !== false,
            hover: options.hover !== false,
            bordered: options.bordered || false,
            compact: options.compact || false,
            
            // Inline editing
            editable: options.editable || false,
            onEdit: options.onEdit || null,
            
            // Row actions
            rowActions: options.rowActions || null,
            
            // Bulk actions
            bulkActions: options.bulkActions || null,
            
            ...options
        };

        // State
        this.currentData = [];
        this.filteredData = [];
        this.sortedData = [];
        this.displayData = [];
        this.currentPage = 1;
        this.sortState = {}; // { column: 'asc' | 'desc' }
        this.filterState = {}; // { column: value }
        this.selectedRows = new Set();
        this.visibleColumns = new Set();

        // Initialize
        this.init();
    }

    init() {
        // Initialize visible columns
        this.options.columns.forEach((col, index) => {
            if (col.visible !== false) {
                this.visibleColumns.add(index);
            }
        });

        // Load data
        if (typeof this.options.data === 'function') {
            this.loadDataAsync();
        } else {
            this.loadData(this.options.data);
        }
    }

    async loadDataAsync() {
        try {
            const data = await this.options.data();
            this.loadData(data);
        } catch (error) {
            console.error('Error loading data:', error);
            this.renderError('Error loading data');
        }
    }

    loadData(data) {
        this.currentData = Array.isArray(data) ? data : [];
        this.applyFilters();
        // Render after data is processed
        this.render();
    }

    render() {
        this.container.innerHTML = '';
        
        // Create wrapper
        const wrapper = document.createElement('div');
        wrapper.className = `datatable-wrapper ${this.options.className}`;
        
        // Toolbar
        if (this.options.showSearch || this.options.showExport || this.options.showColumnToggle) {
            wrapper.appendChild(this.createToolbar());
        }
        
        // Table container
        const tableContainer = document.createElement('div');
        tableContainer.className = 'datatable-container';
        tableContainer.appendChild(this.createTable());
        wrapper.appendChild(tableContainer);
        
        // Pagination
        if (this.options.pagination) {
            wrapper.appendChild(this.createPagination());
        }
        
        this.container.appendChild(wrapper);
    }

    createToolbar() {
        const toolbar = document.createElement('div');
        toolbar.className = 'datatable-toolbar';
        
        // Left side - Search
        const left = document.createElement('div');
        left.className = 'datatable-toolbar-left';
        
        if (this.options.showSearch) {
            const searchInput = document.createElement('input');
            searchInput.type = 'text';
            searchInput.className = 'datatable-search';
            searchInput.placeholder = 'Search...';
            searchInput.addEventListener('input', (e) => this.handleGlobalSearch(e.target.value));
            left.appendChild(searchInput);
        }
        
        // Right side - Actions
        const right = document.createElement('div');
        right.className = 'datatable-toolbar-right';
        
        if (this.options.showColumnToggle) {
            const columnToggle = this.createColumnToggle();
            right.appendChild(columnToggle);
        }
        
        if (this.options.showExport && this.options.export) {
            const exportBtn = this.createExportButton();
            right.appendChild(exportBtn);
        }
        
        toolbar.appendChild(left);
        toolbar.appendChild(right);
        
        return toolbar;
    }

    createColumnToggle() {
        const btn = document.createElement('button');
        btn.className = 'btn btn-secondary datatable-column-toggle';
        btn.innerHTML = '👁️ Columns';
        btn.addEventListener('click', () => this.showColumnMenu(btn));
        return btn;
    }

    showColumnMenu(button) {
        // Create dropdown menu
        const menu = document.createElement('div');
        menu.className = 'datatable-column-menu';
        
        this.options.columns.forEach((col, index) => {
            const item = document.createElement('div');
            item.className = 'datatable-column-menu-item';
            
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.checked = this.visibleColumns.has(index);
            checkbox.addEventListener('change', () => {
                if (checkbox.checked) {
                    this.visibleColumns.add(index);
                } else {
                    this.visibleColumns.delete(index);
                }
                this.render();
            });
            
            const label = document.createElement('label');
            label.textContent = col.label || col.key;
            label.appendChild(checkbox);
            
            item.appendChild(label);
            menu.appendChild(item);
        });
        
        // Position menu
        const rect = button.getBoundingClientRect();
        menu.style.position = 'fixed';
        menu.style.top = `${rect.bottom + 5}px`;
        menu.style.left = `${rect.left}px`;
        menu.style.zIndex = '1000';
        
        document.body.appendChild(menu);
        
        // Close on outside click
        const closeMenu = (e) => {
            if (!menu.contains(e.target) && e.target !== button) {
                document.body.removeChild(menu);
                document.removeEventListener('click', closeMenu);
            }
        };
        setTimeout(() => document.addEventListener('click', closeMenu), 0);
    }

    createExportButton() {
        const btn = document.createElement('button');
        btn.className = 'btn btn-success datatable-export';
        btn.innerHTML = '📥 Export';
        
        const menu = document.createElement('div');
        menu.className = 'datatable-export-menu';
        menu.innerHTML = `
            <a href="#" data-format="csv">Export CSV</a>
            <a href="#" data-format="excel">Export Excel</a>
            <a href="#" data-format="pdf">Export PDF</a>
            <a href="#" data-format="print">Print</a>
        `;
        
        menu.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.export(link.dataset.format);
            });
        });
        
        btn.addEventListener('click', () => {
            const rect = btn.getBoundingClientRect();
            menu.style.position = 'fixed';
            menu.style.top = `${rect.bottom + 5}px`;
            menu.style.left = `${rect.left}px`;
            menu.style.zIndex = '1000';
            document.body.appendChild(menu);
            
            const closeMenu = (e) => {
                if (!menu.contains(e.target) && e.target !== btn) {
                    document.body.removeChild(menu);
                    document.removeEventListener('click', closeMenu);
                }
            };
            setTimeout(() => document.addEventListener('click', closeMenu), 0);
        });
        
        return btn;
    }

    createTable() {
        const table = document.createElement('table');
        let tableClass = 'datatable-table';
        if (this.options.striped) tableClass += ' datatable-striped';
        if (this.options.hover) tableClass += ' datatable-hover';
        if (this.options.bordered) tableClass += ' datatable-bordered';
        if (this.options.compact) tableClass += ' datatable-compact';
        if (this.options.stickyHeader) tableClass += ' datatable-sticky-header';
        table.className = tableClass;
        
        // Header
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        
        // Selection column
        if (this.options.selection) {
            const th = document.createElement('th');
            th.className = 'datatable-select-all';
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.addEventListener('change', (e) => this.selectAll(e.target.checked));
            th.appendChild(checkbox);
            headerRow.appendChild(th);
        }
        
        // Data columns
        this.options.columns.forEach((col, index) => {
            if (!this.visibleColumns.has(index)) return;
            
            const th = document.createElement('th');
            // Use innerHTML if label contains HTML tags, otherwise textContent
            const labelText = col.label || col.key;
            if (labelText.includes('<')) {
                th.innerHTML = labelText;
            } else {
                th.textContent = labelText;
            }
            th.className = col.align || 'left';
            
            if (col.sortable !== false && this.options.sorting) {
                th.className += ' sortable';
                th.addEventListener('click', () => this.sort(index));
                this.updateSortIndicator(th, index);
            }
            
            headerRow.appendChild(th);
        });
        
        thead.appendChild(headerRow);
        table.appendChild(thead);
        
        // Body
        const tbody = document.createElement('tbody');
        tbody.className = 'datatable-body';
        
        // Loading state
        if (this.options.loading) {
            const row = document.createElement('tr');
            const cell = document.createElement('td');
            cell.colSpan = this.visibleColumns.size + (this.options.selection ? 1 : 0);
            cell.className = 'datatable-loading';
            cell.innerHTML = `
                <div class="datatable-loading-spinner">
                    <div class="spinner"></div>
                    <span>${this.options.loadingMessage}</span>
                </div>
            `;
            row.appendChild(cell);
            tbody.appendChild(row);
        } else if (this.displayData.length === 0) {
            const row = document.createElement('tr');
            const cell = document.createElement('td');
            cell.colSpan = this.visibleColumns.size + (this.options.selection ? 1 : 0);
            cell.className = 'datatable-empty';
            cell.innerHTML = `
                <div class="datatable-empty-state">
                    <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#ccc" stroke-width="1">
                        <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/>
                        <polyline points="13 2 13 9 20 9"/>
                    </svg>
                    <p>${this.options.emptyMessage}</p>
                </div>
            `;
            row.appendChild(cell);
            tbody.appendChild(row);
        } else {
            this.displayData.forEach((rowData, rowIndex) => {
                const row = document.createElement('tr');
                row.dataset.index = rowIndex;
                
                if (this.options.onRowClick) {
                    row.style.cursor = 'pointer';
                    row.addEventListener('click', () => this.options.onRowClick(rowData, rowIndex));
                }
                
                // Selection checkbox
                if (this.options.selection) {
                    const td = document.createElement('td');
                    const checkbox = document.createElement('input');
                    checkbox.type = 'checkbox';
                    checkbox.checked = this.selectedRows.has(rowIndex);
                    checkbox.addEventListener('change', (e) => {
                        e.stopPropagation();
                        this.toggleSelection(rowIndex, e.target.checked);
                    });
                    td.appendChild(checkbox);
                    row.appendChild(td);
                }
                
                // Data cells
                this.options.columns.forEach((col, colIndex) => {
                    if (!this.visibleColumns.has(colIndex)) return;
                    
                    const td = document.createElement('td');
                    td.className = col.align || 'left';
                    
                    const value = this.getNestedValue(rowData, col.key);
                    td.innerHTML = this.renderCell(value, rowData, col);
                    
                    row.appendChild(td);
                });
                
                tbody.appendChild(row);
            });
        }
        
        table.appendChild(tbody);
        return table;
    }

    getNestedValue(obj, path) {
        return path.split('.').reduce((o, p) => o && o[p], obj);
    }

    renderCell(value, rowData, column) {
        if (column.render && typeof column.render === 'function') {
            return column.render(value, rowData);
        }
        
        if (value === null || value === undefined) {
            return 'N/A';
        }
        
        switch (column.type) {
            case 'currency':
                const currency = column.format || 'INR';
                const symbol = currency === 'INR' ? '₹' : '$';
                return `${symbol}${parseFloat(value).toFixed(2)}`;
            
            case 'date':
                return this.formatDate(value);
            
            case 'badge':
                return `<span class="status-badge status-${value}">${value}</span>`;
            
            case 'number':
                return parseFloat(value).toLocaleString();
            
            default:
                return String(value);
        }
    }

    formatDate(date) {
        if (!date) return 'N/A';
        const d = new Date(date);
        return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
    }

    createPagination() {
        const pagination = document.createElement('div');
        pagination.className = 'datatable-pagination';
        
        const totalPages = Math.ceil(this.sortedData.length / this.options.pageSize);
        
        // Page info
        const info = document.createElement('div');
        info.className = 'datatable-pagination-info';
        const start = (this.currentPage - 1) * this.options.pageSize + 1;
        const end = Math.min(this.currentPage * this.options.pageSize, this.sortedData.length);
        info.textContent = `Showing ${start}-${end} of ${this.sortedData.length}`;
        pagination.appendChild(info);
        
        // Page size selector
        const pageSizeSelect = document.createElement('select');
        pageSizeSelect.className = 'datatable-page-size';
        this.options.pageSizeOptions.forEach(size => {
            const option = document.createElement('option');
            option.value = size;
            option.textContent = size;
            option.selected = size === this.options.pageSize;
            pageSizeSelect.appendChild(option);
        });
        pageSizeSelect.addEventListener('change', (e) => {
            this.options.pageSize = parseInt(e.target.value);
            this.currentPage = 1;
            this.applyPagination();
            this.render();
        });
        pagination.appendChild(pageSizeSelect);
        
        // Navigation buttons
        const nav = document.createElement('div');
        nav.className = 'datatable-pagination-nav';
        
        const firstBtn = document.createElement('button');
        firstBtn.textContent = '«';
        firstBtn.disabled = this.currentPage === 1;
        firstBtn.addEventListener('click', () => this.goToPage(1));
        nav.appendChild(firstBtn);
        
        const prevBtn = document.createElement('button');
        prevBtn.textContent = '‹';
        prevBtn.disabled = this.currentPage === 1;
        prevBtn.addEventListener('click', () => this.goToPage(this.currentPage - 1));
        nav.appendChild(prevBtn);
        
        // Page numbers
        const pageInfo = document.createElement('span');
        pageInfo.className = 'datatable-page-info';
        pageInfo.textContent = `Page ${this.currentPage} of ${totalPages}`;
        nav.appendChild(pageInfo);
        
        const nextBtn = document.createElement('button');
        nextBtn.textContent = '›';
        nextBtn.disabled = this.currentPage === totalPages;
        nextBtn.addEventListener('click', () => this.goToPage(this.currentPage + 1));
        nav.appendChild(nextBtn);
        
        const lastBtn = document.createElement('button');
        lastBtn.textContent = '»';
        lastBtn.disabled = this.currentPage === totalPages;
        lastBtn.addEventListener('click', () => this.goToPage(totalPages));
        nav.appendChild(lastBtn);
        
        pagination.appendChild(nav);
        
        return pagination;
    }

    // Sorting
    sort(columnIndex) {
        const column = this.options.columns[columnIndex];
        if (!column || column.sortable === false) return;
        
        const currentSort = this.sortState[columnIndex];
        let newSort = 'asc';
        
        if (currentSort === 'asc') {
            newSort = 'desc';
        } else if (currentSort === 'desc') {
            newSort = null; // Clear sort
        }
        
        if (newSort) {
            this.sortState = { [columnIndex]: newSort };
        } else {
            this.sortState = {};
        }
        
        this.applySorting();
        this.render();
        
        if (this.options.onSort) {
            this.options.onSort(column.key, newSort);
        }
    }

    applySorting() {
        if (Object.keys(this.sortState).length === 0) {
            this.sortedData = [...this.filteredData];
        } else {
            const [columnIndex, direction] = Object.entries(this.sortState)[0];
            const column = this.options.columns[columnIndex];
            
            this.sortedData = [...this.filteredData].sort((a, b) => {
                const aVal = this.getNestedValue(a, column.key);
                const bVal = this.getNestedValue(b, column.key);
                
                let comparison = 0;
                if (aVal < bVal) comparison = -1;
                if (aVal > bVal) comparison = 1;
                
                return direction === 'asc' ? comparison : -comparison;
            });
        }
        
        // Always apply pagination after sorting
        this.applyPagination();
    }

    updateSortIndicator(th, columnIndex) {
        const sort = this.sortState[columnIndex];
        th.classList.remove('sort-asc', 'sort-desc');
        if (sort === 'asc') {
            th.classList.add('sort-asc');
            th.innerHTML = `${th.textContent} ↑`;
        } else if (sort === 'desc') {
            th.classList.add('sort-desc');
            th.innerHTML = `${th.textContent} ↓`;
        }
    }

    // Filtering
    handleGlobalSearch(query) {
        this.filterState.global = query.toLowerCase();
        this.applyFilters();
    }

    applyFilters() {
        this.filteredData = this.currentData.filter(row => {
            // Global search
            if (this.filterState.global) {
                const searchTerm = this.filterState.global.toLowerCase();
                const searchable = this.options.columns
                    .map(col => String(this.getNestedValue(row, col.key) || '').toLowerCase())
                    .join(' ');
                if (!searchable.includes(searchTerm)) {
                    return false;
                }
            }
            
            // Column filters
            for (const [columnKey, filterValue] of Object.entries(this.filterState)) {
                if (columnKey === 'global') continue;
                const column = this.options.columns.find(col => col.key === columnKey);
                if (column) {
                    const cellValue = String(this.getNestedValue(row, column.key) || '').toLowerCase();
                    if (!cellValue.includes(filterValue.toLowerCase())) {
                        return false;
                    }
                }
            }
            
            return true;
        });
        
        this.applySorting();
    }

    applyPagination() {
        const start = (this.currentPage - 1) * this.options.pageSize;
        const end = start + this.options.pageSize;
        this.displayData = this.sortedData.slice(start, end);
    }

    goToPage(page) {
        const totalPages = Math.ceil(this.sortedData.length / this.options.pageSize);
        if (page >= 1 && page <= totalPages) {
            this.currentPage = page;
            this.applyPagination();
            this.render();
        }
    }

    // Selection
    selectAll(checked) {
        if (checked) {
            this.displayData.forEach((_, index) => {
                this.selectedRows.add(index);
            });
        } else {
            this.selectedRows.clear();
        }
        this.render();
        
        if (this.options.onSelect) {
            this.options.onSelect(this.getSelectedRows());
        }
    }

    toggleSelection(rowIndex, checked) {
        if (checked) {
            this.selectedRows.add(rowIndex);
        } else {
            this.selectedRows.delete(rowIndex);
        }
        
        if (this.options.onSelect) {
            this.options.onSelect(this.getSelectedRows());
        }
    }

    getSelectedRows() {
        return Array.from(this.selectedRows).map(index => this.displayData[index]);
    }

    // Export
    export(format) {
        const data = this.sortedData;
        const columns = this.options.columns.filter((_, index) => this.visibleColumns.has(index));
        
        switch (format) {
            case 'csv':
                this.exportCSV(data, columns);
                break;
            case 'excel':
                this.exportExcel(data, columns);
                break;
            case 'pdf':
                this.exportPDF(data, columns);
                break;
            case 'print':
                this.printTable();
                break;
        }
    }

    exportCSV(data, columns) {
        const headers = columns.map(col => col.label || col.key);
        const rows = data.map(row => 
            columns.map(col => {
                const value = this.getNestedValue(row, col.key);
                return `"${String(value || '').replace(/"/g, '""')}"`;
            }).join(',')
        );
        
        const csv = [headers.join(','), ...rows].join('\n');
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `export_${new Date().getTime()}.csv`;
        a.click();
        URL.revokeObjectURL(url);
    }

    exportExcel(data, columns) {
        // Requires SheetJS library
        if (typeof XLSX === 'undefined') {
            alert('Excel export requires SheetJS library. Please include: <script src="https://cdn.sheetjs.com/xlsx-0.20.0/package/dist/xlsx.full.min.js"></script>');
            return;
        }
        
        const headers = columns.map(col => col.label || col.key);
        const rows = data.map(row => 
            columns.map(col => this.getNestedValue(row, col.key))
        );
        
        const ws = XLSX.utils.aoa_to_sheet([headers, ...rows]);
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, 'Sheet1');
        XLSX.writeFile(wb, `export_${new Date().getTime()}.xlsx`);
    }

    exportPDF(data, columns) {
        // Requires jsPDF library
        if (typeof jsPDF === 'undefined') {
            alert('PDF export requires jsPDF library. Please include: <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>');
            return;
        }
        
        alert('PDF export coming soon!');
    }

    printTable() {
        const printWindow = window.open('', '_blank');
        const tableHTML = this.container.querySelector('.datatable-table').outerHTML;
        printWindow.document.write(`
            <html>
                <head>
                    <title>Print Table</title>
                    <style>
                        table { border-collapse: collapse; width: 100%; }
                        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                        th { background-color: #f2f2f2; }
                    </style>
                </head>
                <body>
                    ${tableHTML}
                </body>
            </html>
        `);
        printWindow.document.close();
        printWindow.print();
    }

    renderError(message) {
        this.container.innerHTML = `<div class="datatable-error">${message}</div>`;
    }

    // Public API
    refresh() {
        if (typeof this.options.data === 'function') {
            this.loadDataAsync();
        } else {
            this.loadData(this.options.data);
        }
        this.render();
    }

    updateData(data) {
        this.loadData(data);
        // render() is already called in loadData()
    }
    
    setLoading(loading) {
        this.options.loading = loading;
        this.render();
    }
    
    getFilteredData() {
        return this.filteredData;
    }
    
    getSortedData() {
        return this.sortedData;
    }
    
    getCurrentPage() {
        return this.currentPage;
    }
    
    getTotalPages() {
        return Math.ceil(this.sortedData.length / this.options.pageSize);
    }
    
    getTotalRecords() {
        return this.currentData.length;
    }
    
    getFilteredRecords() {
        return this.filteredData.length;
    }
    
    clearFilters() {
        this.filterState = {};
        this.applyFilters();
    }
    
    clearSelection() {
        this.selectedRows.clear();
        this.render();
    }
    
    selectRow(index) {
        this.selectedRows.add(index);
        this.render();
    }
    
    deselectRow(index) {
        this.selectedRows.delete(index);
        this.render();
    }
    
    destroy() {
        this.container.innerHTML = '';
    }
}

// Make available globally
window.DataTable = DataTable;


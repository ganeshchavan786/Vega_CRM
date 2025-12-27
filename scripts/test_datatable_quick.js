/**
 * Quick DataTable Testing Script
 * Run this in browser console on each page to test DataTable functionality
 * 
 * Usage:
 * 1. Open browser console (F12)
 * 2. Navigate to a page (Leads, Customers, etc.)
 * 3. Copy and paste this script
 * 4. Run: testDataTable('leads') // or 'customers', 'contacts', etc.
 */

function testDataTable(pageName) {
    const tableVar = `${pageName}Table`;
    const table = window[tableVar];
    
    console.log(`\n🧪 Testing DataTable on ${pageName.toUpperCase()} page`);
    console.log('=====================================\n');
    
    // Test 1: DataTable class exists
    console.log('Test 1: DataTable class exists');
    if (typeof DataTable !== 'undefined') {
        console.log('✅ PASS: DataTable class is available');
    } else {
        console.log('❌ FAIL: DataTable class not found');
        return;
    }
    
    // Test 2: Table instance exists
    console.log('\nTest 2: Table instance exists');
    if (table) {
        console.log('✅ PASS: Table instance found');
        console.log(`   Instance: window.${tableVar}`);
    } else {
        console.log(`❌ FAIL: Table instance not found (window.${tableVar})`);
        return;
    }
    
    // Test 3: Data loaded
    console.log('\nTest 3: Data loaded');
    if (table.currentData && Array.isArray(table.currentData)) {
        console.log(`✅ PASS: Data loaded (${table.currentData.length} records)`);
        console.log(`   Current data: ${table.currentData.length} records`);
        console.log(`   Display data: ${table.displayData.length} records`);
        console.log(`   Filtered data: ${table.filteredData.length} records`);
        console.log(`   Sorted data: ${table.sortedData.length} records`);
    } else {
        console.log('❌ FAIL: No data loaded');
    }
    
    // Test 4: Columns defined
    console.log('\nTest 4: Columns defined');
    if (table.options && table.options.columns && table.options.columns.length > 0) {
        console.log(`✅ PASS: ${table.options.columns.length} columns defined`);
        console.log('   Columns:', table.options.columns.map(c => c.label || c.key).join(', '));
    } else {
        console.log('❌ FAIL: No columns defined');
    }
    
    // Test 5: Pagination enabled
    console.log('\nTest 5: Pagination enabled');
    if (table.options.pagination) {
        console.log('✅ PASS: Pagination is enabled');
        console.log(`   Page size: ${table.options.pageSize}`);
        console.log(`   Current page: ${table.currentPage}`);
        const totalPages = Math.ceil(table.sortedData.length / table.options.pageSize);
        console.log(`   Total pages: ${totalPages}`);
    } else {
        console.log('⚠️  WARN: Pagination is disabled');
    }
    
    // Test 6: Sorting enabled
    console.log('\nTest 6: Sorting enabled');
    if (table.options.sorting) {
        console.log('✅ PASS: Sorting is enabled');
        const sortableColumns = table.options.columns.filter(c => c.sortable !== false).length;
        console.log(`   Sortable columns: ${sortableColumns}`);
    } else {
        console.log('⚠️  WARN: Sorting is disabled');
    }
    
    // Test 7: Filtering enabled
    console.log('\nTest 7: Filtering enabled');
    if (table.options.filtering) {
        console.log('✅ PASS: Filtering is enabled');
    } else {
        console.log('⚠️  WARN: Filtering is disabled');
    }
    
    // Test 8: Export enabled
    console.log('\nTest 8: Export enabled');
    if (table.options.export) {
        console.log('✅ PASS: Export is enabled');
    } else {
        console.log('⚠️  WARN: Export is disabled');
    }
    
    // Test 9: Test sorting (first column)
    console.log('\nTest 9: Test sorting');
    try {
        const originalSortState = { ...table.sortState };
        table.sort(0); // Sort first column
        console.log('✅ PASS: Sorting works');
        console.log(`   Sort state changed: ${JSON.stringify(originalSortState)} → ${JSON.stringify(table.sortState)}`);
    } catch (error) {
        console.log('❌ FAIL: Sorting error:', error.message);
    }
    
    // Test 10: Test search
    console.log('\nTest 10: Test search');
    try {
        const originalFilterState = { ...table.filterState };
        table.handleGlobalSearch('test');
        console.log('✅ PASS: Search works');
        console.log(`   Filter state: ${JSON.stringify(table.filterState)}`);
        // Reset search
        table.handleGlobalSearch('');
    } catch (error) {
        console.log('❌ FAIL: Search error:', error.message);
    }
    
    // Test 11: Test refresh
    console.log('\nTest 11: Test refresh');
    try {
        table.refresh();
        console.log('✅ PASS: Refresh works');
    } catch (error) {
        console.log('❌ FAIL: Refresh error:', error.message);
    }
    
    // Test 12: Check for errors in DOM
    console.log('\nTest 12: Check DOM for errors');
    const container = document.getElementById(`${pageName}Table`);
    if (container) {
        const errorDiv = container.querySelector('.datatable-error');
        if (errorDiv) {
            console.log('❌ FAIL: Error message found in DOM:', errorDiv.textContent);
        } else {
            console.log('✅ PASS: No error messages in DOM');
        }
    }
    
    console.log('\n=====================================');
    console.log('✅ Testing complete!\n');
    
    return {
        page: pageName,
        tableExists: !!table,
        dataLoaded: table && table.currentData && table.currentData.length > 0,
        columnsDefined: table && table.options && table.options.columns && table.options.columns.length > 0,
        paginationEnabled: table && table.options.pagination,
        sortingEnabled: table && table.options.sorting,
        filteringEnabled: table && table.options.filtering,
        exportEnabled: table && table.options.export
    };
}

// Test all pages
function testAllPages() {
    const pages = ['leads', 'customers', 'contacts', 'deals', 'tasks', 'activities'];
    const results = {};
    
    console.log('🧪 Testing All DataTable Pages');
    console.log('=====================================\n');
    
    pages.forEach(page => {
        const result = testDataTable(page);
        if (result) {
            results[page] = result;
        }
        console.log('\n');
    });
    
    // Summary
    console.log('📊 SUMMARY');
    console.log('=====================================');
    Object.keys(results).forEach(page => {
        const r = results[page];
        const status = (r.tableExists && r.dataLoaded && r.columnsDefined) ? '✅' : '❌';
        console.log(`${status} ${page.toUpperCase()}: Table=${r.tableExists}, Data=${r.dataLoaded}, Columns=${r.columnsDefined}`);
    });
    
    return results;
}

// Helper function to test specific feature
function testFeature(pageName, feature) {
    const table = window[`${pageName}Table`];
    if (!table) {
        console.log(`❌ Table not found: ${pageName}Table`);
        return;
    }
    
    switch(feature) {
        case 'sort':
            table.sort(0);
            console.log('✅ Sorted first column');
            break;
        case 'search':
            table.handleGlobalSearch('test');
            console.log('✅ Search applied');
            setTimeout(() => {
                table.handleGlobalSearch('');
                console.log('✅ Search cleared');
            }, 1000);
            break;
        case 'refresh':
            table.refresh();
            console.log('✅ Table refreshed');
            break;
        default:
            console.log('Available features: sort, search, refresh');
    }
}

console.log('✅ DataTable testing script loaded!');
console.log('Usage:');
console.log('  testDataTable("leads") - Test Leads page');
console.log('  testDataTable("customers") - Test Customers page');
console.log('  testAllPages() - Test all pages');
console.log('  testFeature("leads", "sort") - Test specific feature');


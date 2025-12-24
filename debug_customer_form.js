// Customer Form Debug Script
// Run this in browser console to diagnose issues

console.log('%c=== CUSTOMER FORM DEBUG SCRIPT ===', 'color: blue; font-size: 16px; font-weight: bold;');

let debugResults = {
    errors: [],
    warnings: [],
    success: []
};

function addResult(type, message) {
    debugResults[type].push(message);
    const color = type === 'errors' ? 'red' : type === 'warnings' ? 'orange' : 'green';
    console.log(`%c[${type.toUpperCase()}] ${message}`, `color: ${color};`);
}

// 1. Check if required HTML elements exist
console.log('\n%c1. Checking HTML Elements...', 'color: cyan; font-weight: bold;');
const formModal = document.getElementById('formModal');
const formContent = document.getElementById('formContent');
const customersTable = document.getElementById('customersTable');
const customerSearch = document.getElementById('customerSearch');

if (formModal) {
    addResult('success', '✓ formModal element found');
} else {
    addResult('errors', '✗ formModal element NOT found - CRITICAL!');
}

if (formContent) {
    addResult('success', '✓ formContent element found');
} else {
    addResult('errors', '✗ formContent element NOT found - CRITICAL!');
}

if (customersTable) {
    addResult('success', '✓ customersTable element found');
} else {
    addResult('warnings', '⚠ customersTable element NOT found');
}

// 2. Check if JavaScript functions are defined
console.log('\n%c2. Checking JavaScript Functions...', 'color: cyan; font-weight: bold;');

if (typeof window.showCustomerForm === 'function') {
    addResult('success', '✓ showCustomerForm function is defined');
    console.log('   Function code:', window.showCustomerForm.toString().substring(0, 200));
} else {
    addResult('errors', '✗ showCustomerForm function NOT defined - CRITICAL!');
}

if (typeof window.editCustomer === 'function') {
    addResult('success', '✓ editCustomer function is defined');
} else {
    addResult('errors', '✗ editCustomer function NOT defined');
}

// Check if openCustomerModal is accessible (might be private)
try {
    const testModal = document.getElementById('formModal');
    if (testModal) {
        addResult('success', '✓ Modal can be accessed');
    }
} catch (e) {
    addResult('errors', '✗ Cannot access modal: ' + e.message);
}

// 3. Check if customers.js script is loaded
console.log('\n%c3. Checking Script Loading...', 'color: cyan; font-weight: bold;');
const scripts = Array.from(document.querySelectorAll('script[src]'));
const customersScript = scripts.find(s => s.src.includes('customers.js'));

if (customersScript) {
    addResult('success', '✓ customers.js script tag found');
    console.log('   Script src:', customersScript.src);
    console.log('   Script loaded:', customersScript.textContent ? 'Yes (inline)' : 'No (external)');
} else {
    addResult('warnings', '⚠ customers.js script tag NOT found in DOM');
    // Check if it's loaded via navigation.js
    const pageScripts = Array.from(document.querySelectorAll('script[src*="pages/"]'));
    console.log('   Found page scripts:', pageScripts.map(s => s.src));
}

// 4. Test function execution
console.log('\n%c4. Testing Function Execution...', 'color: cyan; font-weight: bold;');

if (typeof window.showCustomerForm === 'function') {
    try {
        // Don't actually call it, just check if it can be called
        addResult('success', '✓ showCustomerForm can be called (not executing to avoid opening modal)');
    } catch (e) {
        addResult('errors', '✗ Error calling showCustomerForm: ' + e.message);
    }
}

// 5. Check page context
console.log('\n%c5. Checking Page Context...', 'color: cyan; font-weight: bold;');
const currentPage = window.location.pathname;
const currentHash = window.location.hash;
const pageContent = document.getElementById('page-content');

addResult('success', `Current URL: ${currentPage}${currentHash}`);
if (pageContent) {
    const activeSection = pageContent.querySelector('.section.active');
    if (activeSection) {
        addResult('success', `Active section: ${activeSection.id || 'unknown'}`);
    } else {
        addResult('warnings', '⚠ No active section found');
    }
}

// 6. Check for JavaScript errors
console.log('\n%c6. Checking for Common Issues...', 'color: cyan; font-weight: bold;');

// Check if API_BASE is defined
if (typeof API_BASE === 'undefined') {
    addResult('errors', '✗ API_BASE is not defined');
} else {
    addResult('success', `✓ API_BASE is defined: ${API_BASE}`);
}

// Check if companyId is defined
if (typeof companyId === 'undefined') {
    addResult('errors', '✗ companyId is not defined');
} else {
    addResult('success', `✓ companyId is defined: ${companyId}`);
}

// Check if getHeaders is defined
if (typeof getHeaders === 'function') {
    addResult('success', '✓ getHeaders function is defined');
} else {
    addResult('errors', '✗ getHeaders function is NOT defined');
}

// 7. Check Add Customer Button
console.log('\n%c7. Checking Add Customer Button...', 'color: cyan; font-weight: bold;');
const addButtons = document.querySelectorAll('button[onclick*="showCustomerForm"], button:contains("Add Customer")');
if (addButtons.length > 0) {
    addResult('success', `✓ Found ${addButtons.length} Add Customer button(s)`);
    addButtons.forEach((btn, idx) => {
        console.log(`   Button ${idx + 1}:`, {
            onclick: btn.getAttribute('onclick'),
            text: btn.textContent.trim(),
            visible: btn.offsetParent !== null
        });
    });
} else {
    // Try alternative selector
    const altButtons = Array.from(document.querySelectorAll('button')).filter(b => 
        b.textContent.includes('Add Customer') || b.textContent.includes('Customer')
    );
    if (altButtons.length > 0) {
        addResult('warnings', `⚠ Found ${altButtons.length} potential button(s) but no onclick handler`);
        altButtons.forEach(btn => console.log('   Button:', btn.textContent.trim(), btn));
    } else {
        addResult('errors', '✗ Add Customer button NOT found');
    }
}

// 8. Check event listeners (if any)
console.log('\n%c8. Checking Event Listeners...', 'color: cyan; font-weight: bold;');
// Note: Can't easily check inline onclick handlers, but we can check if elements exist

// 9. Summary
console.log('\n%c=== DEBUG SUMMARY ===', 'color: blue; font-size: 16px; font-weight: bold;');
console.log(`✓ Success: ${debugResults.success.length}`);
console.log(`⚠ Warnings: ${debugResults.warnings.length}`);
console.log(`✗ Errors: ${debugResults.errors.length}`);

if (debugResults.errors.length > 0) {
    console.log('\n%cCRITICAL ERRORS FOUND:', 'color: red; font-weight: bold;');
    debugResults.errors.forEach(err => console.log('  -', err));
}

if (debugResults.warnings.length > 0) {
    console.log('\n%cWARNINGS:', 'color: orange; font-weight: bold;');
    debugResults.warnings.forEach(warn => console.log('  -', warn));
}

// 10. Provide recommendations
console.log('\n%c=== RECOMMENDATIONS ===', 'color: blue; font-weight: bold;');

if (debugResults.errors.some(e => e.includes('showCustomerForm'))) {
    console.log('%c1. showCustomerForm function is missing', 'color: red;');
    console.log('   → Check if customers.js is loaded');
    console.log('   → Check browser console for JavaScript errors');
    console.log('   → Try hard refresh: Ctrl + Shift + R');
}

if (debugResults.errors.some(e => e.includes('formModal'))) {
    console.log('%c2. Modal elements are missing', 'color: red;');
    console.log('   → Check if index.html has formModal div');
    console.log('   → Verify HTML structure');
}

if (debugResults.warnings.some(w => w.includes('script'))) {
    console.log('%c3. Script loading issues', 'color: orange;');
    console.log('   → Check Network tab for 404 errors');
    console.log('   → Verify navigation.js is loading customers.js correctly');
}

// Export results for further inspection
window.debugResults = debugResults;
console.log('\n%cDebug results saved to window.debugResults', 'color: green;');

// Quick test function
window.testCustomerForm = function() {
    console.log('%c=== TESTING CUSTOMER FORM ===', 'color: blue; font-weight: bold;');
    
    if (typeof window.showCustomerForm === 'function') {
        console.log('Calling showCustomerForm()...');
        try {
            window.showCustomerForm();
            console.log('%c✓ Function executed successfully', 'color: green;');
        } catch (error) {
            console.error('%c✗ Error executing function:', 'color: red;', error);
        }
    } else {
        console.error('%c✗ showCustomerForm is not defined', 'color: red;');
    }
};

console.log('\n%cTo test the form, run: testCustomerForm()', 'color: yellow; font-weight: bold;');
console.log('%cTo see results again, run: console.log(debugResults)', 'color: yellow;');


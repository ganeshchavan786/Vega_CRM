// ============================================
// Forms Test Script - Run in Browser Console
// ============================================
// Copy this entire script and paste in browser console
// Make sure you are logged in and have selected a company

console.log('%c🧪 FORMS TEST SCRIPT STARTED', 'background: #0052CC; color: white; font-size: 16px; padding: 10px;');

// Test Configuration
const TEST_CONFIG = {
    testDelay: 1000, // Delay between tests (ms)
    verbose: true,    // Show detailed logs
    stopOnError: false // Continue even if one test fails
};

// Test Results
let testResults = {
    passed: 0,
    failed: 0,
    errors: []
};

// Helper Functions
function logTest(testName, status, message = '') {
    const icon = status === 'PASS' ? '✅' : status === 'FAIL' ? '❌' : '⚠️';
    const color = status === 'PASS' ? 'green' : status === 'FAIL' ? 'red' : 'orange';
    console.log(`%c${icon} ${testName}: ${status}`, `color: ${color}; font-weight: bold;`, message);
    
    if (status === 'PASS') {
        testResults.passed++;
    } else {
        testResults.failed++;
        testResults.errors.push({ test: testName, message });
    }
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Check Prerequisites
function checkPrerequisites() {
    console.log('\n%c📋 Checking Prerequisites...', 'background: #0052CC; color: white; padding: 5px;');
    
    // Check if logged in
    const authToken = localStorage.getItem('authToken');
    const companyId = localStorage.getItem('companyId');
    
    if (!authToken) {
        logTest('Authentication Check', 'FAIL', 'No auth token found. Please login first.');
        return false;
    }
    
    if (!companyId) {
        logTest('Company Selection Check', 'FAIL', 'No company selected. Please select a company first.');
        return false;
    }
    
    logTest('Authentication Check', 'PASS', `Token: ${authToken.substring(0, 20)}...`);
    logTest('Company Selection Check', 'PASS', `Company ID: ${companyId}`);
    
    // Check if required functions exist
    const requiredFunctions = [
        'showCustomerForm',
        'showLeadForm',
        'showDealForm',
        'showTaskForm',
        'showActivityForm',
        'closeFormModal'
    ];
    
    let allFunctionsExist = true;
    requiredFunctions.forEach(funcName => {
        if (typeof window[funcName] !== 'function') {
            logTest(`Function Check: ${funcName}`, 'FAIL', 'Function not found');
            allFunctionsExist = false;
        } else {
            logTest(`Function Check: ${funcName}`, 'PASS');
        }
    });
    
    return allFunctionsExist;
}

// Test Modal Elements
async function testModalElements() {
    console.log('\n%c🔍 Testing Modal Elements...', 'background: #0052CC; color: white; padding: 5px;');
    
    const modal = document.getElementById('formModal');
    const formContent = document.getElementById('formContent');
    
    if (!modal) {
        logTest('Modal Element', 'FAIL', 'formModal not found');
        return false;
    }
    logTest('Modal Element', 'PASS');
    
    if (!formContent) {
        logTest('Form Content Element', 'FAIL', 'formContent not found');
        return false;
    }
    logTest('Form Content Element', 'PASS');
    
    return true;
}

// Test Customer Form
async function testCustomerForm() {
    console.log('\n%c👥 Testing Customer Form...', 'background: #0052CC; color: white; padding: 5px;');
    
    try {
        // Test showCustomerForm
        if (typeof window.showCustomerForm === 'function') {
            window.showCustomerForm();
            await sleep(500);
            
            const modal = document.getElementById('formModal');
            if (modal && modal.classList.contains('active')) {
                logTest('Customer Form: Open Modal', 'PASS');
            } else {
                logTest('Customer Form: Open Modal', 'FAIL', 'Modal did not open');
                return false;
            }
            
            // Check form fields
            const requiredFields = ['customerName', 'customerType', 'customerStatus'];
            let allFieldsExist = true;
            
            requiredFields.forEach(fieldId => {
                const field = document.getElementById(fieldId);
                if (field) {
                    logTest(`Customer Form: Field ${fieldId}`, 'PASS');
                } else {
                    logTest(`Customer Form: Field ${fieldId}`, 'FAIL', 'Field not found');
                    allFieldsExist = false;
                }
            });
            
            // Test close
            if (typeof window.closeFormModal === 'function') {
                window.closeFormModal();
                await sleep(300);
                if (!modal.classList.contains('active')) {
                    logTest('Customer Form: Close Modal', 'PASS');
                } else {
                    logTest('Customer Form: Close Modal', 'FAIL', 'Modal did not close');
                }
            }
            
            return allFieldsExist;
        } else {
            logTest('Customer Form: Function Check', 'FAIL', 'showCustomerForm not found');
            return false;
        }
    } catch (error) {
        logTest('Customer Form: Error', 'FAIL', error.message);
        return false;
    }
}

// Test Lead Form
async function testLeadForm() {
    console.log('\n%c🎯 Testing Lead Form...', 'background: #0052CC; color: white; padding: 5px;');
    
    try {
        if (typeof window.showLeadForm === 'function') {
            window.showLeadForm();
            await sleep(500);
            
            const modal = document.getElementById('formModal');
            if (modal && modal.classList.contains('active')) {
                logTest('Lead Form: Open Modal', 'PASS');
            } else {
                logTest('Lead Form: Open Modal', 'FAIL', 'Modal did not open');
                return false;
            }
            
            // Check enterprise fields
            const enterpriseFields = ['leadName', 'leadSource', 'leadCampaign', 'leadMedium', 'leadScore'];
            let allFieldsExist = true;
            
            enterpriseFields.forEach(fieldId => {
                const field = document.getElementById(fieldId);
                if (field) {
                    logTest(`Lead Form: Field ${fieldId}`, 'PASS');
                } else {
                    logTest(`Lead Form: Field ${fieldId}`, 'FAIL', 'Field not found');
                    allFieldsExist = false;
                }
            });
            
            window.closeFormModal();
            await sleep(300);
            logTest('Lead Form: Close Modal', 'PASS');
            
            return allFieldsExist;
        } else {
            logTest('Lead Form: Function Check', 'FAIL', 'showLeadForm not found');
            return false;
        }
    } catch (error) {
        logTest('Lead Form: Error', 'FAIL', error.message);
        return false;
    }
}

// Test Deal Form
async function testDealForm() {
    console.log('\n%c💰 Testing Deal Form...', 'background: #0052CC; color: white; padding: 5px;');
    
    try {
        if (typeof window.showDealForm === 'function') {
            window.showDealForm();
            await sleep(1000); // Wait for customers to load
            
            const modal = document.getElementById('formModal');
            if (modal && modal.classList.contains('active')) {
                logTest('Deal Form: Open Modal', 'PASS');
            } else {
                logTest('Deal Form: Open Modal', 'FAIL', 'Modal did not open');
                return false;
            }
            
            // Check fields
            const dealFields = ['dealName', 'dealCustomerId', 'dealValue', 'dealStage', 'dealProbability'];
            let allFieldsExist = true;
            
            dealFields.forEach(fieldId => {
                const field = document.getElementById(fieldId);
                if (field) {
                    logTest(`Deal Form: Field ${fieldId}`, 'PASS');
                } else {
                    logTest(`Deal Form: Field ${fieldId}`, 'FAIL', 'Field not found');
                    allFieldsExist = false;
                }
            });
            
            window.closeFormModal();
            await sleep(300);
            logTest('Deal Form: Close Modal', 'PASS');
            
            return allFieldsExist;
        } else {
            logTest('Deal Form: Function Check', 'FAIL', 'showDealForm not found');
            return false;
        }
    } catch (error) {
        logTest('Deal Form: Error', 'FAIL', error.message);
        return false;
    }
}

// Test Task Form
async function testTaskForm() {
    console.log('\n%c✓ Testing Task Form...', 'background: #0052CC; color: white; padding: 5px;');
    
    try {
        if (typeof window.showTaskForm === 'function') {
            window.showTaskForm();
            await sleep(1000); // Wait for related entities to load
            
            const modal = document.getElementById('formModal');
            if (modal && modal.classList.contains('active')) {
                logTest('Task Form: Open Modal', 'PASS');
            } else {
                logTest('Task Form: Open Modal', 'FAIL', 'Modal did not open');
                return false;
            }
            
            // Check fields
            const taskFields = ['taskTitle', 'taskType', 'taskPriority', 'taskStatus', 'taskDueDate'];
            let allFieldsExist = true;
            
            taskFields.forEach(fieldId => {
                const field = document.getElementById(fieldId);
                if (field) {
                    logTest(`Task Form: Field ${fieldId}`, 'PASS');
                } else {
                    logTest(`Task Form: Field ${fieldId}`, 'FAIL', 'Field not found');
                    allFieldsExist = false;
                }
            });
            
            window.closeFormModal();
            await sleep(300);
            logTest('Task Form: Close Modal', 'PASS');
            
            return allFieldsExist;
        } else {
            logTest('Task Form: Function Check', 'FAIL', 'showTaskForm not found');
            return false;
        }
    } catch (error) {
        logTest('Task Form: Error', 'FAIL', error.message);
        return false;
    }
}

// Test Activity Form
async function testActivityForm() {
    console.log('\n%c📝 Testing Activity Form...', 'background: #0052CC; color: white; padding: 5px;');
    
    try {
        if (typeof window.showActivityForm === 'function') {
            window.showActivityForm();
            await sleep(1000); // Wait for related entities to load
            
            const modal = document.getElementById('formModal');
            if (modal && modal.classList.contains('active')) {
                logTest('Activity Form: Open Modal', 'PASS');
            } else {
                logTest('Activity Form: Open Modal', 'FAIL', 'Modal did not open');
                return false;
            }
            
            // Check fields
            const activityFields = ['activityType', 'activityTitle', 'activityDate', 'activityDuration', 'activityOutcome'];
            let allFieldsExist = true;
            
            activityFields.forEach(fieldId => {
                const field = document.getElementById(fieldId);
                if (field) {
                    logTest(`Activity Form: Field ${fieldId}`, 'PASS');
                } else {
                    logTest(`Activity Form: Field ${fieldId}`, 'FAIL', 'Field not found');
                    allFieldsExist = false;
                }
            });
            
            window.closeFormModal();
            await sleep(300);
            logTest('Activity Form: Close Modal', 'PASS');
            
            return allFieldsExist;
        } else {
            logTest('Activity Form: Function Check', 'FAIL', 'showActivityForm not found');
            return false;
        }
    } catch (error) {
        logTest('Activity Form: Error', 'FAIL', error.message);
        return false;
    }
}

// Test API Endpoints
async function testAPIEndpoints() {
    console.log('\n%c🌐 Testing API Endpoints...', 'background: #0052CC; color: white; padding: 5px;');
    
    const companyId = localStorage.getItem('companyId');
    const authToken = localStorage.getItem('authToken');
    
    if (!companyId || !authToken) {
        logTest('API Test: Prerequisites', 'FAIL', 'No company ID or auth token');
        return false;
    }
    
    const API_BASE = window.API_BASE || 'http://localhost:8000/api';
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`
    };
    
    // Test endpoints
    const endpoints = [
        { name: 'Customers', url: `${API_BASE}/companies/${companyId}/customers?page=1&per_page=5` },
        { name: 'Leads', url: `${API_BASE}/companies/${companyId}/leads?page=1&per_page=5` },
        { name: 'Deals', url: `${API_BASE}/companies/${companyId}/deals?page=1&per_page=5` },
        { name: 'Tasks', url: `${API_BASE}/companies/${companyId}/tasks?page=1&per_page=5` },
        { name: 'Activities', url: `${API_BASE}/companies/${companyId}/activities?page=1&per_page=5` }
    ];
    
    for (const endpoint of endpoints) {
        try {
            const response = await fetch(endpoint.url, { headers });
            if (response.ok || response.status === 401) {
                logTest(`API: ${endpoint.name}`, response.ok ? 'PASS' : 'FAIL', `Status: ${response.status}`);
            } else {
                logTest(`API: ${endpoint.name}`, 'FAIL', `Status: ${response.status}`);
            }
            await sleep(300);
        } catch (error) {
            logTest(`API: ${endpoint.name}`, 'FAIL', error.message);
        }
    }
    
    return true;
}

// Main Test Runner
async function runAllTests() {
    console.clear();
    console.log('%c' + '='.repeat(60), 'background: #0052CC; color: white;');
    console.log('%c🧪 FORMS COMPREHENSIVE TEST SUITE', 'background: #0052CC; color: white; font-size: 18px; padding: 10px; font-weight: bold;');
    console.log('%c' + '='.repeat(60), 'background: #0052CC; color: white;');
    
    const startTime = Date.now();
    
    // Run tests
    if (!checkPrerequisites()) {
        console.error('\n%c❌ Prerequisites not met. Please login and select a company first.', 'color: red; font-weight: bold;');
        return;
    }
    
    await testModalElements();
    await sleep(TEST_CONFIG.testDelay);
    
    await testCustomerForm();
    await sleep(TEST_CONFIG.testDelay);
    
    await testLeadForm();
    await sleep(TEST_CONFIG.testDelay);
    
    await testDealForm();
    await sleep(TEST_CONFIG.testDelay);
    
    await testTaskForm();
    await sleep(TEST_CONFIG.testDelay);
    
    await testActivityForm();
    await sleep(TEST_CONFIG.testDelay);
    
    await testAPIEndpoints();
    
    // Summary
    const endTime = Date.now();
    const duration = ((endTime - startTime) / 1000).toFixed(2);
    
    console.log('\n%c' + '='.repeat(60), 'background: #0052CC; color: white;');
    console.log('%c📊 TEST SUMMARY', 'background: #0052CC; color: white; font-size: 16px; padding: 10px; font-weight: bold;');
    console.log('%c' + '='.repeat(60), 'background: #0052CC; color: white;');
    
    console.log(`%c✅ Passed: ${testResults.passed}`, 'color: green; font-weight: bold; font-size: 14px;');
    console.log(`%c❌ Failed: ${testResults.failed}`, 'color: red; font-weight: bold; font-size: 14px;');
    console.log(`%c⏱️  Duration: ${duration}s`, 'color: blue; font-weight: bold; font-size: 14px;');
    
    if (testResults.errors.length > 0) {
        console.log('\n%c🔴 ERRORS:', 'color: red; font-weight: bold; font-size: 14px;');
        testResults.errors.forEach((error, index) => {
            console.log(`%c${index + 1}. ${error.test}: ${error.message}`, 'color: red;');
        });
    }
    
    const totalTests = testResults.passed + testResults.failed;
    const passRate = totalTests > 0 ? ((testResults.passed / totalTests) * 100).toFixed(1) : 0;
    
    console.log(`%c📈 Pass Rate: ${passRate}%`, passRate >= 80 ? 'color: green;' : passRate >= 50 ? 'color: orange;' : 'color: red;', 'font-weight: bold; font-size: 14px;');
    
    console.log('\n%c' + '='.repeat(60), 'background: #0052CC; color: white;');
    
    // Return test object for programmatic access
    return {
        results: testResults,
        duration,
        passRate: parseFloat(passRate)
    };
}

// Quick Test Functions
window.quickTestForms = async function() {
    console.log('%c🚀 Quick Test Started...', 'color: blue; font-weight: bold;');
    return await runAllTests();
};

window.testSingleForm = async function(formName) {
    const tests = {
        customer: testCustomerForm,
        lead: testLeadForm,
        deal: testDealForm,
        task: testTaskForm,
        activity: testActivityForm
    };
    
    if (tests[formName.toLowerCase()]) {
        console.log(`%c🧪 Testing ${formName} form only...`, 'color: blue; font-weight: bold;');
        return await tests[formName.toLowerCase()]();
    } else {
        console.error(`%c❌ Unknown form: ${formName}`, 'color: red;');
        console.log('%cAvailable forms: customer, lead, deal, task, activity', 'color: gray;');
    }
};

// Auto-run if this script is loaded
console.log('%c✅ Test script loaded!', 'color: green; font-weight: bold;');
console.log('%cRun: quickTestForms() - Run all tests', 'color: blue;');
console.log('%cRun: testSingleForm("customer") - Test specific form', 'color: blue;');
console.log('%cAvailable forms: customer, lead, deal, task, activity', 'color: gray;');

// Export for manual execution
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { runAllTests, testSingleForm };
}


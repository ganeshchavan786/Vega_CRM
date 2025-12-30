// Account Report Page JavaScript
// Author: CRM SAAS Team

let accountsByTypeChart = null;
let accountsByLifecycleChart = null;
let accountGrowthChart = null;
let revenueReportChart = null;
let dealsByStageChart = null;
let winLossChart = null;
let leadsBySourceChart = null;
let leadsByStatusChart = null;
let leadScoreChart = null;
let activitiesByTypeChart = null;
let dailyActivityChart = null;

function initAccountreport() {
    loadReports();
    
    // Date range change handler
    const dateRange = document.getElementById('reportDateRange');
    if (dateRange) {
        dateRange.addEventListener('change', () => loadReports());
    }
}

window.switchReportTab = function(tab) {
    // Update tab buttons
    document.querySelectorAll('.report-tab').forEach(t => t.classList.remove('active'));
    document.querySelector(`.report-tab[data-tab="${tab}"]`)?.classList.add('active');
    
    // Update views
    document.querySelectorAll('.report-view').forEach(v => v.classList.remove('active'));
    document.getElementById(`${tab}ReportView`)?.classList.add('active');
    
    // Load specific report data
    switch(tab) {
        case 'areawise':
            loadAreaWiseReport();
            break;
        case 'accounts':
            loadAccountReports();
            break;
        case 'sales':
            loadSalesReports();
            break;
        case 'leads':
            loadLeadReports();
            break;
        case 'activities':
            loadActivityReports();
            break;
    }
    
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
};

window.loadReports = async function() {
    // Load Area Wise Report first (default tab)
    loadAreaWiseReport();
};

// ============================================
// Area Wise Customer Report (First Tab)
// ============================================
async function loadAreaWiseReport() {
    loadAccountLocationMap();
    loadCustomersByStateTable();
}

async function loadCustomersByStateTable() {
    const tbody = document.getElementById('customersByStateTable');
    if (!tbody) return;
    
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}/customers?limit=500`, { headers: getHeaders() });
        
        if (!response.ok) {
            tbody.innerHTML = '<tr><td colspan="5" class="loading">Unable to load data</td></tr>';
            return;
        }
        
        const result = await response.json();
        const accounts = result.data || [];
        
        // Group by state
        const stateData = {};
        
        accounts.forEach(acc => {
            const state = acc.state || getStateFromPinCode(acc.zip_code) || 'Unknown';
            const city = acc.city || 'Unknown';
            const pinCode = acc.zip_code || '';
            
            if (!stateData[state]) {
                stateData[state] = { count: 0, revenue: 0, cities: new Set(), pinCodes: new Set() };
            }
            stateData[state].count++;
            stateData[state].revenue += acc.total_revenue || 0;
            if (city !== 'Unknown') stateData[state].cities.add(city);
            if (pinCode) stateData[state].pinCodes.add(pinCode);
        });
        
        // Update summary cards
        const totalStates = Object.keys(stateData).filter(s => s !== 'Unknown').length;
        const allCities = new Set();
        const allPinCodes = new Set();
        
        Object.values(stateData).forEach(s => {
            s.cities.forEach(c => allCities.add(c));
            s.pinCodes.forEach(p => allPinCodes.add(p));
        });
        
        document.getElementById('totalStates').textContent = totalStates;
        document.getElementById('totalCities').textContent = allCities.size;
        document.getElementById('totalPinCodes').textContent = allPinCodes.size;
        document.getElementById('totalAreaCustomers').textContent = accounts.length;
        
        // Render table
        const sortedStates = Object.entries(stateData)
            .filter(([state]) => state !== 'Unknown')
            .sort((a, b) => b[1].count - a[1].count);
        
        if (sortedStates.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="loading">No state data available</td></tr>';
            return;
        }
        
        tbody.innerHTML = sortedStates.map(([state, data]) => `
            <tr>
                <td><strong>${state}</strong></td>
                <td><span class="count-badge">${data.count}</span></td>
                <td>${data.cities.size}</td>
                <td>${data.pinCodes.size}</td>
                <td>${formatCurrency(data.revenue)}</td>
            </tr>
        `).join('');
        
    } catch (error) {
        console.error('Error loading state data:', error);
        tbody.innerHTML = '<tr><td colspan="5" class="loading">Error loading data</td></tr>';
    }
}

window.exportReport = function() {
    const activeTab = document.querySelector('.report-tab.active')?.dataset.tab || 'accounts';
    alert(`Exporting ${activeTab} report... (Feature coming soon)`);
};

// ============================================
// Account Reports
// ============================================
async function loadAccountReports() {
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}/customers-stats`, { headers: getHeaders() });
        
        if (!response.ok) {
            console.error('Failed to load account stats');
            return;
        }
        
        const result = await response.json();
        const data = result.data || {};
        
        // Update summary cards
        document.getElementById('totalAccounts').textContent = data.total_customers || 0;
        document.getElementById('activeAccounts').textContent = data.active_customers || data.total_customers || 0;
        document.getElementById('newAccounts').textContent = data.new_this_month || 0;
        
        const avgHealth = data.avg_health_score || 0;
        document.getElementById('avgHealthScore').textContent = `${avgHealth}%`;
        
        // Update health distribution
        updateHealthDistribution(data);
        
        // Load charts
        loadAccountsByTypeChart(data);
        loadAccountsByLifecycleChart(data);
        loadAccountGrowthChart();
        
        // Load top accounts table
        loadTopAccountsTable();
        
    } catch (error) {
        console.error('Error loading account reports:', error);
    }
}

function updateHealthDistribution(data) {
    const green = data.health_green || data.by_health?.green || 0;
    const yellow = data.health_yellow || data.by_health?.yellow || 0;
    const red = data.health_red || data.by_health?.red || 0;
    const total = green + yellow + red || 1;
    
    document.getElementById('healthGreen').textContent = green;
    document.getElementById('healthYellow').textContent = yellow;
    document.getElementById('healthRed').textContent = red;
    
    const greenBar = document.querySelector('.health-item.green .health-bar');
    const yellowBar = document.querySelector('.health-item.yellow .health-bar');
    const redBar = document.querySelector('.health-item.red .health-bar');
    
    if (greenBar) greenBar.style.width = `${(green / total) * 100}%`;
    if (yellowBar) yellowBar.style.width = `${(yellow / total) * 100}%`;
    if (redBar) redBar.style.width = `${(red / total) * 100}%`;
}

function loadAccountsByTypeChart(data) {
    const ctx = document.getElementById('accountsByTypeChart');
    if (!ctx || typeof Chart === 'undefined') return;
    
    const types = data.by_type || { Customer: 60, Prospect: 30, Partner: 10 };
    
    if (accountsByTypeChart) accountsByTypeChart.destroy();
    
    accountsByTypeChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(types),
            datasets: [{
                data: Object.values(types),
                backgroundColor: ['#22c55e', '#3b82f6', '#f59e0b', '#8b5cf6', '#ec4899'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
}

function loadAccountsByLifecycleChart(data) {
    const ctx = document.getElementById('accountsByLifecycleChart');
    if (!ctx || typeof Chart === 'undefined') return;
    
    const lifecycle = data.by_lifecycle || { Prospect: 40, Customer: 50, Churned: 10 };
    
    if (accountsByLifecycleChart) accountsByLifecycleChart.destroy();
    
    accountsByLifecycleChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(lifecycle),
            datasets: [{
                label: 'Accounts',
                data: Object.values(lifecycle),
                backgroundColor: ['#3b82f6', '#22c55e', '#ef4444', '#64748b'],
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, grid: { color: '#f1f5f9' } },
                x: { grid: { display: false } }
            }
        }
    });
}

async function loadAccountGrowthChart() {
    const ctx = document.getElementById('accountGrowthChart');
    if (!ctx || typeof Chart === 'undefined') return;
    
    // Sample growth data
    const months = ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const growthData = [85, 92, 98, 105, 110, 120];
    
    if (accountGrowthChart) accountGrowthChart.destroy();
    
    accountGrowthChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: months,
            datasets: [{
                label: 'Total Accounts',
                data: growthData,
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                fill: true,
                tension: 0.4,
                borderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: false, grid: { color: '#f1f5f9' } },
                x: { grid: { display: false } }
            }
        }
    });
}

async function loadTopAccountsTable() {
    const tbody = document.getElementById('topAccountsTable');
    if (!tbody) return;
    
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}/customers?limit=10`, { headers: getHeaders() });
        
        if (!response.ok) {
            tbody.innerHTML = '<tr><td colspan="6" class="loading">Unable to load accounts</td></tr>';
            return;
        }
        
        const result = await response.json();
        const accounts = result.data || [];
        
        if (accounts.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="loading">No accounts found</td></tr>';
            return;
        }
        
        tbody.innerHTML = accounts.slice(0, 10).map(acc => `
            <tr>
                <td><strong>${acc.name || 'Unnamed'}</strong></td>
                <td><span class="status-badge status-${(acc.customer_type || 'customer').toLowerCase()}">${acc.customer_type || 'Customer'}</span></td>
                <td><span class="lifecycle-badge ${(acc.lifecycle_stage || 'prospect').toLowerCase()}">${acc.lifecycle_stage || 'Prospect'}</span></td>
                <td><span class="health-badge ${(acc.health_score || 'green').toLowerCase()}">${acc.health_score || 'Green'}</span></td>
                <td>${formatCurrency(acc.total_revenue || 0)}</td>
                <td>${acc.contacts_count || 0}</td>
            </tr>
        `).join('');
        
    } catch (error) {
        console.error('Error loading top accounts:', error);
        tbody.innerHTML = '<tr><td colspan="6" class="loading">Error loading accounts</td></tr>';
    }
}

// ============================================
// Sales Reports
// ============================================
async function loadSalesReports() {
    try {
        const [dealsRes, forecastRes] = await Promise.all([
            fetch(`${API_BASE}/companies/${companyId}/deals-stats`, { headers: getHeaders() }),
            fetch(`${API_BASE}/companies/${companyId}/deals/forecast`, { headers: getHeaders() })
        ]);
        
        const dealsData = dealsRes.ok ? (await dealsRes.json()).data : {};
        const forecastData = forecastRes.ok ? (await forecastRes.json()).data : {};
        
        // Update summary cards
        document.getElementById('totalRevenue').textContent = formatCurrency(forecastData.total_pipeline || dealsData.total_value || 0);
        document.getElementById('totalDeals').textContent = dealsData.total_deals || 0;
        document.getElementById('wonDeals').textContent = dealsData.by_stage?.closed_won || 0;
        
        const avgDeal = dealsData.total_deals > 0 ? (dealsData.total_value || 0) / dealsData.total_deals : 0;
        document.getElementById('avgDealSize').textContent = formatCurrency(avgDeal);
        
        // Load charts
        loadRevenueReportChart(forecastData);
        loadDealsByStageChart(dealsData);
        loadWinLossChart(dealsData);
        loadTopDealsReportTable();
        
    } catch (error) {
        console.error('Error loading sales reports:', error);
    }
}

function loadRevenueReportChart(data) {
    const ctx = document.getElementById('revenueReportChart');
    if (!ctx || typeof Chart === 'undefined') return;
    
    const months = ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const projections = data.monthly_projections || [];
    const revenueData = projections.length > 0 
        ? projections.map(p => p.projected_revenue || 0)
        : [150000, 180000, 220000, 280000, 350000, 420000];
    
    if (revenueReportChart) revenueReportChart.destroy();
    
    revenueReportChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: months,
            datasets: [{
                label: 'Revenue',
                data: revenueData,
                backgroundColor: '#22c55e',
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { 
                    beginAtZero: true,
                    ticks: { callback: v => '₹' + (v/1000) + 'K' },
                    grid: { color: '#f1f5f9' }
                },
                x: { grid: { display: false } }
            }
        }
    });
}

function loadDealsByStageChart(data) {
    const ctx = document.getElementById('dealsByStageChart');
    if (!ctx || typeof Chart === 'undefined') return;
    
    const stages = data.by_stage || { prospect: 10, qualified: 8, proposal: 5, negotiation: 3, closed_won: 2 };
    
    if (dealsByStageChart) dealsByStageChart.destroy();
    
    dealsByStageChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(stages).map(s => s.replace('_', ' ').toUpperCase()),
            datasets: [{
                data: Object.values(stages),
                backgroundColor: ['#3b82f6', '#8b5cf6', '#f59e0b', '#f97316', '#22c55e', '#ef4444'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'bottom' } }
        }
    });
}

function loadWinLossChart(data) {
    const ctx = document.getElementById('winLossChart');
    if (!ctx || typeof Chart === 'undefined') return;
    
    const won = data.by_stage?.closed_won || 0;
    const lost = data.by_stage?.closed_lost || 0;
    
    if (winLossChart) winLossChart.destroy();
    
    winLossChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Won', 'Lost'],
            datasets: [{
                data: [won || 1, lost || 1],
                backgroundColor: ['#22c55e', '#ef4444'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'bottom' } }
        }
    });
}

async function loadTopDealsReportTable() {
    const tbody = document.getElementById('topDealsReportTable');
    if (!tbody) return;
    
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}/deals?limit=10`, { headers: getHeaders() });
        
        if (!response.ok) {
            tbody.innerHTML = '<tr><td colspan="6" class="loading">Unable to load deals</td></tr>';
            return;
        }
        
        const result = await response.json();
        const deals = result.data || [];
        
        if (deals.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="loading">No deals found</td></tr>';
            return;
        }
        
        tbody.innerHTML = deals.slice(0, 10).map(deal => `
            <tr>
                <td><strong>${deal.title || deal.name || 'Untitled'}</strong></td>
                <td>${deal.customer?.name || deal.customer_name || '-'}</td>
                <td><span class="status-badge status-${(deal.stage || 'prospect').toLowerCase().replace(' ', '-')}">${deal.stage || 'Prospect'}</span></td>
                <td>${formatCurrency(deal.amount || 0)}</td>
                <td>${deal.probability || 0}%</td>
                <td>${deal.expected_close_date ? new Date(deal.expected_close_date).toLocaleDateString() : '-'}</td>
            </tr>
        `).join('');
        
    } catch (error) {
        console.error('Error loading deals:', error);
    }
}

// ============================================
// Lead Reports
// ============================================
async function loadLeadReports() {
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}/leads-stats`, { headers: getHeaders() });
        
        const data = response.ok ? (await response.json()).data : {};
        
        // Update summary cards
        document.getElementById('totalLeadsReport').textContent = data.total_leads || 0;
        document.getElementById('qualifiedLeads').textContent = data.qualified_leads || data.by_status?.qualified || 0;
        document.getElementById('convertedLeads').textContent = data.converted_leads || data.by_status?.converted || 0;
        
        const total = data.total_leads || 1;
        const converted = data.converted_leads || data.by_status?.converted || 0;
        const rate = Math.round((converted / total) * 100);
        document.getElementById('conversionRateReport').textContent = `${rate}%`;
        
        // Load charts
        loadLeadsBySourceChart(data);
        loadLeadsByStatusChart(data);
        loadLeadScoreChart(data);
        loadTopLeadsTable();
        
    } catch (error) {
        console.error('Error loading lead reports:', error);
    }
}

function loadLeadsBySourceChart(data) {
    const ctx = document.getElementById('leadsBySourceChart');
    if (!ctx || typeof Chart === 'undefined') return;
    
    const sources = data.by_source || { Website: 35, Referral: 25, Social: 20, Direct: 15, Other: 5 };
    
    if (leadsBySourceChart) leadsBySourceChart.destroy();
    
    leadsBySourceChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(sources),
            datasets: [{
                data: Object.values(sources),
                backgroundColor: ['#3b82f6', '#22c55e', '#f59e0b', '#8b5cf6', '#ec4899'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'bottom' } }
        }
    });
}

function loadLeadsByStatusChart(data) {
    const ctx = document.getElementById('leadsByStatusChart');
    if (!ctx || typeof Chart === 'undefined') return;
    
    const statuses = data.by_status || { new: 20, contacted: 15, qualified: 10, converted: 5 };
    
    if (leadsByStatusChart) leadsByStatusChart.destroy();
    
    leadsByStatusChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(statuses).map(s => s.toUpperCase()),
            datasets: [{
                label: 'Leads',
                data: Object.values(statuses),
                backgroundColor: ['#3b82f6', '#f59e0b', '#22c55e', '#8b5cf6'],
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, grid: { color: '#f1f5f9' } },
                x: { grid: { display: false } }
            }
        }
    });
}

function loadLeadScoreChart(data) {
    const ctx = document.getElementById('leadScoreChart');
    if (!ctx || typeof Chart === 'undefined') return;
    
    const scores = data.by_score || { '0-25': 10, '26-50': 15, '51-75': 20, '76-100': 8 };
    
    if (leadScoreChart) leadScoreChart.destroy();
    
    leadScoreChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(scores),
            datasets: [{
                label: 'Leads',
                data: Object.values(scores),
                backgroundColor: ['#ef4444', '#f59e0b', '#22c55e', '#3b82f6'],
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, grid: { color: '#f1f5f9' } },
                x: { grid: { display: false } }
            }
        }
    });
}

async function loadTopLeadsTable() {
    const tbody = document.getElementById('topLeadsTable');
    if (!tbody) return;
    
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}/leads?limit=10&sort=-score`, { headers: getHeaders() });
        
        if (!response.ok) {
            tbody.innerHTML = '<tr><td colspan="6" class="loading">Unable to load leads</td></tr>';
            return;
        }
        
        const result = await response.json();
        const leads = result.data || [];
        
        if (leads.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="loading">No leads found</td></tr>';
            return;
        }
        
        tbody.innerHTML = leads.slice(0, 10).map(lead => `
            <tr>
                <td><strong>${lead.first_name || ''} ${lead.last_name || ''}</strong></td>
                <td>${lead.company_name || '-'}</td>
                <td>${lead.source || '-'}</td>
                <td><span class="status-badge status-${(lead.status || 'new').toLowerCase()}">${lead.status || 'New'}</span></td>
                <td><span class="score-badge score-${getScoreLevel(lead.score)}">${lead.score || 0}</span></td>
                <td>${lead.created_at ? new Date(lead.created_at).toLocaleDateString() : '-'}</td>
            </tr>
        `).join('');
        
    } catch (error) {
        console.error('Error loading leads:', error);
    }
}

// ============================================
// Activity Reports
// ============================================
async function loadActivityReports() {
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}/activities?limit=100`, { headers: getHeaders() });
        
        const result = response.ok ? await response.json() : { data: [] };
        const activities = result.data || [];
        
        // Count by type
        const calls = activities.filter(a => a.activity_type?.toLowerCase() === 'call').length;
        const emails = activities.filter(a => a.activity_type?.toLowerCase() === 'email').length;
        const meetings = activities.filter(a => a.activity_type?.toLowerCase() === 'meeting').length;
        
        // Update summary cards
        document.getElementById('totalActivities').textContent = activities.length;
        document.getElementById('totalCalls').textContent = calls;
        document.getElementById('totalEmails').textContent = emails;
        document.getElementById('totalMeetings').textContent = meetings;
        
        // Load charts
        loadActivitiesByTypeChart({ call: calls, email: emails, meeting: meetings, note: activities.length - calls - emails - meetings });
        loadDailyActivityChart(activities);
        loadTeamActivityTable();
        
    } catch (error) {
        console.error('Error loading activity reports:', error);
    }
}

function loadActivitiesByTypeChart(data) {
    const ctx = document.getElementById('activitiesByTypeChart');
    if (!ctx || typeof Chart === 'undefined') return;
    
    if (activitiesByTypeChart) activitiesByTypeChart.destroy();
    
    activitiesByTypeChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Calls', 'Emails', 'Meetings', 'Notes'],
            datasets: [{
                data: [data.call || 0, data.email || 0, data.meeting || 0, data.note || 0],
                backgroundColor: ['#3b82f6', '#8b5cf6', '#22c55e', '#f59e0b'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'bottom' } }
        }
    });
}

function loadDailyActivityChart(activities) {
    const ctx = document.getElementById('dailyActivityChart');
    if (!ctx || typeof Chart === 'undefined') return;
    
    // Group by day (last 7 days)
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const dayCounts = [0, 0, 0, 0, 0, 0, 0];
    
    activities.forEach(a => {
        if (a.activity_date) {
            const day = new Date(a.activity_date).getDay();
            dayCounts[day]++;
        }
    });
    
    if (dailyActivityChart) dailyActivityChart.destroy();
    
    dailyActivityChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: days,
            datasets: [{
                label: 'Activities',
                data: dayCounts,
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                fill: true,
                tension: 0.4,
                borderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, grid: { color: '#f1f5f9' } },
                x: { grid: { display: false } }
            }
        }
    });
}

async function loadTeamActivityTable() {
    const tbody = document.getElementById('teamActivityTable');
    if (!tbody) return;
    
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}/users`, { headers: getHeaders() });
        
        if (!response.ok) {
            tbody.innerHTML = '<tr><td colspan="6" class="loading">Unable to load team</td></tr>';
            return;
        }
        
        const result = await response.json();
        const users = result.data || [];
        
        if (users.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="loading">No team members found</td></tr>';
            return;
        }
        
        // Sample activity counts per user
        tbody.innerHTML = users.slice(0, 10).map(user => {
            const calls = Math.floor(Math.random() * 20);
            const emails = Math.floor(Math.random() * 30);
            const meetings = Math.floor(Math.random() * 10);
            const notes = Math.floor(Math.random() * 15);
            return `
                <tr>
                    <td><strong>${user.name || user.email}</strong></td>
                    <td>${calls}</td>
                    <td>${emails}</td>
                    <td>${meetings}</td>
                    <td>${notes}</td>
                    <td><strong>${calls + emails + meetings + notes}</strong></td>
                </tr>
            `;
        }).join('');
        
    } catch (error) {
        console.error('Error loading team activity:', error);
    }
}

// ============================================
// Account Location Map Functions
// ============================================

// India City Coordinates (lat, lng)
const cityCoordinates = {
    // Maharashtra
    'Mumbai': { lat: 19.0760, lng: 72.8777 },
    'Pune': { lat: 18.5204, lng: 73.8567 },
    'Nagpur': { lat: 21.1458, lng: 79.0882 },
    'Nashik': { lat: 19.9975, lng: 73.7898 },
    'Thane': { lat: 19.2183, lng: 72.9781 },
    // Karnataka
    'Bangalore': { lat: 12.9716, lng: 77.5946 },
    'Bengaluru': { lat: 12.9716, lng: 77.5946 },
    'Mysore': { lat: 12.2958, lng: 76.6394 },
    'Hubli': { lat: 15.3647, lng: 75.1240 },
    // Tamil Nadu
    'Chennai': { lat: 13.0827, lng: 80.2707 },
    'Coimbatore': { lat: 11.0168, lng: 76.9558 },
    'Madurai': { lat: 9.9252, lng: 78.1198 },
    // Telangana
    'Hyderabad': { lat: 17.3850, lng: 78.4867 },
    'Secunderabad': { lat: 17.4399, lng: 78.4983 },
    'Warangal': { lat: 17.9784, lng: 79.5941 },
    // Andhra Pradesh
    'Visakhapatnam': { lat: 17.6868, lng: 83.2185 },
    'Vijayawada': { lat: 16.5062, lng: 80.6480 },
    'Tirupati': { lat: 13.6288, lng: 79.4192 },
    // Gujarat
    'Ahmedabad': { lat: 23.0225, lng: 72.5714 },
    'Surat': { lat: 21.1702, lng: 72.8311 },
    'Vadodara': { lat: 22.3072, lng: 73.1812 },
    'Rajkot': { lat: 22.3039, lng: 70.8022 },
    // Delhi NCR
    'Delhi': { lat: 28.6139, lng: 77.2090 },
    'New Delhi': { lat: 28.6139, lng: 77.2090 },
    'Noida': { lat: 28.5355, lng: 77.3910 },
    'Gurgaon': { lat: 28.4595, lng: 77.0266 },
    'Gurugram': { lat: 28.4595, lng: 77.0266 },
    'Faridabad': { lat: 28.4089, lng: 77.3178 },
    // Rajasthan
    'Jaipur': { lat: 26.9124, lng: 75.7873 },
    'Jodhpur': { lat: 26.2389, lng: 73.0243 },
    'Udaipur': { lat: 24.5854, lng: 73.7125 },
    // Uttar Pradesh
    'Lucknow': { lat: 26.8467, lng: 80.9462 },
    'Kanpur': { lat: 26.4499, lng: 80.3319 },
    'Varanasi': { lat: 25.3176, lng: 82.9739 },
    'Agra': { lat: 27.1767, lng: 78.0081 },
    // West Bengal
    'Kolkata': { lat: 22.5726, lng: 88.3639 },
    'Howrah': { lat: 22.5958, lng: 88.2636 },
    // Kerala
    'Kochi': { lat: 9.9312, lng: 76.2673 },
    'Thiruvananthapuram': { lat: 8.5241, lng: 76.9366 },
    'Kozhikode': { lat: 11.2588, lng: 75.7804 },
    'Ernakulam': { lat: 9.9816, lng: 76.2999 },
    // Punjab
    'Chandigarh': { lat: 30.7333, lng: 76.7794 },
    'Ludhiana': { lat: 30.9010, lng: 75.8573 },
    'Amritsar': { lat: 31.6340, lng: 74.8723 },
    // Madhya Pradesh
    'Indore': { lat: 22.7196, lng: 75.8577 },
    'Bhopal': { lat: 23.2599, lng: 77.4126 },
    // Bihar
    'Patna': { lat: 25.5941, lng: 85.1376 },
    // Odisha
    'Bhubaneswar': { lat: 20.2961, lng: 85.8245 },
    // Assam
    'Guwahati': { lat: 26.1445, lng: 91.7362 },
    // Goa
    'Panaji': { lat: 15.4909, lng: 73.8278 },
    // Jharkhand
    'Ranchi': { lat: 23.3441, lng: 85.3096 },
    'Jamshedpur': { lat: 22.8046, lng: 86.2029 }
};

// Marker colors based on count
const markerColors = ['#ef4444', '#f97316', '#f59e0b', '#22c55e', '#3b82f6', '#8b5cf6', '#ec4899', '#06b6d4'];

let indiaMap = null;

// Pin code to State mapping (first 2 digits)
const pinCodeToState = {
    '11': 'Delhi', '12': 'Haryana', '13': 'Haryana', '14': 'Punjab', '15': 'Punjab',
    '16': 'Punjab', '17': 'Himachal Pradesh', '18': 'Jammu & Kashmir', '19': 'Jammu & Kashmir',
    '20': 'Uttar Pradesh', '21': 'Uttar Pradesh', '22': 'Uttar Pradesh', '23': 'Uttar Pradesh',
    '24': 'Uttar Pradesh', '25': 'Uttar Pradesh', '26': 'Uttar Pradesh', '27': 'Uttar Pradesh', '28': 'Uttar Pradesh',
    '30': 'Rajasthan', '31': 'Rajasthan', '32': 'Rajasthan', '33': 'Rajasthan', '34': 'Rajasthan',
    '36': 'Gujarat', '37': 'Gujarat', '38': 'Gujarat', '39': 'Gujarat',
    '40': 'Maharashtra', '41': 'Maharashtra', '42': 'Maharashtra', '43': 'Maharashtra', '44': 'Maharashtra',
    '45': 'Madhya Pradesh', '46': 'Madhya Pradesh', '47': 'Madhya Pradesh', '48': 'Madhya Pradesh', '49': 'Chhattisgarh',
    '50': 'Telangana', '51': 'Telangana', '52': 'Andhra Pradesh', '53': 'Andhra Pradesh',
    '56': 'Karnataka', '57': 'Karnataka', '58': 'Karnataka', '59': 'Karnataka',
    '60': 'Tamil Nadu', '61': 'Tamil Nadu', '62': 'Tamil Nadu', '63': 'Tamil Nadu', '64': 'Tamil Nadu',
    '67': 'Kerala', '68': 'Kerala', '69': 'Kerala',
    '70': 'West Bengal', '71': 'West Bengal', '72': 'West Bengal', '73': 'West Bengal', '74': 'West Bengal',
    '75': 'Odisha', '76': 'Odisha', '77': 'Odisha',
    '78': 'Assam', '79': 'Northeast',
    '80': 'Bihar', '81': 'Bihar', '82': 'Bihar', '83': 'Jharkhand', '84': 'Jharkhand', '85': 'Jharkhand'
};

async function loadAccountLocationMap() {
    const mapContainer = document.getElementById('indiaLeafletMap');
    const legendContainer = document.getElementById('stateLegend');
    const cityTable = document.getElementById('accountsByCityTable');
    
    if (!mapContainer || !legendContainer) return;
    
    try {
        // Fetch all accounts with location data
        const response = await fetch(`${API_BASE}/companies/${companyId}/customers?limit=500`, { headers: getHeaders() });
        
        if (!response.ok) {
            mapContainer.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#64748b;">Unable to load map data</div>';
            return;
        }
        
        const result = await response.json();
        const accounts = result.data || [];
        
        // Group accounts by city
        const cityData = {};
        
        accounts.forEach(acc => {
            const city = acc.city || 'Unknown';
            const state = acc.state || getStateFromPinCode(acc.zip_code) || 'Unknown';
            const pinCode = acc.zip_code || '';
            
            if (city === 'Unknown') return;
            
            const cityKey = city;
            if (!cityData[cityKey]) {
                cityData[cityKey] = { 
                    city, 
                    state, 
                    pinCode, 
                    count: 0, 
                    revenue: 0,
                    coords: cityCoordinates[city] || null
                };
            }
            cityData[cityKey].count++;
            cityData[cityKey].revenue += acc.total_revenue || 0;
            if (pinCode && !cityData[cityKey].pinCode) {
                cityData[cityKey].pinCode = pinCode;
            }
        });
        
        // Initialize Leaflet map
        initLeafletMap(mapContainer, cityData);
        
        // Render city legend
        renderCityLegend(cityData, legendContainer);
        
        // Render city table
        renderCityTable(cityData, cityTable);
        
        // Reinitialize icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
        
    } catch (error) {
        console.error('Error loading map data:', error);
        mapContainer.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#64748b;">Error loading map data</div>';
    }
}

function initLeafletMap(container, cityData) {
    // Destroy existing map if any
    if (indiaMap) {
        indiaMap.remove();
        indiaMap = null;
    }
    
    // Check if Leaflet is loaded
    if (typeof L === 'undefined') {
        container.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#64748b;">Map library not loaded</div>';
        return;
    }
    
    // Initialize map centered on India
    indiaMap = L.map(container, {
        center: [20.5937, 78.9629], // India center
        zoom: 5,
        minZoom: 4,
        maxZoom: 10,
        scrollWheelZoom: true
    });
    
    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(indiaMap);
    
    // Add city markers
    const sortedCities = Object.values(cityData)
        .filter(c => c.coords)
        .sort((a, b) => b.count - a.count);
    
    sortedCities.forEach((city, index) => {
        if (!city.coords) return;
        
        // Determine marker size based on count
        let size = 24;
        if (city.count >= 10) size = 48;
        else if (city.count >= 5) size = 36;
        else if (city.count >= 2) size = 30;
        
        // Create custom icon
        const color = markerColors[index % markerColors.length];
        const icon = L.divIcon({
            className: 'custom-marker',
            html: `<div style="
                width: ${size}px;
                height: ${size}px;
                background: ${color};
                border: 3px solid white;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: 700;
                font-size: ${size > 30 ? 14 : 11}px;
                box-shadow: 0 3px 10px rgba(0,0,0,0.3);
            ">${city.count}</div>`,
            iconSize: [size, size],
            iconAnchor: [size/2, size/2]
        });
        
        // Add marker
        const marker = L.marker([city.coords.lat, city.coords.lng], { icon })
            .addTo(indiaMap);
        
        // Add popup
        marker.bindPopup(`
            <div class="map-popup">
                <h4>${city.city}</h4>
                <p>${city.state}</p>
                <div class="popup-count">${city.count} Customers</div>
                <p>Revenue: ${formatCurrency(city.revenue)}</p>
            </div>
        `);
    });
    
    // Fit bounds to show all markers
    if (sortedCities.length > 0) {
        const bounds = sortedCities
            .filter(c => c.coords)
            .map(c => [c.coords.lat, c.coords.lng]);
        if (bounds.length > 0) {
            indiaMap.fitBounds(bounds, { padding: [50, 50] });
        }
    }
}

function renderCityLegend(cityData, container) {
    const sortedCities = Object.values(cityData)
        .filter(c => c.city !== 'Unknown')
        .sort((a, b) => b.count - a.count);
    
    if (sortedCities.length === 0) {
        container.innerHTML = '<div class="legend-item"><span class="legend-state">No city data available</span></div>';
        return;
    }
    
    container.innerHTML = sortedCities.slice(0, 10).map((city, index) => `
        <div class="legend-item" onclick="focusCity('${city.city}')">
            <div class="legend-color" style="background: ${markerColors[index % markerColors.length]}"></div>
            <div class="legend-info">
                <span class="legend-state">${city.city}</span>
                <span class="legend-count">${city.count} customers</span>
            </div>
            <span class="legend-value">${formatCurrency(city.revenue)}</span>
        </div>
    `).join('');
}

window.focusCity = function(cityName) {
    const coords = cityCoordinates[cityName];
    if (coords && indiaMap) {
        indiaMap.setView([coords.lat, coords.lng], 8);
    }
};

function getStateFromPinCode(pinCode) {
    if (!pinCode) return null;
    const prefix = pinCode.toString().substring(0, 2);
    return pinCodeToState[prefix] || null;
}

function renderStateLegend(stateData, container) {
    const sortedStates = Object.entries(stateData)
        .filter(([state]) => state !== 'Unknown')
        .sort((a, b) => b[1].count - a[1].count);
    
    if (sortedStates.length === 0) {
        container.innerHTML = '<div class="legend-item"><span class="legend-state">No location data available</span></div>';
        return;
    }
    
    const colors = ['#22c55e', '#3b82f6', '#8b5cf6', '#f59e0b', '#ec4899', '#06b6d4', '#f97316', '#6366f1', '#84cc16', '#a855f7'];
    
    container.innerHTML = sortedStates.map(([state, data], index) => `
        <div class="legend-item" onclick="highlightState('${state}')">
            <div class="legend-color" style="background: ${colors[index % colors.length]}"></div>
            <div class="legend-info">
                <span class="legend-state">${state}</span>
                <span class="legend-count">${data.count} accounts</span>
            </div>
            <span class="legend-value">${formatCurrency(data.revenue)}</span>
        </div>
    `).join('');
}

function renderMapMarkers(stateData) {
    const mapWrapper = document.querySelector('.india-map-wrapper');
    if (!mapWrapper) return;
    
    // Remove existing markers
    mapWrapper.querySelectorAll('.state-marker').forEach(m => m.remove());
    
    // Add markers for states with accounts
    Object.entries(stateData).forEach(([state, data]) => {
        if (state === 'Unknown') return;
        
        const coords = stateCoordinates[state];
        if (!coords) return;
        
        const marker = document.createElement('div');
        marker.className = 'state-marker';
        marker.style.left = `${(coords.x / 600) * 100}%`;
        marker.style.top = `${(coords.y / 700) * 100}%`;
        marker.innerHTML = `
            <div class="marker-dot" style="background: linear-gradient(135deg, ${coords.color}, ${coords.color}dd)">${data.count}</div>
            <div class="marker-label">${state}</div>
        `;
        marker.onclick = () => highlightState(state);
        mapWrapper.appendChild(marker);
    });
}

function renderMapStats(stateData, cityData, pinCodes, container) {
    if (!container) return;
    
    const stateCount = Object.keys(stateData).filter(s => s !== 'Unknown').length;
    const cityCount = Object.keys(cityData).length;
    const pinCodeCount = pinCodes.size;
    const totalAccounts = Object.values(stateData).reduce((sum, s) => sum + s.count, 0);
    
    container.innerHTML = `
        <div class="map-stat-card">
            <div class="map-stat-icon states"><i data-lucide="map"></i></div>
            <span class="map-stat-value">${stateCount}</span>
            <span class="map-stat-label">States Covered</span>
        </div>
        <div class="map-stat-card">
            <div class="map-stat-icon cities"><i data-lucide="building-2"></i></div>
            <span class="map-stat-value">${cityCount}</span>
            <span class="map-stat-label">Cities</span>
        </div>
        <div class="map-stat-card">
            <div class="map-stat-icon pincodes"><i data-lucide="map-pin"></i></div>
            <span class="map-stat-value">${pinCodeCount}</span>
            <span class="map-stat-label">Pin Codes</span>
        </div>
        <div class="map-stat-card">
            <div class="map-stat-icon coverage"><i data-lucide="users"></i></div>
            <span class="map-stat-value">${totalAccounts}</span>
            <span class="map-stat-label">Total Accounts</span>
        </div>
    `;
}

function renderCityTable(cityData, tbody) {
    if (!tbody) return;
    
    const sortedCities = Object.values(cityData)
        .filter(c => c.city !== 'Unknown')
        .sort((a, b) => b.count - a.count);
    
    if (sortedCities.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="loading">No city data available</td></tr>';
        return;
    }
    
    tbody.innerHTML = sortedCities.slice(0, 15).map(city => `
        <tr>
            <td><strong>${city.city}</strong></td>
            <td>${city.state}</td>
            <td><span class="pincode-badge">${city.pinCode || '-'}</span></td>
            <td><span class="count-badge">${city.count}</span></td>
            <td>${formatCurrency(city.revenue)}</td>
        </tr>
    `).join('');
}

window.highlightState = function(state) {
    // Highlight the selected state in legend
    document.querySelectorAll('.legend-item').forEach(item => {
        item.style.background = item.textContent.includes(state) ? '#e2e8f0' : '#f8fafc';
    });
    
    // Highlight marker
    document.querySelectorAll('.state-marker').forEach(marker => {
        const isSelected = marker.textContent.includes(state);
        marker.style.transform = isSelected ? 'translate(-50%, -50%) scale(1.2)' : 'translate(-50%, -50%)';
        marker.style.zIndex = isSelected ? '20' : '10';
    });
};

// ============================================
// Helper Functions
// ============================================
function formatCurrency(value) {
    if (value >= 10000000) return '₹' + (value / 10000000).toFixed(1) + 'Cr';
    if (value >= 100000) return '₹' + (value / 100000).toFixed(1) + 'L';
    if (value >= 1000) return '₹' + (value / 1000).toFixed(0) + 'K';
    return '₹' + value;
}

function getScoreLevel(score) {
    if (score >= 75) return 'high';
    if (score >= 50) return 'medium';
    return 'low';
}

// ============================================
// Export to Excel/CSV Functionality
// ============================================

window.exportReport = async function() {
    const activeTab = document.querySelector('.report-tab.active')?.dataset.tab || 'leads';
    
    let data = [];
    let filename = 'report';
    let headers = [];
    
    try {
        switch(activeTab) {
            case 'leads':
                data = await fetchLeadsForExport();
                headers = ['Name', 'Email', 'Phone', 'Company', 'Source', 'Status', 'Score', 'Created'];
                filename = 'leads_report';
                break;
            case 'sales':
                data = await fetchDealsForExport();
                headers = ['Deal Name', 'Account', 'Stage', 'Value', 'Probability', 'Close Date'];
                filename = 'sales_report';
                break;
            case 'accounts':
                data = await fetchCustomersForExport();
                headers = ['Name', 'Email', 'Phone', 'Type', 'Status', 'Lifecycle', 'Health Score'];
                filename = 'accounts_report';
                break;
            case 'activities':
                data = await fetchActivitiesForExport();
                headers = ['Type', 'Subject', 'Related To', 'Date', 'Created By'];
                filename = 'activities_report';
                break;
            case 'areawise':
                data = await fetchAreaWiseForExport();
                headers = ['City', 'State', 'Pin Code', 'Customers', 'Revenue'];
                filename = 'areawise_report';
                break;
        }
        
        if (data.length === 0) {
            showToast('No data to export', 'warning');
            return;
        }
        
        // Generate CSV
        const csv = generateCSV(headers, data);
        downloadCSV(csv, filename);
        
        showToast(`Exported ${data.length} records`, 'success');
        
    } catch (error) {
        console.error('Export error:', error);
        showToast('Failed to export report', 'error');
    }
};

async function fetchLeadsForExport() {
    const response = await fetch(`${API_BASE}/companies/${companyId}/leads?per_page=1000`, { headers: getHeaders() });
    if (!response.ok) return [];
    const result = await response.json();
    const leads = result.data || [];
    
    return leads.map(l => [
        `${l.first_name || ''} ${l.last_name || ''}`.trim() || l.lead_name || '-',
        l.email || '-',
        l.phone || '-',
        l.company_name || '-',
        l.source || '-',
        l.status || '-',
        l.lead_score || '-',
        l.created_at ? new Date(l.created_at).toLocaleDateString() : '-'
    ]);
}

async function fetchDealsForExport() {
    const response = await fetch(`${API_BASE}/companies/${companyId}/deals?per_page=1000`, { headers: getHeaders() });
    if (!response.ok) return [];
    const result = await response.json();
    const deals = result.data || [];
    
    return deals.map(d => [
        d.name || '-',
        d.customer_name || '-',
        d.stage || '-',
        d.value || 0,
        d.probability || 0,
        d.expected_close_date ? new Date(d.expected_close_date).toLocaleDateString() : '-'
    ]);
}

async function fetchCustomersForExport() {
    const response = await fetch(`${API_BASE}/companies/${companyId}/customers?per_page=1000`, { headers: getHeaders() });
    if (!response.ok) return [];
    const result = await response.json();
    const customers = result.data || [];
    
    return customers.map(c => [
        c.name || '-',
        c.email || '-',
        c.phone || '-',
        c.customer_type || '-',
        c.status || '-',
        c.lifecycle_stage || '-',
        c.health_score || '-'
    ]);
}

async function fetchActivitiesForExport() {
    const response = await fetch(`${API_BASE}/companies/${companyId}/activities?per_page=1000`, { headers: getHeaders() });
    if (!response.ok) return [];
    const result = await response.json();
    const activities = result.data || [];
    
    return activities.map(a => [
        a.activity_type || '-',
        a.subject || '-',
        a.related_to || '-',
        a.created_at ? new Date(a.created_at).toLocaleDateString() : '-',
        a.created_by_name || '-'
    ]);
}

async function fetchAreaWiseForExport() {
    const response = await fetch(`${API_BASE}/companies/${companyId}/customers?per_page=1000`, { headers: getHeaders() });
    if (!response.ok) return [];
    const result = await response.json();
    const customers = result.data || [];
    
    // Group by city
    const cityData = {};
    customers.forEach(c => {
        const city = c.city || 'Unknown';
        if (!cityData[city]) {
            cityData[city] = { city, state: c.state || '-', pinCode: c.zip_code || '-', count: 0, revenue: 0 };
        }
        cityData[city].count++;
        cityData[city].revenue += c.total_revenue || 0;
    });
    
    return Object.values(cityData).map(c => [
        c.city,
        c.state,
        c.pinCode,
        c.count,
        c.revenue
    ]);
}

function generateCSV(headers, data) {
    const escape = (val) => {
        if (val === null || val === undefined) return '';
        const str = String(val);
        if (str.includes(',') || str.includes('"') || str.includes('\n')) {
            return '"' + str.replace(/"/g, '""') + '"';
        }
        return str;
    };
    
    const headerRow = headers.map(escape).join(',');
    const dataRows = data.map(row => row.map(escape).join(','));
    
    return [headerRow, ...dataRows].join('\n');
}

function downloadCSV(csv, filename) {
    const BOM = '\uFEFF'; // UTF-8 BOM for Excel
    const blob = new Blob([BOM + csv], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${filename}_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
}

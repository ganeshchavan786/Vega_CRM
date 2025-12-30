// Dashboard Page JavaScript - Ultimate BI Analytics

let revenueTrendChart = null;
let leadSourcesChart = null;

function initDashboard() {
    // Ensure navbar is loaded and visible
    const navbarContainer = document.getElementById('navbar-container');
    if (navbarContainer) {
        if (!navbarContainer.innerHTML.trim() || !navbarContainer.querySelector('.navbar-advanced, .navbar')) {
            loadNavigation().then(() => {
                navbarContainer.style.display = 'block';
                navbarContainer.style.visibility = 'visible';
                navbarContainer.style.opacity = '1';
                navbarContainer.style.background = '#0052CC';
                
                // Force navbar element visibility
                const navElement = navbarContainer.querySelector('.navbar-advanced, .navbar');
                if (navElement) {
                    navElement.style.display = 'block';
                    navElement.style.visibility = 'visible';
                    navElement.style.background = 'linear-gradient(135deg, #0052CC 0%, #0065FF 100%)';
                    navElement.style.backgroundColor = '#0052CC';
                }
            });
        } else {
            navbarContainer.style.display = 'block';
            navbarContainer.style.visibility = 'visible';
            navbarContainer.style.opacity = '1';
            navbarContainer.style.background = '#0052CC';
            
            // Force navbar element visibility
            const navElement = navbarContainer.querySelector('.navbar-advanced, .navbar');
            if (navElement) {
                navElement.style.display = 'block';
                navElement.style.visibility = 'visible';
                navElement.style.background = 'linear-gradient(135deg, #0052CC 0%, #0065FF 100%)';
                navElement.style.backgroundColor = '#0052CC';
            }
        }
    }
    
    // Initialize date filter buttons
    initDateFilters();
    
    // Load dashboard data
    loadBIDashboard();
}

window.loadDashboard = async function() {
    try {
        // Refresh companyId from localStorage
        const storedCompanyId = localStorage.getItem('companyId');
        if (storedCompanyId) {
            companyId = storedCompanyId;
        }
        
        if (!companyId) {
            console.error('Company ID not set');
            if (typeof loadPage === 'function') {
                loadPage('company-selection');
            }
            return;
        }

        // Ensure companyId is a number
        const companyIdNum = parseInt(companyId);
        if (isNaN(companyIdNum)) {
            console.error('Invalid company ID');
            return;
        }

        // Load stats
        const [customersRes, leadsRes, dealsRes, tasksRes, activitiesRes] = await Promise.all([
            fetch(`${API_BASE}/companies/${companyIdNum}/customers-stats`, {
                headers: getHeaders()
            }),
            fetch(`${API_BASE}/companies/${companyIdNum}/leads-stats`, {
                headers: getHeaders()
            }),
            fetch(`${API_BASE}/companies/${companyIdNum}/deals-stats`, {
                headers: getHeaders()
            }),
            fetch(`${API_BASE}/companies/${companyIdNum}/tasks-stats`, {
                headers: getHeaders()
            }),
            fetch(`${API_BASE}/companies/${companyIdNum}/activities/timeline?limit=10`, {
                headers: getHeaders()
            })
        ]);

        // Check for 401 errors (unauthorized)
        if (customersRes.status === 401 || leadsRes.status === 401 || dealsRes.status === 401 || 
            tasksRes.status === 401 || activitiesRes.status === 401) {
            if (typeof handle401Error === 'function') {
                handle401Error();
            } else {
                console.error('401 Unauthorized - please login again');
                if (typeof loadPage === 'function') {
                    loadPage('home');
                }
            }
            return;
        }
        
        // Check for other errors
        if (!customersRes.ok) {
            console.error('Customers stats error:', customersRes.status, await customersRes.text());
        }
        if (!leadsRes.ok) {
            console.error('Leads stats error:', leadsRes.status, await leadsRes.text());
        }
        if (!dealsRes.ok) {
            console.error('Deals stats error:', dealsRes.status, await dealsRes.text());
        }
        if (!tasksRes.ok) {
            console.error('Tasks stats error:', tasksRes.status, await tasksRes.text());
        }
        if (!activitiesRes.ok) {
            console.error('Activities timeline error:', activitiesRes.status, await activitiesRes.text());
        }

        const customersData = customersRes.ok ? await customersRes.json() : { data: { total_customers: 0 } };
        const leadsData = leadsRes.ok ? await leadsRes.json() : { data: { total_leads: 0 } };
        const dealsData = dealsRes.ok ? await dealsRes.json() : { data: { total_deals: 0 } };
        const tasksData = tasksRes.ok ? await tasksRes.json() : { data: { total_tasks: 0 } };
        const activitiesData = activitiesRes.ok ? await activitiesRes.json() : { data: [] };

        // Update stats
        const statCustomers = document.getElementById('statCustomers');
        const statLeads = document.getElementById('statLeads');
        const statDeals = document.getElementById('statDeals');
        const statTasks = document.getElementById('statTasks');

        if (statCustomers) statCustomers.textContent = customersData.data?.total_customers || 0;
        if (statLeads) statLeads.textContent = leadsData.data?.total_leads || 0;
        if (statDeals) statDeals.textContent = dealsData.data?.total_deals || 0;
        if (statTasks) statTasks.textContent = tasksData.data?.total_tasks || 0;

        // Recent activities
        const activitiesList = document.getElementById('recentActivities');
        if (activitiesList) {
            if (activitiesData.data && activitiesData.data.length > 0) {
                activitiesList.innerHTML = activitiesData.data.map(activity => `
                    <div class="activity-item">
                        <div class="activity-info">
                            <h4>${activity.title}</h4>
                            <p>${activity.activity_type} • ${new Date(activity.activity_date).toLocaleDateString()}</p>
                        </div>
                    </div>
                `).join('');
            } else {
                activitiesList.innerHTML = '<div class="empty-state"><p>No recent activities</p></div>';
            }
        }

        // Pipeline chart
        const pipelineChart = document.getElementById('pipelineChart');
        if (pipelineChart && dealsData.data?.by_stage) {
            const stages = ['prospect', 'qualified', 'proposal', 'negotiation'];
            const maxValue = Math.max(...stages.map(s => dealsData.data.by_stage[s] || 0), 1);
            
            pipelineChart.innerHTML = stages.map(stage => {
                const value = dealsData.data.by_stage[stage] || 0;
                const height = (value / maxValue) * 100;
                return `
                    <div class="pipeline-bar" style="height: ${height}%">
                        <div>${value}</div>
                        <div style="margin-top: auto; font-size: 0.8rem;">${stage}</div>
                    </div>
                `;
            }).join('');
        }
        
        // Load Data Quality metrics
        loadDataQualityMetrics();
        
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
};

// Load Data Quality Metrics
window.loadDataQualityMetrics = async function() {
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}/data/quality-report`, {
            headers: getHeaders()
        });
        
        if (!response.ok) {
            // If API not available, show placeholder data
            updateQualityUI({ overall_score: 85, completeness: 78, accuracy: 92, consistency: 88 });
            return;
        }
        
        const result = await response.json();
        const data = result.data || {};
        
        updateQualityUI({
            overall_score: data.overall_score || 0,
            completeness: data.completeness_score || data.completeness || 0,
            accuracy: data.accuracy_score || data.accuracy || 0,
            consistency: data.consistency_score || data.consistency || 0
        });
    } catch (error) {
        console.error('Error loading data quality:', error);
        // Show placeholder on error
        updateQualityUI({ overall_score: 85, completeness: 78, accuracy: 92, consistency: 88 });
    }
};

function updateQualityUI(metrics) {
    const overallEl = document.getElementById('qm-overall-score');
    const completenessEl = document.getElementById('qm-completeness');
    const accuracyEl = document.getElementById('qm-accuracy');
    const consistencyEl = document.getElementById('qm-consistency');
    
    if (overallEl) {
        overallEl.textContent = `${metrics.overall_score}%`;
        overallEl.className = `quality-score ${getScoreClass(metrics.overall_score)}`;
    }
    if (completenessEl) {
        completenessEl.textContent = `${metrics.completeness}%`;
        completenessEl.className = `quality-score ${getScoreClass(metrics.completeness)}`;
    }
    if (accuracyEl) {
        accuracyEl.textContent = `${metrics.accuracy}%`;
        accuracyEl.className = `quality-score ${getScoreClass(metrics.accuracy)}`;
    }
    if (consistencyEl) {
        consistencyEl.textContent = `${metrics.consistency}%`;
        consistencyEl.className = `quality-score ${getScoreClass(metrics.consistency)}`;
    }
    
    // Update bars
    const overallBar = document.getElementById('qm-overall-bar');
    const completenessBar = document.getElementById('qm-completeness-bar');
    const accuracyBar = document.getElementById('qm-accuracy-bar');
    const consistencyBar = document.getElementById('qm-consistency-bar');
    
    if (overallBar) overallBar.style.width = `${metrics.overall_score}%`;
    if (completenessBar) completenessBar.style.width = `${metrics.completeness}%`;
    if (accuracyBar) accuracyBar.style.width = `${metrics.accuracy}%`;
    if (consistencyBar) consistencyBar.style.width = `${metrics.consistency}%`;
    
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

function getScoreClass(score) {
    if (score >= 80) return 'score-high';
    if (score >= 60) return 'score-medium';
    return 'score-low';
}

// ============================================
// BI Dashboard Functions
// ============================================

function initDateFilters() {
    const filterBtns = document.querySelectorAll('.bi-filter-btn');
    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            filterBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            loadBIDashboard(this.dataset.range);
        });
    });
}

window.refreshDashboard = function() {
    const activeFilter = document.querySelector('.bi-filter-btn.active');
    const range = activeFilter ? activeFilter.dataset.range : 'month';
    loadBIDashboard(range);
};

window.loadBIDashboard = async function(range = 'month') {
    try {
        const storedCompanyId = localStorage.getItem('companyId');
        if (storedCompanyId) companyId = storedCompanyId;
        
        if (!companyId) {
            console.error('Company ID not set');
            return;
        }

        const companyIdNum = parseInt(companyId);
        
        // Set greeting
        const greeting = document.getElementById('dashboardGreeting');
        if (greeting) {
            const hour = new Date().getHours();
            const greetText = hour < 12 ? 'Good Morning' : hour < 17 ? 'Good Afternoon' : 'Good Evening';
            const userName = localStorage.getItem('userName') || 'User';
            greeting.textContent = `${greetText}, ${userName}! Here's your business overview`;
        }

        // Fetch all dashboard data in parallel
        const [statsRes, dealsRes, leadsRes, tasksRes, activitiesRes, forecastRes] = await Promise.all([
            fetch(`${API_BASE}/companies/${companyIdNum}/customers-stats`, { headers: getHeaders() }),
            fetch(`${API_BASE}/companies/${companyIdNum}/deals-stats`, { headers: getHeaders() }),
            fetch(`${API_BASE}/companies/${companyIdNum}/leads-stats`, { headers: getHeaders() }),
            fetch(`${API_BASE}/companies/${companyIdNum}/tasks/overdue`, { headers: getHeaders() }),
            fetch(`${API_BASE}/companies/${companyIdNum}/activities/timeline?limit=10`, { headers: getHeaders() }),
            fetch(`${API_BASE}/companies/${companyIdNum}/deals/forecast`, { headers: getHeaders() })
        ]);

        // Parse responses
        const statsData = statsRes.ok ? await statsRes.json() : { data: {} };
        const dealsData = dealsRes.ok ? await dealsRes.json() : { data: {} };
        const leadsData = leadsRes.ok ? await leadsRes.json() : { data: {} };
        const tasksData = tasksRes.ok ? await tasksRes.json() : { data: [] };
        const activitiesData = activitiesRes.ok ? await activitiesRes.json() : { data: [] };
        const forecastData = forecastRes.ok ? await forecastRes.json() : { data: {} };

        // Update KPI Cards
        updateKPICards(statsData.data, dealsData.data, leadsData.data, forecastData.data);
        
        // Update Pipeline Funnel
        updatePipelineFunnel(dealsData.data);
        
        // Update Charts
        updateRevenueTrendChart(forecastData.data);
        updateLeadSourcesChart(leadsData.data);
        
        // Update Activity Heatmap
        updateActivityHeatmap();
        
        // Update Quick Stats
        updateQuickStats(activitiesData.data);
        
        // Update Top Deals Table
        updateTopDealsTable(dealsData.data);
        
        // Update Team Leaderboard
        updateTeamLeaderboard();
        
        // Update Timeline
        updateActivitiesTimeline(activitiesData.data);
        
        // Update Overdue Tasks
        updateOverdueTasks(tasksData.data);
        
        // Update Forecast Gauge
        updateForecastGauge(forecastData.data);
        
        // Update Data Quality
        loadDataQualityMetricsBI();
        
        // Reinitialize Lucide icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }

    } catch (error) {
        console.error('Error loading BI dashboard:', error);
    }
};

function updateKPICards(stats, deals, leads, forecast) {
    // Total Revenue
    const revenue = forecast?.total_pipeline || deals?.total_value || 0;
    const kpiRevenue = document.getElementById('kpiRevenue');
    if (kpiRevenue) kpiRevenue.textContent = formatCurrency(revenue);
    
    // Pipeline Value
    const pipeline = forecast?.weighted_pipeline || revenue * 0.6;
    const kpiPipeline = document.getElementById('kpiPipeline');
    if (kpiPipeline) kpiPipeline.textContent = formatCurrency(pipeline);
    
    // Win Rate - Calculate from actual deals data
    const totalDeals = deals?.total_deals || 0;
    const wonDeals = deals?.by_stage?.closed_won || 0;
    const lostDeals = deals?.by_stage?.closed_lost || 0;
    const closedDeals = wonDeals + lostDeals;
    const winRate = closedDeals > 0 ? Math.round((wonDeals / closedDeals) * 100) : (forecast?.historical_win_rate || 0);
    const kpiWinRate = document.getElementById('kpiWinRate');
    if (kpiWinRate) kpiWinRate.textContent = `${winRate}%`;
    
    // Active Deals
    const activeDeals = deals?.total_deals || 0;
    const kpiActiveDeals = document.getElementById('kpiActiveDeals');
    if (kpiActiveDeals) kpiActiveDeals.textContent = activeDeals;
    
    // Deal breakdown
    const dealsProspect = document.getElementById('dealsProspect');
    const dealsNegotiation = document.getElementById('dealsNegotiation');
    if (dealsProspect) dealsProspect.textContent = deals?.by_stage?.prospect || 0;
    if (dealsNegotiation) dealsNegotiation.textContent = deals?.by_stage?.negotiation || 0;
    
    // Conversion Rate
    const totalLeads = leads?.total_leads || 1;
    const totalCustomers = stats?.total_customers || 0;
    const conversionRate = Math.round((totalCustomers / Math.max(totalLeads, 1)) * 100);
    const kpiConversion = document.getElementById('kpiConversion');
    if (kpiConversion) kpiConversion.textContent = `${conversionRate}%`;
    
    // Funnel counts
    const funnelLeads = document.getElementById('funnelLeads');
    const funnelCustomers = document.getElementById('funnelCustomers');
    if (funnelLeads) funnelLeads.textContent = totalLeads;
    if (funnelCustomers) funnelCustomers.textContent = totalCustomers;
}

function updatePipelineFunnel(deals) {
    const stageData = deals?.by_stage || { prospect: 5, qualified: 3, proposal: 2, negotiation: 1, closed_won: 1 };
    const stageValues = deals?.value_by_stage || { prospect: 250000, qualified: 180000, proposal: 120000, negotiation: 80000, closed_won: 50000 };
    
    // Update counts
    const prospectCount = document.getElementById('funnelProspectCount');
    const qualifiedCount = document.getElementById('funnelQualifiedCount');
    const proposalCount = document.getElementById('funnelProposalCount');
    const negotiationCount = document.getElementById('funnelNegotiationCount');
    const wonCount = document.getElementById('funnelWonCount');
    
    if (prospectCount) prospectCount.textContent = stageData.prospect || 0;
    if (qualifiedCount) qualifiedCount.textContent = stageData.qualified || 0;
    if (proposalCount) proposalCount.textContent = stageData.proposal || 0;
    if (negotiationCount) negotiationCount.textContent = stageData.negotiation || 0;
    if (wonCount) wonCount.textContent = stageData.closed_won || 0;
    
    // Update values
    const prospectValue = document.getElementById('funnelProspectValue');
    const qualifiedValue = document.getElementById('funnelQualifiedValue');
    const proposalValue = document.getElementById('funnelProposalValue');
    const negotiationValue = document.getElementById('funnelNegotiationValue');
    const wonValue = document.getElementById('funnelWonValue');
    
    if (prospectValue) prospectValue.textContent = formatCurrency(stageValues.prospect || 0);
    if (qualifiedValue) qualifiedValue.textContent = formatCurrency(stageValues.qualified || 0);
    if (proposalValue) proposalValue.textContent = formatCurrency(stageValues.proposal || 0);
    if (negotiationValue) negotiationValue.textContent = formatCurrency(stageValues.negotiation || 0);
    if (wonValue) wonValue.textContent = formatCurrency(stageValues.closed_won || 0);
}

function updateRevenueTrendChart(forecast) {
    const ctx = document.getElementById('revenueTrendChart');
    if (!ctx) return;
    
    // Check if Chart.js is loaded
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js not loaded');
        return;
    }
    
    // Generate sample data if not available
    const months = ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const projections = forecast?.monthly_projections || [];
    const revenueData = projections.length > 0 
        ? projections.map(p => p.projected_revenue || 0)
        : [120000, 150000, 180000, 220000, 280000, 350000];
    
    if (revenueTrendChart) {
        revenueTrendChart.destroy();
    }
    
    revenueTrendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: months,
            datasets: [{
                label: 'Revenue',
                data: revenueData,
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#3b82f6',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: value => '₹' + (value / 1000) + 'K'
                    },
                    grid: { color: '#f1f5f9' }
                },
                x: {
                    grid: { display: false }
                }
            }
        }
    });
}

function updateLeadSourcesChart(leads) {
    const ctx = document.getElementById('leadSourcesChart');
    if (!ctx) return;
    
    // Check if Chart.js is loaded
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js not loaded');
        return;
    }
    
    const sources = leads?.by_source || {
        'Website': 35,
        'Referral': 25,
        'Social': 20,
        'Direct': 15,
        'Other': 5
    };
    
    const labels = Object.keys(sources);
    const data = Object.values(sources);
    const colors = ['#3b82f6', '#22c55e', '#f59e0b', '#8b5cf6', '#ec4899'];
    
    if (leadSourcesChart) {
        leadSourcesChart.destroy();
    }
    
    leadSourcesChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { boxWidth: 12, padding: 15 }
                }
            }
        }
    });
}

function updateActivityHeatmap() {
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'];
    const hours = 8; // 8 hours per day
    
    days.forEach(day => {
        const container = document.getElementById(`heatmap${day}`);
        if (!container) return;
        
        let html = '';
        for (let i = 0; i < hours; i++) {
            const level = Math.floor(Math.random() * 5);
            html += `<div class="heatmap-cell ${level > 0 ? 'level-' + level : ''}"></div>`;
        }
        container.innerHTML = html;
    });
}

function updateQuickStats(activities) {
    const activityList = Array.isArray(activities) ? activities : [];
    
    // Count actual activities by type
    const calls = activityList.filter(a => a.activity_type === 'call' || a.activity_type === 'Call').length;
    const emails = activityList.filter(a => a.activity_type === 'email' || a.activity_type === 'Email').length;
    const meetings = activityList.filter(a => a.activity_type === 'meeting' || a.activity_type === 'Meeting').length;
    const notes = activityList.filter(a => a.activity_type === 'note' || a.activity_type === 'Note').length;
    
    const statCalls = document.getElementById('statCalls');
    const statEmails = document.getElementById('statEmails');
    const statMeetings = document.getElementById('statMeetings');
    const statTasksCompleted = document.getElementById('statTasksCompleted');
    
    if (statCalls) statCalls.textContent = calls;
    if (statEmails) statEmails.textContent = emails;
    if (statMeetings) statMeetings.textContent = meetings;
    if (statTasksCompleted) statTasksCompleted.textContent = notes || activityList.length;
}

function updateTopDealsTable(deals) {
    const tbody = document.getElementById('topDealsTable');
    if (!tbody) return;
    
    // Use actual deals from API if available
    const topDeals = deals?.top_deals || deals?.recent_deals || [];
    
    if (topDeals.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:#94a3b8;padding:24px;">No deals found</td></tr>';
        return;
    }
    
    tbody.innerHTML = topDeals.slice(0, 5).map(deal => `
        <tr>
            <td><strong>${deal.name || deal.title || 'Untitled'}</strong></td>
            <td>${deal.account || deal.customer_name || deal.customer?.name || '-'}</td>
            <td>${formatCurrency(deal.value || deal.amount || 0)}</td>
            <td><span class="status-badge status-${(deal.stage || 'prospect').toLowerCase().replace(' ', '-')}">${deal.stage || 'Prospect'}</span></td>
            <td>
                <div style="display:flex;align-items:center;gap:8px;">
                    <div style="flex:1;height:6px;background:#e2e8f0;border-radius:3px;">
                        <div style="width:${deal.probability || 0}%;height:100%;background:#22c55e;border-radius:3px;"></div>
                    </div>
                    <span>${deal.probability || 0}%</span>
                </div>
            </td>
        </tr>
    `).join('');
}

async function updateTeamLeaderboard() {
    const container = document.getElementById('teamLeaderboard');
    if (!container) return;
    
    try {
        // Fetch actual users data
        const response = await fetch(`${API_BASE}/companies/${companyId}/users`, { headers: getHeaders() });
        
        if (response.ok) {
            const result = await response.json();
            const users = result.data || [];
            
            if (users.length === 0) {
                container.innerHTML = '<div class="leaderboard-item" style="justify-content:center;color:#94a3b8;">No team members</div>';
                return;
            }
            
            const rankClasses = ['gold', 'silver', 'bronze', 'normal'];
            
            container.innerHTML = users.slice(0, 5).map((user, index) => `
                <div class="leaderboard-item">
                    <div class="leaderboard-rank ${rankClasses[index] || 'normal'}">${index + 1}</div>
                    <div class="leaderboard-avatar">${(user.name || user.email || 'U').split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase()}</div>
                    <div class="leaderboard-info">
                        <div class="leaderboard-name">${user.name || user.email}</div>
                        <div class="leaderboard-deals">${user.role || 'Team Member'}</div>
                    </div>
                    <div class="leaderboard-value" style="color:#64748b;font-size:12px;">${user.is_active ? 'Active' : 'Inactive'}</div>
                </div>
            `).join('');
        } else {
            container.innerHTML = '<div class="leaderboard-item" style="justify-content:center;color:#94a3b8;">Unable to load team</div>';
        }
    } catch (error) {
        console.error('Error loading team:', error);
        container.innerHTML = '<div class="leaderboard-item" style="justify-content:center;color:#94a3b8;">Unable to load team</div>';
    }
}

function updateActivitiesTimeline(activities) {
    const container = document.getElementById('recentActivitiesTimeline');
    if (!container) return;
    
    if (!activities || activities.length === 0) {
        container.innerHTML = '<div class="timeline-item"><div class="timeline-content">No recent activities</div></div>';
        return;
    }
    
    const iconMap = {
        'call': 'phone',
        'email': 'mail',
        'meeting': 'calendar',
        'note': 'file-text'
    };
    
    container.innerHTML = activities.slice(0, 6).map(activity => `
        <div class="timeline-item">
            <div class="timeline-icon ${activity.activity_type || 'note'}">
                <i data-lucide="${iconMap[activity.activity_type] || 'circle'}"></i>
            </div>
            <div class="timeline-content">
                <div class="timeline-title">${activity.title || 'Activity'}</div>
                <div class="timeline-desc">${activity.description || activity.activity_type || ''}</div>
            </div>
            <div class="timeline-time">${formatTimeAgo(activity.activity_date || activity.created_at)}</div>
        </div>
    `).join('');
}

function updateOverdueTasks(tasks) {
    const container = document.getElementById('overdueTasksList');
    const countBadge = document.getElementById('overdueCount');
    
    if (!container) return;
    
    const overdueTasks = Array.isArray(tasks) ? tasks : (tasks?.overdue_tasks || []);
    
    if (countBadge) countBadge.textContent = overdueTasks.length;
    
    if (overdueTasks.length === 0) {
        container.innerHTML = '<div class="task-item" style="background:#f0fdf4;border-left-color:#22c55e;justify-content:center;color:#22c55e;">No overdue tasks!</div>';
        return;
    }
    
    container.innerHTML = overdueTasks.slice(0, 5).map(task => `
        <div class="task-item">
            <div class="task-priority ${task.priority || 'medium'}"></div>
            <div class="task-info">
                <div class="task-title">${task.title || 'Untitled Task'}</div>
                <div class="task-due">Due: ${formatDate(task.due_date)}</div>
            </div>
            <button class="task-action" onclick="completeTask(${task.id})">Complete</button>
        </div>
    `).join('');
}

function updateForecastGauge(forecast) {
    const target = 1000000; // ₹10 Lakh target
    const achieved = forecast?.total_pipeline || 650000;
    const percent = Math.min(Math.round((achieved / target) * 100), 100);
    
    const forecastPercent = document.getElementById('forecastPercent');
    const forecastAchieved = document.getElementById('forecastAchieved');
    const forecastTarget = document.getElementById('forecastTarget');
    const forecastRemaining = document.getElementById('forecastRemaining');
    
    if (forecastPercent) forecastPercent.textContent = `${percent}%`;
    if (forecastAchieved) forecastAchieved.textContent = formatCurrency(achieved);
    if (forecastTarget) forecastTarget.textContent = formatCurrency(target);
    if (forecastRemaining) forecastRemaining.textContent = formatCurrency(Math.max(target - achieved, 0));
    
    // Update gauge progress
    const gaugeProgress = document.getElementById('forecastGaugeProgress');
    if (gaugeProgress) {
        const dashOffset = 251 - (251 * percent / 100);
        gaugeProgress.style.strokeDashoffset = dashOffset;
    }
}

async function loadDataQualityMetricsBI() {
    // Default metrics
    let metrics = { overall: 0, completeness: 0, accuracy: 0, consistency: 0, validity: 0 };
    
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}/data/quality-report`, { headers: getHeaders() });
        if (response.ok) {
            const result = await response.json();
            const data = result.data || {};
            metrics = {
                overall: data.overall_score || 0,
                completeness: data.completeness_score || data.completeness || 0,
                accuracy: data.accuracy_score || data.accuracy || 0,
                consistency: data.consistency_score || data.consistency || 0,
                validity: data.validity_score || data.validity || 0
            };
        }
    } catch (error) {
        console.error('Error loading data quality:', error);
    }
    
    // Update ring
    const ringFill = document.getElementById('qualityRingOverall');
    if (ringFill) {
        const dashOffset = 251 - (251 * metrics.overall / 100);
        ringFill.style.strokeDashoffset = dashOffset;
    }
    
    const qualityOverall = document.getElementById('qualityOverall');
    if (qualityOverall) qualityOverall.textContent = `${metrics.overall}%`;
    
    // Update bars
    const bars = ['Completeness', 'Accuracy', 'Consistency', 'Validity'];
    bars.forEach(bar => {
        const barEl = document.getElementById(`qualityBar${bar}`);
        const valueEl = document.getElementById(`quality${bar}`);
        const value = metrics[bar.toLowerCase()] || 0;
        
        if (barEl) barEl.style.height = `${value}%`;
        if (valueEl) valueEl.textContent = `${value}%`;
    });
}

// Helper Functions
function formatCurrency(value) {
    if (value >= 10000000) return '₹' + (value / 10000000).toFixed(1) + 'Cr';
    if (value >= 100000) return '₹' + (value / 100000).toFixed(1) + 'L';
    if (value >= 1000) return '₹' + (value / 1000).toFixed(0) + 'K';
    return '₹' + value;
}

function formatDate(dateStr) {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
}

function formatTimeAgo(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    const now = new Date();
    const diff = Math.floor((now - date) / 1000);
    
    if (diff < 60) return 'Just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
}

function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}


// Dashboard Page JavaScript

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
    
    loadDashboard();
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
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
};


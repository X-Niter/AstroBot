// AstroBot Analytics Dashboard - React Components
// This file contains the React components for the analytics dashboard

// Register required Chart.js components
Chart.register(
  ChartDataLabels,
  Chart.controllers.line,
  Chart.controllers.bar,
  Chart.controllers.doughnut,
  Chart.controllers.pie,
  Chart.controllers.bubble
);

// Set default Chart.js options for all charts
Chart.defaults.responsive = true;
Chart.defaults.maintainAspectRatio = false;
Chart.defaults.font.family = "'Inter', 'Helvetica', 'Arial', sans-serif";
Chart.defaults.plugins.legend.position = 'top';
Chart.defaults.plugins.tooltip.enabled = true;
Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(0, 0, 0, 0.7)';
Chart.defaults.plugins.tooltip.padding = 10;
Chart.defaults.plugins.tooltip.cornerRadius = 6;
Chart.defaults.plugins.datalabels.display = false; // Only enable for specific charts

// Color schemes for charts based on current theme
const getChartColors = (theme) => {
  const themeColors = {
    light: {
      primary: '#007bff',
      secondary: '#6c757d',
      success: '#28a745',
      info: '#17a2b8',
      warning: '#ffc107',
      danger: '#dc3545',
      purple: '#6f42c1',
      pink: '#e83e8c',
      orange: '#fd7e14'
    },
    dark: {
      primary: '#375a7f',
      secondary: '#6c757d',
      success: '#00bc8c',
      info: '#3498db',
      warning: '#f39c12',
      danger: '#e74c3c',
      purple: '#8c44ad',
      pink: '#e83e8c',
      orange: '#fd7e14'
    },
    space: {
      primary: '#7269ef',
      secondary: '#6c757d',
      success: '#06d6a0',
      info: '#3fc5f0',
      warning: '#ffd166',
      danger: '#ef476f',
      purple: '#9681eb',
      pink: '#e83e8c',
      orange: '#fd7e14'
    },
    neon: {
      primary: '#00eeff',
      secondary: '#6c757d',
      success: '#39ff14',
      info: '#00ffff',
      warning: '#ffff00',
      danger: '#ff0080',
      purple: '#bf00ff',
      pink: '#ff00ff',
      orange: '#ff8000'
    }
  };

  return themeColors[theme] || themeColors.light;
};

// Sample data for the dashboard
// In a real application, this would be fetched from an API
const getSampleData = () => {
  return {
    stats: {
      users: 5428,
      commands: 15342,
      aiPrompts: 3247,
      modActions: 267
    },
    activityOverTime: {
      labels: ['May 3', 'May 4', 'May 5', 'May 6', 'May 7', 'May 8', 'May 9'],
      datasets: [
        {
          label: 'Commands',
          data: [4251, 4812, 5132, 4987, 5643, 6218, 5987]
        },
        {
          label: 'AI Interactions',
          data: [1532, 1876, 2132, 2432, 2876, 3012, 2987]
        },
        {
          label: 'User Activity',
          data: [8765, 9432, 10234, 9876, 11234, 12543, 11987]
        }
      ]
    },
    topCommands: {
      labels: ['!help', '!ai', '!mod', '!config', '!minecraft', '!twitch'],
      data: [32, 24, 15, 13, 9, 7]
    },
    aiUsage: {
      labels: ['Claude 3.5', 'GPT-4o', 'Stable Diffusion', 'Others'],
      data: [42, 35, 15, 8]
    },
    activeServers: [
      {
        name: 'AstroFrame Community',
        id: '123456789012345678',
        iconColor: '#7289DA',
        members: 4285,
        commandsToday: 587,
        aiUsage: 75,
        status: 'online'
      },
      {
        name: 'Minecraft Modders',
        id: '234567890123456789',
        iconColor: '#43B581',
        members: 2147,
        commandsToday: 342,
        aiUsage: 52,
        status: 'online'
      },
      {
        name: 'Twitch Streamers',
        id: '345678901234567890',
        iconColor: '#FAA61A',
        members: 1893,
        commandsToday: 271,
        aiUsage: 38,
        status: 'online'
      }
    ]
  };
};

// Main Dashboard Component
const Dashboard = () => {
  const [timeRange, setTimeRange] = React.useState(7);
  const [data, setData] = React.useState(getSampleData());
  const [loading, setLoading] = React.useState(true);
  const [theme, setTheme] = React.useState('light');
  const [initialLoad, setInitialLoad] = React.useState(true);
  
  // Get current theme from body class
  React.useEffect(() => {
    const bodyClasses = document.body.className;
    if (bodyClasses.includes('theme-dark')) setTheme('dark');
    else if (bodyClasses.includes('theme-space')) setTheme('space');
    else if (bodyClasses.includes('theme-neon')) setTheme('neon');
    else setTheme('light');
    
    // Listen for theme changes
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.attributeName === 'class') {
          const newBodyClasses = document.body.className;
          if (newBodyClasses.includes('theme-dark')) setTheme('dark');
          else if (newBodyClasses.includes('theme-space')) setTheme('space');
          else if (newBodyClasses.includes('theme-neon')) setTheme('neon');
          else setTheme('light');
        }
      });
    });
    
    observer.observe(document.body, { attributes: true });
    
    // Simulate loading data
    setTimeout(() => {
      setLoading(false);
      setInitialLoad(false);
    }, 1500);
    
    return () => observer.disconnect();
  }, []);
  
  // Connect to socket.io for real-time updates
  React.useEffect(() => {
    // Don't try to connect during initial load
    if (initialLoad) return;
    
    // Check if socket is available
    if (typeof window !== 'undefined' && window.astrobotSocket) {
      try {
        // Listen for updates
        window.astrobotSocket.on('stats_update', (newData) => {
          setData(prevData => ({
            ...prevData,
            stats: {
              users: newData.users,
              commands: newData.commands,
              aiPrompts: newData.ai_prompts,
              modActions: newData.mod_actions
            }
          }));
        });
        
        // Join analytics channel
        window.astrobotSocket.emit('join_channel', 'analytics');
      } catch (err) {
        console.log('Socket initialization error:', err);
      }
    }
    
    // Cleanup on unmount
    return () => {
      if (typeof window !== 'undefined' && window.astrobotSocket) {
        try {
          window.astrobotSocket.off('stats_update');
        } catch (err) {
          console.log('Socket cleanup error:', err);
        }
      }
    };
  }, [initialLoad]);
  
  // Function to update time range
  const handleTimeRangeChange = (days) => {
    setTimeRange(days);
    setLoading(true);
    
    // In a real app, we would fetch new data based on the time range
    // For demo, we'll just simulate a delay
    setTimeout(() => {
      setLoading(false);
    }, 800);
  };
  
  // Get chart colors based on current theme
  const colors = getChartColors(theme);
  
  return (
    <div className="dashboard-container">
      <div className="dashboard-content">
        {/* Header */}
        <DashboardHeader 
          timeRange={timeRange} 
          onTimeRangeChange={handleTimeRangeChange} 
        />
        
        {/* Stats Cards */}
        <div className="row g-3 mb-3">
          <StatsCard 
            icon="people-fill" 
            title="Total Users" 
            value={data.stats.users} 
            color={colors.primary}
            loading={loading}
          />
          <StatsCard 
            icon="terminal-fill" 
            title="Commands Used" 
            value={data.stats.commands} 
            color={colors.success}
            loading={loading}
          />
          <StatsCard 
            icon="robot" 
            title="AI Prompts" 
            value={data.stats.aiPrompts} 
            color={colors.purple}
            loading={loading}
          />
          <StatsCard 
            icon="shield-check" 
            title="Mod Actions" 
            value={data.stats.modActions} 
            color={colors.danger}
            loading={loading}
          />
        </div>
        
        {/* Charts - Row 1 */}
        <div className="row g-3 mb-3">
          <div className="col-12 col-lg-8">
            <ActivityChart 
              data={data.activityOverTime} 
              loading={loading} 
              colors={colors}
            />
          </div>
          <div className="col-12 col-lg-4">
            <CommandsChart 
              data={data.topCommands} 
              loading={loading} 
              colors={colors}
            />
          </div>
        </div>
        
        {/* Charts - Row 2 */}
        <div className="row g-3 mb-3">
          <div className="col-12 col-lg-6">
            <AIUsageChart 
              data={data.aiUsage} 
              loading={loading} 
              colors={colors}
            />
          </div>
          <div className="col-12 col-lg-6">
            <ActivityHeatmap 
              loading={loading} 
              colors={colors}
            />
          </div>
        </div>
        
        {/* Servers Table */}
        <div className="row g-3">
          <div className="col-12">
            <ServersTable 
              servers={data.activeServers} 
              loading={loading}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

// Dashboard Header Component
const DashboardHeader = ({ timeRange, onTimeRangeChange }) => {
  return (
    <div className="dashboard-header d-flex justify-content-between align-items-center mb-3">
      <h5 className="mb-0">Analytics Dashboard</h5>
      <div className="d-flex">
        <div className="dropdown me-2">
          <button className="btn btn-outline-secondary btn-sm dropdown-toggle" type="button" id="timeRangeDropdown" data-bs-toggle="dropdown" aria-expanded="false">
            Last {timeRange} Days
          </button>
          <ul className="dropdown-menu dropdown-menu-end" aria-labelledby="timeRangeDropdown">
            <li><button className={`dropdown-item ${timeRange === 7 ? 'active' : ''}`} onClick={() => onTimeRangeChange(7)}>Last 7 Days</button></li>
            <li><button className={`dropdown-item ${timeRange === 14 ? 'active' : ''}`} onClick={() => onTimeRangeChange(14)}>Last 14 Days</button></li>
            <li><button className={`dropdown-item ${timeRange === 30 ? 'active' : ''}`} onClick={() => onTimeRangeChange(30)}>Last 30 Days</button></li>
            <li><button className={`dropdown-item ${timeRange === 90 ? 'active' : ''}`} onClick={() => onTimeRangeChange(90)}>Last 90 Days</button></li>
          </ul>
        </div>
        <button className="btn btn-outline-primary btn-sm" data-bs-toggle="modal" data-bs-target="#liveActivityModal">
          <i className="bi bi-activity"></i> Live Feed
        </button>
      </div>
    </div>
  );
};

// Stats Card Component
const StatsCard = ({ icon, title, value, color, loading }) => {
  return (
    <div className="col-sm-6 col-lg-3">
      <div className="stats-card d-flex align-items-center">
        <div className="rounded-circle d-flex align-items-center justify-content-center me-3" 
             style={{ width: '48px', height: '48px', backgroundColor: `${color}20` }}>
          <i className={`bi bi-${icon}`} style={{ color: color, fontSize: '1.5rem' }}></i>
        </div>
        <div>
          <div className="text-secondary small">{title}</div>
          {loading ? (
            <div className="placeholder-glow">
              <span className="placeholder col-6"></span>
            </div>
          ) : (
            <div className="fs-4 fw-bold">{value.toLocaleString()}</div>
          )}
        </div>
      </div>
    </div>
  );
};

// Activity Chart Component
const ActivityChart = ({ data, loading, colors }) => {
  // Instead of creating our own canvas, we'll use the pre-existing one
  const [chart, setChart] = React.useState(null);
  
  React.useEffect(() => {
    // Find the existing canvas element instead of creating a new one
    const canvas = document.getElementById('activity-chart');
    
    if (canvas && !loading) {
      // Safely access the canvas context
      let ctx;
      try {
        ctx = canvas.getContext('2d');
      } catch (err) {
        console.error('Error getting canvas context:', err);
        return;
      }
      
      // Destroy previous chart if it exists
      if (chart) {
        try {
          chart.destroy();
        } catch (err) {
          console.error('Error destroying previous chart:', err);
        }
      }
      
      try {
        // Create new chart
        const newChart = new Chart(ctx, {
          type: 'line',
          data: {
            labels: data.labels,
            datasets: [
              {
                label: 'Commands',
                data: data.datasets[0].data,
                borderColor: colors.primary,
                backgroundColor: `${colors.primary}20`,
                borderWidth: 2,
                tension: 0.4,
                fill: true
              },
              {
                label: 'AI Interactions',
                data: data.datasets[1].data,
                borderColor: colors.purple,
                backgroundColor: `${colors.purple}20`,
                borderWidth: 2,
                tension: 0.4,
                fill: true
              },
              {
                label: 'User Activity',
                data: data.datasets[2].data,
                borderColor: colors.success,
                backgroundColor: `${colors.success}20`,
                borderWidth: 2,
                tension: 0.4,
                fill: true
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
              mode: 'index',
              intersect: false
            },
            plugins: {
              title: {
                display: true,
                text: 'Activity Over Time',
                font: {
                  size: 16,
                  weight: 'normal'
                }
              },
              legend: {
                position: 'top'
              },
              tooltip: {
                boxPadding: 8
              }
            },
            scales: {
              x: {
                grid: {
                  display: false
                }
              },
              y: {
                beginAtZero: true,
                ticks: {
                  callback: (value) => value.toLocaleString()
                }
              }
            }
          }
        });
        
        setChart(newChart);
      } catch (err) {
        console.error('Error creating chart:', err);
      }
    }
    
    // Cleanup on unmount
    return () => {
      if (chart) {
        try {
          chart.destroy();
        } catch (err) {
          console.error('Error destroying chart on unmount:', err);
        }
      }
    };
  }, [data, loading, colors]);
  
  return (
    <div className="chart-wrapper">
      {loading ? (
        <div className="d-flex justify-content-center align-items-center h-100">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      ) : (
        <div className="chart-container">
          <h5 className="card-title mb-3">Activity Over Time</h5>
          {/* We don't render a canvas here since we're using the hidden one */}
        </div>
      )}
    </div>
  );
};

// Commands Chart Component
const CommandsChart = ({ data, loading, colors }) => {
  // Instead of creating our own canvas, we'll use the pre-existing one
  const [chart, setChart] = React.useState(null);
  
  React.useEffect(() => {
    // Find the existing canvas element instead of creating a new one
    const canvas = document.getElementById('commands-chart');
    
    if (canvas && !loading) {
      // Safely access the canvas context
      let ctx;
      try {
        ctx = canvas.getContext('2d');
      } catch (err) {
        console.error('Error getting canvas context:', err);
        return;
      }
      
      // Destroy previous chart if it exists
      if (chart) {
        try {
          chart.destroy();
        } catch (err) {
          console.error('Error destroying previous chart:', err);
        }
      }
      
      try {
        // Create chart colors array
        const chartColors = [
          colors.primary,
          colors.purple,
          colors.orange,
          colors.success,
          colors.info,
          colors.danger
        ];
        
        // Create new chart
        const newChart = new Chart(ctx, {
          type: 'doughnut',
          data: {
            labels: data.labels,
            datasets: [{
              data: data.data,
              backgroundColor: chartColors,
              borderWidth: 1,
              borderColor: chartColors.map(color => `${color}50`)
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              title: {
                display: true,
                text: 'Top Commands',
                font: {
                  size: 16,
                  weight: 'normal'
                }
              },
              legend: {
                position: 'bottom',
                labels: {
                  boxWidth: 12,
                  padding: 15
                }
              },
              datalabels: {
                display: true,
                color: 'white',
                font: {
                  weight: 'bold'
                },
                formatter: (value, ctx) => {
                  const sum = ctx.dataset.data.reduce((a, b) => a + b, 0);
                  const percentage = Math.round((value / sum) * 100) + '%';
                  return percentage;
                }
              }
            },
            cutout: '65%'
          }
        });
        
        setChart(newChart);
      } catch (err) {
        console.error('Error creating chart:', err);
      }
    }
    
    // Cleanup on unmount
    return () => {
      if (chart) {
        try {
          chart.destroy();
        } catch (err) {
          console.error('Error destroying chart on unmount:', err);
        }
      }
    };
  }, [data, loading, colors]);
  
  return (
    <div className="chart-wrapper">
      {loading ? (
        <div className="d-flex justify-content-center align-items-center h-100">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      ) : (
        <div className="chart-container">
          <h5 className="card-title mb-3">Top Commands</h5>
          {/* We don't render a canvas here since we're using the hidden one */}
        </div>
      )}
    </div>
  );
};

// AI Usage Chart Component
const AIUsageChart = ({ data, loading, colors }) => {
  // Instead of creating our own canvas, we'll use the pre-existing one
  const [chart, setChart] = React.useState(null);
  
  React.useEffect(() => {
    // Find the existing canvas element instead of creating a new one
    const canvas = document.getElementById('ai-usage-chart');
    
    if (canvas && !loading) {
      // Safely access the canvas context
      let ctx;
      try {
        ctx = canvas.getContext('2d');
      } catch (err) {
        console.error('Error getting canvas context:', err);
        return;
      }
      
      // Destroy previous chart if it exists
      if (chart) {
        try {
          chart.destroy();
        } catch (err) {
          console.error('Error destroying previous chart:', err);
        }
      }
      
      try {
        // Create chart colors array
        const chartColors = [
          colors.purple,
          colors.primary,
          colors.success,
          colors.secondary
        ];
        
        // Create new chart
        const newChart = new Chart(ctx, {
          type: 'pie',
          data: {
            labels: data.labels,
            datasets: [{
              data: data.data,
              backgroundColor: chartColors,
              borderWidth: 1,
              borderColor: chartColors.map(color => `${color}50`)
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              title: {
                display: true,
                text: 'AI Model Usage',
                font: {
                  size: 16,
                  weight: 'normal'
                }
              },
              legend: {
                position: 'bottom',
                labels: {
                  boxWidth: 12,
                  padding: 15
                }
              },
              datalabels: {
                display: true,
                color: 'white',
                font: {
                  weight: 'bold'
                },
                formatter: (value, ctx) => {
                  const sum = ctx.dataset.data.reduce((a, b) => a + b, 0);
                  const percentage = Math.round((value / sum) * 100) + '%';
                  return percentage;
                }
              }
            }
          }
        });
        
        setChart(newChart);
      } catch (err) {
        console.error('Error creating chart:', err);
      }
    }
    
    // Cleanup on unmount
    return () => {
      if (chart) {
        try {
          chart.destroy();
        } catch (err) {
          console.error('Error destroying chart on unmount:', err);
        }
      }
    };
  }, [data, loading, colors]);
  
  return (
    <div className="chart-wrapper">
      {loading ? (
        <div className="d-flex justify-content-center align-items-center h-100">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      ) : (
        <div className="chart-container">
          <h5 className="card-title mb-3">AI Model Usage</h5>
          {/* We don't render a canvas here since we're using the hidden one */}
        </div>
      )}
    </div>
  );
};

// Activity Heatmap Component
const ActivityHeatmap = ({ loading, colors }) => {
  // Instead of creating our own canvas, we'll use the pre-existing one
  const [chart, setChart] = React.useState(null);
  
  React.useEffect(() => {
    // Find the existing canvas element instead of creating a new one
    const canvas = document.getElementById('heatmap-chart');
    
    if (canvas && !loading) {
      // Safely access the canvas context
      let ctx;
      try {
        ctx = canvas.getContext('2d');
      } catch (err) {
        console.error('Error getting canvas context:', err);
        return;
      }
      
      // Destroy previous chart if it exists
      if (chart) {
        try {
          chart.destroy();
        } catch (err) {
          console.error('Error destroying previous chart:', err);
        }
      }
      
      try {
        // Generate heatmap data
        const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
        const hours = ['12am', '4am', '8am', '12pm', '4pm', '8pm'];
        
        const heatmapData = [];
        for (let i = 0; i < hours.length; i++) {
          for (let j = 0; j < days.length; j++) {
            const value = Math.floor(Math.random() * 100);
            const opacity = value < 20 ? 0.2 : value < 50 ? 0.5 : value < 80 ? 0.8 : 1;
            
            heatmapData.push({
              x: j,
              y: i,
              v: value,
              r: 10 + (value / 10),
              color: `rgba(${parseInt(colors.success.substring(1, 3), 16)}, ${parseInt(colors.success.substring(3, 5), 16)}, ${parseInt(colors.success.substring(5, 7), 16)}, ${opacity})`
            });
          }
        }
        
        // Create new chart
        const newChart = new Chart(ctx, {
          type: 'bubble',
          data: {
            datasets: [{
              data: heatmapData.map(d => ({
                x: d.x,
                y: d.y,
                r: d.r
              })),
              backgroundColor: heatmapData.map(d => d.color)
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              title: {
                display: true,
                text: 'Hourly Activity Heatmap',
                font: {
                  size: 16,
                  weight: 'normal'
                }
              },
              legend: {
                display: false
              },
              tooltip: {
                callbacks: {
                  label: function(context) {
                    const d = heatmapData[context.dataIndex];
                    return `${days[d.x]} ${hours[d.y]}: ${d.v} activities`;
                  }
                }
              }
            },
            scales: {
              x: {
                min: -0.5,
                max: 6.5,
                ticks: {
                  callback: function(value) {
                    return days[value];
                  }
                },
                grid: {
                  display: false
                }
              },
              y: {
                min: -0.5,
                max: 5.5,
                ticks: {
                  callback: function(value) {
                    return hours[value];
                  }
                },
                grid: {
                  display: false
                }
              }
            }
          }
        });
        
        setChart(newChart);
      } catch (err) {
        console.error('Error creating chart:', err);
      }
    }
    
    // Cleanup on unmount
    return () => {
      if (chart) {
        try {
          chart.destroy();
        } catch (err) {
          console.error('Error destroying chart on unmount:', err);
        }
      }
    };
  }, [loading, colors]);
  
  return (
    <div className="chart-wrapper">
      {loading ? (
        <div className="d-flex justify-content-center align-items-center h-100">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      ) : (
        <div className="chart-container">
          <h5 className="card-title mb-3">Hourly Activity Heatmap</h5>
          {/* We don't render a canvas here since we're using the hidden one */}
        </div>
      )}
    </div>
  );
};

// Servers Table Component
const ServersTable = ({ servers, loading }) => {
  return (
    <div className="table-container">
      <div className="d-flex justify-content-between align-items-center p-3 border-bottom">
        <h6 className="mb-0">Top Active Servers</h6>
        <button className="btn btn-sm btn-outline-primary" disabled={loading}>
          <i className={`bi bi-arrow-clockwise ${loading ? 'spinner-border spinner-border-sm' : ''}`}></i> {loading ? 'Loading...' : 'Refresh'}
        </button>
      </div>
      <div className="table-responsive">
        <table className="table table-hover mb-0">
          <thead>
            <tr>
              <th>Server</th>
              <th>Members</th>
              <th>Commands Today</th>
              <th>AI Usage</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              [...Array(3)].map((_, i) => (
                <tr key={i}>
                  <td>
                    <div className="placeholder-glow d-flex align-items-center">
                      <div className="me-2" style={{ width: '32px', height: '32px', borderRadius: '50%' }}>
                        <span className="placeholder rounded-circle w-100 h-100"></span>
                      </div>
                      <div style={{ width: '180px' }}>
                        <span className="placeholder col-12"></span>
                        <span className="placeholder col-8"></span>
                      </div>
                    </div>
                  </td>
                  <td><span className="placeholder col-6"></span></td>
                  <td><span className="placeholder col-4"></span></td>
                  <td><span className="placeholder col-12"></span></td>
                  <td><span className="placeholder col-6"></span></td>
                </tr>
              ))
            ) : (
              servers.map((server, index) => (
                <tr key={index}>
                  <td>
                    <div className="d-flex align-items-center">
                      <div className="server-icon me-2" style={{ width: '32px', height: '32px', backgroundColor: server.iconColor, borderRadius: '50%' }}></div>
                      <div>
                        <div className="fw-bold">{server.name}</div>
                        <div className="small text-muted">ID: {server.id}</div>
                      </div>
                    </div>
                  </td>
                  <td>{server.members.toLocaleString()}</td>
                  <td>{server.commandsToday.toLocaleString()}</td>
                  <td>
                    <div className="progress" style={{ height: '8px' }}>
                      <div 
                        className="progress-bar bg-success" 
                        role="progressbar" 
                        style={{ width: `${server.aiUsage}%` }} 
                        aria-valuenow={server.aiUsage} 
                        aria-valuemin="0" 
                        aria-valuemax="100"
                      ></div>
                    </div>
                  </td>
                  <td>
                    <span className={`badge bg-${server.status === 'online' ? 'success' : 'danger'}`}>
                      {server.status === 'online' ? 'Online' : 'Offline'}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// Render the Dashboard component to the DOM
document.addEventListener('DOMContentLoaded', function() {
  const root = document.getElementById('analytics-dashboard-root');
  if (root) {
    ReactDOM.render(React.createElement(Dashboard), root);
  }
});
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #0f172a;
    color: white;
}

.app-shell {
    display: flex;
    min-height: 100vh;
}

.sidebar {
    width: 260px;
    background: linear-gradient(180deg, #0f172a, #1e293b);
    padding: 20px;
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    border-right: 1px solid rgba(255, 255, 255, 0.08);
}

.brand-block {
    text-align: center;
    margin-bottom: 30px;
}

.sidebar-logo {
    width: 120px;
    max-width: 100%;
    margin-bottom: 12px;
}

.nav-menu {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.nav-menu a {
    color: white;
    text-decoration: none;
    padding: 12px 14px;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.05);
    transition: 0.2s ease;
}

.nav-menu a:hover {
    background: linear-gradient(145deg, #f59e0b, #f97316);
    color: black;
}

.main-content {
    margin-left: 260px;
    width: calc(100% - 260px);
    padding: 30px;
}

.flash-wrap {
    margin-bottom: 20px;
}

.flash-message {
    padding: 14px 16px;
    border-radius: 12px;
    margin-bottom: 10px;
    font-weight: bold;
}

.flash-message.success {
    background: rgba(16, 185, 129, 0.18);
    border: 1px solid rgba(16, 185, 129, 0.55);
    color: #d1fae5;
}

.flash-message.error {
    background: rgba(239, 68, 68, 0.18);
    border: 1px solid rgba(239, 68, 68, 0.55);
    color: #fee2e2;
}

.command-center {
    text-align: center;
}

.logo-center {
    margin-bottom: 24px;
}

.main-logo {
    width: 14%;
    min-width: 140px;
    max-width: 220px;
}

.subtitle {
    color: #cbd5e1;
    margin-bottom: 30px;
}

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.metric-card {
    background: linear-gradient(145deg, #1e293b, #0f172a);
    padding: 20px;
    border-radius: 16px;
    box-shadow: 6px 6px 14px rgba(0, 0, 0, 0.45);
}

.metric-card h3 {
    margin-top: 0;
    color: #fbbf24;
}

.metric-card p {
    font-size: 28px;
    font-weight: bold;
    margin-bottom: 0;
}

.module-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
    gap: 22px;
    margin: 35px 0;
}

.module-button {
    display: block;
    padding: 26px;
    font-size: 20px;
    font-weight: bold;
    text-decoration: none;
    color: white;
    background: linear-gradient(145deg, #0f172a, #1e40af);
    border-radius: 18px;
    box-shadow: 6px 6px 12px #0a0f1a, -4px -4px 10px rgba(255, 255, 255, 0.06);
    transition: all 0.2s ease;
}

.module-button:hover {
    transform: translateY(-4px) scale(1.02);
    background: linear-gradient(145deg, #fbbf24, #f97316);
    color: black;
}

.chart-panel {
    background: linear-gradient(145deg, #111827, #1f2937);
    padding: 24px;
    border-radius: 18px;
    box-shadow: 6px 6px 14px rgba(0, 0, 0, 0.45);
    margin-top: 20px;
}

#samiWidget {
    position: fixed;
    right: 28px;
    bottom: 28px;
    width: 78px;
    height: 78px;
    border-radius: 50%;
    background: linear-gradient(145deg, #fbbf24, #f97316);
    color: black;
    font-weight: bold;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    box-shadow: 0 0 18px rgba(0, 0, 0, 0.45);
}

.module-page {
    max-width: 1200px;
    margin: 0 auto;
}

.module-header {
    margin-bottom: 28px;
}

.module-header h1 {
    margin-bottom: 8px;
    color: #fbbf24;
}

.module-header p {
    color: #cbd5e1;
    margin-top: 0;
}

.module-info-grid,
.crm-layout {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 22px;
}

.info-card {
    background: linear-gradient(145deg, #111827, #1f2937);
    border-radius: 18px;
    padding: 24px;
    box-shadow: 6px 6px 14px rgba(0, 0, 0, 0.45);
    text-align: left;
}

.info-card h3 {
    margin-top: 0;
    color: #fbbf24;
}

.info-card p {
    color: #e2e8f0;
    line-height: 1.5;
    margin-bottom: 0;
}

.crm-form {
    display: grid;
    gap: 12px;
}

.crm-form label {
    font-weight: bold;
    color: #fbbf24;
}

.crm-form input {
    padding: 12px;
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    background: #0f172a;
    color: white;
}

.action-button {
    margin-top: 8px;
    padding: 14px 16px;
    border: none;
    border-radius: 12px;
    font-size: 16px;
    font-weight: bold;
    cursor: pointer;
    background: linear-gradient(145deg, #fbbf24, #f97316);
    color: black;
}

.action-button:hover {
    opacity: 0.95;
}

.module-list {
    margin-bottom: 0;
    padding-left: 20px;
    color: #e2e8f0;
}

.table-card {
    margin-top: 24px;
}

.table-wrap {
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
}

thead {
    background: rgba(255, 255, 255, 0.06);
}

th,
td {
    padding: 14px 12px;
    text-align: left;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

th {
    color: #fbbf24;
}

td {
    color: #e2e8f0;
}

@media (max-width: 900px) {
    .sidebar {
        position: relative;
        width: 100%;
        height: auto;
    }

    .app-shell {
        flex-direction: column;
    }

    .main-content {
        margin-left: 0;
        width: 100%;
    }

    .main-logo {
        width: 28%;
    }

    #samiWidget {
        width: 66px;
        height: 66px;
        right: 18px;
        bottom: 18px;
    }
}
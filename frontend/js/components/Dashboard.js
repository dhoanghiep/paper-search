import { api } from '../api.js';

export async function Dashboard() {
    try {
        const stats = await api.get('/stats');
        const recentPapers = await api.get('/papers?limit=5');

        return `
            <h2>Dashboard</h2>
            <div class="stats">
                <div class="stat-card">
                    <h3>Total Papers</h3>
                    <div class="value">${stats.total_papers || 0}</div>
                </div>
                <div class="stat-card">
                    <h3>Categories</h3>
                    <div class="value">${stats.total_categories || 0}</div>
                </div>
                <div class="stat-card">
                    <h3>This Week</h3>
                    <div class="value">${stats.papers_this_week || 0}</div>
                </div>
            </div>
            
            <div class="card">
                <h3>Recent Papers</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Title</th>
                            <th>Category</th>
                            <th>Date</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${recentPapers.map(p => `
                            <tr>
                                <td><a href="#paper/${p.id}">${p.title}</a></td>
                                <td>${p.category || 'Uncategorized'}</td>
                                <td>${new Date(p.published_date).toLocaleDateString()}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    } catch (error) {
        return `<div class="card">Error loading dashboard: ${error.message}</div>`;
    }
}

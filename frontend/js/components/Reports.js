import { api } from '../api.js';

export async function Reports() {
    try {
        const reports = await api.get('/reports');

        return `
            <h2>Reports</h2>
            <div class="card">
                <table>
                    <thead>
                        <tr>
                            <th>Report Type</th>
                            <th>Date</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${reports.map(r => `
                            <tr>
                                <td>${r.type}</td>
                                <td>${new Date(r.created_at).toLocaleDateString()}</td>
                                <td><button class="btn btn-primary">Download</button></td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    } catch (error) {
        return `<div class="card">Error loading reports: ${error.message}</div>`;
    }
}

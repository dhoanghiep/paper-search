import { api } from '../api.js';

export async function Categories() {
    try {
        const categories = await api.get('/categories');

        return `
            <h2>Categories</h2>
            <div class="card">
                <table>
                    <thead>
                        <tr>
                            <th>Category</th>
                            <th>Paper Count</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${categories.map(c => `
                            <tr>
                                <td>${c.name}</td>
                                <td>${c.count || 0}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    } catch (error) {
        return `<div class="card">Error loading categories: ${error.message}</div>`;
    }
}

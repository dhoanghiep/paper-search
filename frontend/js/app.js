import { Dashboard } from './components/Dashboard.js';
import { PapersList } from './components/PapersList.js';
import { PaperDetail } from './components/PaperDetail.js';
import { Categories } from './components/Categories.js';
import { Reports } from './components/Reports.js';

const app = document.getElementById('app');

const routes = {
    'dashboard': Dashboard,
    'papers': PapersList,
    'categories': Categories,
    'reports': Reports
};

async function render(page, params) {
    app.innerHTML = '<div class="loading">Loading...</div>';
    
    try {
        let content;
        if (page === 'paper' && params) {
            content = await PaperDetail(params);
        } else {
            const component = routes[page] || routes['dashboard'];
            content = await component();
        }
        app.innerHTML = content;
    } catch (error) {
        app.innerHTML = `<div class="card">Error: ${error.message}</div>`;
    }
}

function router() {
    const hash = window.location.hash.slice(1) || 'dashboard';
    const [page, ...params] = hash.split('/');
    render(page, params[0]);
}

document.querySelectorAll('.nav-links a').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const page = e.target.dataset.page;
        window.location.hash = page;
    });
});

window.addEventListener('hashchange', router);
window.addEventListener('load', router);

window.viewPaper = (id) => {
    window.location.hash = `paper/${id}`;
};

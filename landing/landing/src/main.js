import './style.css'

const yearEl = document.getElementById('year')
if (yearEl) yearEl.textContent = new Date().getFullYear()


// Tabs
document.querySelectorAll('.tab').forEach(btn => {
btn.addEventListener('click', () => {
document.querySelectorAll('.tab').forEach(b => b.dataset.active = 'false')
document.querySelectorAll('.tab-pane').forEach(p => p.classList.add('hidden'))
btn.dataset.active = 'true'
document.querySelector(btn.dataset.target).classList.remove('hidden')
})
})


// Copy
function decodeHtml(html) { const txt = document.createElement('textarea'); txt.innerHTML = html; return txt.value }
document.querySelectorAll('.copy').forEach(btn => {
btn.addEventListener('click', async () => {
const raw = btn.getAttribute('data-copy')
const text = decodeHtml(raw)
try { await navigator.clipboard.writeText(text); btn.textContent = 'Kopiert!'; setTimeout(()=>btn.textContent='Kopieren',1200) } catch { alert('Kopieren nicht möglich') }
})
})
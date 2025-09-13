// src/blog.js
function decodeHtml(html) { const t = document.createElement('textarea'); t.innerHTML = html; return t.value }

document.querySelectorAll('.copy').forEach(btn => {
  btn.addEventListener('click', async () => {
    const raw = btn.getAttribute('data-copy')
    const text = decodeHtml(raw)
    try { await navigator.clipboard.writeText(text); btn.textContent = 'Copied!'; setTimeout(()=>btn.textContent='Copy',1200) }
    catch { alert('Copy failed') }
  })
})

const y = new Date().getFullYear()
const yearTop = document.getElementById('year')
if (yearTop) yearTop.textContent = y
const yearFooter = document.getElementById('year-footer')
if (yearFooter) yearFooter.textContent = y

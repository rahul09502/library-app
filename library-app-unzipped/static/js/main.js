document.getElementById('go').addEventListener('click', doSearch)
document.getElementById('q').addEventListener('keydown', function(e){ if(e.key === 'Enter') doSearch() })

function doSearch(){
  const q = document.getElementById('q').value
  const dept = document.getElementById('dept').value
  const min_year = document.getElementById('min_year') ? document.getElementById('min_year').value : ''
  const max_year = document.getElementById('max_year') ? document.getElementById('max_year').value : ''
  const available = document.getElementById('available') && document.getElementById('available').checked ? '1' : ''
  const url = `/api/search?q=${encodeURIComponent(q)}&dept=${encodeURIComponent(dept)}&min_year=${encodeURIComponent(min_year)}&max_year=${encodeURIComponent(max_year)}&available=${encodeURIComponent(available)}`
  fetch(url).then(r=>r.json()).then(render)
}

function render(data){
  const out = document.getElementById('results')
  if(!data || data.length === 0){ out.innerHTML = '<p>No books found.</p>'; return }
  out.innerHTML = data.map(b => {
    const loggedIn = (typeof STUDENT_LOGGED_IN !== 'undefined' && (STUDENT_LOGGED_IN === true || STUDENT_LOGGED_IN === 'true'))
    let borrowBtn = ''
    if(loggedIn){
      if(typeof STUDENT_BORROW_COUNT !== 'undefined' && STUDENT_BORROW_COUNT >= 3){
        borrowBtn = `<button class="btn btn-sm btn-secondary" disabled>Borrow (limit reached)</button>`
      } else {
        // use JS helper to create POST form so CSRF token is always included
        borrowBtn = `<button class="btn btn-sm btn-primary" type="button" onclick="submitPost('/student/borrow/${b.id}')">Borrow</button>`
      }
    }
    return `
    <div class="book p-3 mb-2 border rounded">
      <div class="title"><strong>${escapeHtml(b.title)}</strong></div>
      <div class="meta text-muted">${escapeHtml(b.author)} — ${b.year || ''} — ${escapeHtml(b.department)} — ISBN: ${escapeHtml(b.isbn || '')} — Copies: ${b.copies}</div>
      <div style="margin-top:8px">${borrowBtn}</div>
    </div>`
  }).join('')
}

function submitPost(path){
  const f = document.createElement('form')
  f.method = 'POST'
  f.action = path
  // include CSRF token if available
  if(typeof CSRFTOKEN !== 'undefined'){
    const inp = document.createElement('input')
    inp.type = 'hidden'
    inp.name = 'csrf_token'
    inp.value = CSRFTOKEN
    f.appendChild(inp)
  }
  document.body.appendChild(f)
  f.submit()
}

function escapeHtml(s){ if(!s) return ''; return s.replace(/[&<>"']/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":"&#39;"}[c] }) }

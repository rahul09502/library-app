// Simple client-side validation for forms with .needs-validation
document.addEventListener('DOMContentLoaded', function(){
  document.querySelectorAll('form.needs-validation').forEach(form=>{
    form.addEventListener('submit', function(e){
      let valid = true
      form.querySelectorAll('[required]').forEach(inp=>{
        if(!inp.value || inp.value.trim() === '') valid = false
      })
      // numeric checks
      form.querySelectorAll('input[data-validate="int"]').forEach(inp=>{
        if(inp.value && !/^\d+$/.test(inp.value)) valid = false
      })
      if(!valid){
        e.preventDefault(); e.stopPropagation();
        alert('Please fix the highlighted fields before submitting.')
      }
    })
  })
})

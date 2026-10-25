document.addEventListener('DOMContentLoaded',()=>{
 document.querySelectorAll('[data-dismiss]').forEach(b=>b.addEventListener('click',()=>b.closest('.flash').remove()));
 document.querySelectorAll('form[data-confirm]').forEach(f=>f.addEventListener('submit',e=>{if(!confirm(f.dataset.confirm))e.preventDefault()}));
 const toggle=document.querySelector('[data-menu-toggle]'), nav=document.querySelector('[data-mobile-nav]'); if(toggle&&nav)toggle.addEventListener('click',()=>nav.classList.toggle('open'));
 const type=document.querySelector('#movement-type'), reason=document.querySelector('#movement-reason');
 if(type&&reason){const update=()=>{if(type.value==='in'){reason.options[0].hidden=false; if(['Sale','Damaged','Expired'].includes(reason.value))reason.value='Supplier delivery';}else{reason.options[0].hidden=true;if(reason.value==='Supplier delivery')reason.value='Sale';}};type.addEventListener('change',update);update();}
});

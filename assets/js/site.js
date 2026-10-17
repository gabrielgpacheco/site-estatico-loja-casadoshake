(function(){
  // Filtro da home
  var grid=document.getElementById('grid');
  if(grid){
    var cards=Array.prototype.slice.call(grid.querySelectorAll('.card'));
    var q=document.getElementById('q');
    var chips=Array.prototype.slice.call(document.querySelectorAll('.chip[data-cat]'));
    var active='all';
    function apply(){
      var t=(q&&q.value?q.value:'').toLowerCase().trim();
      cards.forEach(function(c){
        var okT=!t||c.dataset.title.indexOf(t)>=0;
        var okC=active==='all'||(' '+c.dataset.cats+' ').indexOf(' '+active+' ')>=0;
        c.style.display=(okT&&okC)?'':'none';
      });
    }
    function setCat(cat){
      active=cat||'all';
      chips.forEach(function(ch){ch.classList.toggle('active',ch.dataset.cat===active);});
      apply();
    }
    chips.forEach(function(ch){ch.addEventListener('click',function(e){e.preventDefault();setCat(ch.dataset.cat);history.replaceState(null,'','#anchor');});});
    if(q)q.addEventListener('input',apply);
    if(location.hash){setCat(location.hash.slice(1));}else{setCat('all');}
  }
  // Galeria do produto
  var main=document.getElementById('mainimg');
  if(main){
    document.querySelectorAll('.thumbs img').forEach(function(t){
      t.addEventListener('click',function(){
        main.src=t.dataset.full;
        document.querySelectorAll('.thumbs img').forEach(function(x){x.classList.remove('active');});
        t.classList.add('active');
      });
    });
  }
  // Variacoes -> mensagem WhatsApp
  var wa=document.getElementById('wa');
  if(wa){
    function build(){
      var parts=[];
      document.querySelectorAll('.opt input:checked').forEach(function(i){
        parts.push(i.dataset.label+': '+i.value.replace(/-/g,' '));
      });
      var msg='Ola! Tenho interesse no produto: '+wa.dataset.title;
      if(parts.length)msg+=' ('+parts.join(', ')+')';
      wa.href='https://wa.me/'+wa.dataset.phone+'?text='+encodeURIComponent(msg);
    }
    document.querySelectorAll('.opt input').forEach(function(i){i.addEventListener('change',build);});
    build();
  }
})();

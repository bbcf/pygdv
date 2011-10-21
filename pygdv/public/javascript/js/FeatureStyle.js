function getFeatureStyle(type,div){
   div.style.backgroundColor='#3333D7';
   div.className='basic';
   switch(type){
   case 'stop_codon' : div.style.height='10px';
       div.style.marginTop='-4px';
       div.style.zIndex='30';
       div.style.backgroundColor='red';
       break;
   case 'CDS' : div.style.height='10px';
       div.style.marginTop='-4px';
       div.style.zIndex='30';
       div.style.backgroundColor='yellow';
       break;
   case 'exon' : div.style.height='20px';
       div.style.marginTop='-8px';
       div.style.zIndex='20';
       div.style.backgroundColor='blue';
       break;
   case 'start_codon' : div.style.height='10px';
       div.style.marginTop='-4px';
       div.style.zIndex='30';
       div.style.backgroundColor='red';
       break;}
};

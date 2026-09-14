/* Photography follows the existing industry selector and validated entry links. */
(function(){
 'use strict';
 const photo=document.getElementById('industry-photo');
 const caption=document.getElementById('industry-photo-caption');
 if(!photo||!caption)return;
 const cases={"retail": {"key": "retail", "width": 1280, "height": 855, "es": "Una emprendedora revisa documentos junto a un portátil, cajas y prendas.", "en": "A shop professional reviews paperwork beside packages and a laptop.", "labelEs": "Comercio", "labelEn": "Retail", "focus": "43% 50%"}, "professional": {"key": "advisory", "width": 1280, "height": 853, "es": "Un asesor explica documentación a otra persona durante una reunión.", "en": "An advisor discusses documents during a meeting.", "labelEs": "Servicios profesionales", "labelEn": "Professional services", "focus": "43% 50%"}, "construction": {"key": "construction", "width": 1280, "height": 853, "es": "Una profesional con casco consulta una tableta en una obra.", "en": "A construction professional in a hard hat uses a tablet on site.", "labelEs": "Construcción", "labelEn": "Construction", "focus": "44% 50%"}, "food": {"key": "restaurant", "width": 1280, "height": 853, "es": "Una profesional de cafetería atiende en el mostrador con una tableta.", "en": "A cafe professional uses a tablet at the counter.", "labelEs": "Restaurantes", "labelEn": "Restaurants", "focus": "59% 48%"}, "beauty": {"key": "beauty", "width": 1280, "height": 853, "es": "Una peluquera seca el cabello de una clienta en un salón con luz natural.", "en": "A hairdresser works with a customer in a salon.", "labelEs": "Belleza", "labelEn": "Beauty", "focus": "48% 50%"}};
 const en=document.documentElement.lang==='en';
 const buttons=Array.from(document.querySelectorAll('[data-industry]'));
 function select(key){
  if(!Object.prototype.hasOwnProperty.call(cases,key))return;
  const item=cases[key];
  photo.srcset='/assets/editorial/'+item.key+'-720.webp 720w, /assets/editorial/'+item.key+'.webp 1280w';
  photo.src='/assets/editorial/'+item.key+'.webp';
  photo.width=item.width;photo.height=item.height;
  photo.alt=en?item.en:item.es;
  photo.style.objectPosition=item.focus;
  caption.textContent=en?item.labelEn:item.labelEs;
 }
 buttons.forEach(button=>button.addEventListener('click',()=>select(button.dataset.industry)));
 const requested=new URLSearchParams(window.location.search).get('sector');
 const target=buttons.find(button=>button.dataset.industry===requested);
 if(target)target.click();
}());

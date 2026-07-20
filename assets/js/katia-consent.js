(function () {
  'use strict';
  var key='katia_analytics_consent_v1';
  function read(){var m=document.cookie.match(new RegExp('(?:^|; )'+key+'=([^;]*)'));return m?decodeURIComponent(m[1]):'';}
  function write(v){document.cookie=key+'='+encodeURIComponent(v)+'; Max-Age=15552000; Path=/; SameSite=Lax; Secure';}
  function loadAnalytics(){
    if(window.__katiaAnalyticsLoaded)return;
    window.__katiaAnalyticsLoaded=true;
    window.dataLayer=window.dataLayer||[];
    window.gtag=function(){window.dataLayer.push(arguments);};
    window.gtag('consent','default',{analytics_storage:'granted',ad_storage:'granted',ad_user_data:'granted',ad_personalization:'granted'});
    window.gtag('js',new Date());
    window.gtag('config','G-LKNZZY2Z9Y',{anonymize_ip:true});
    window.gtag('config','AW-18207097336');
    var ga=document.createElement('script');ga.async=true;ga.src='https://www.googletagmanager.com/gtag/js?id=G-LKNZZY2Z9Y';document.head.appendChild(ga);
    !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');
    window.fbq('init','2021221848741117');window.fbq('track','PageView');
  }
  function removeBanner(){var b=document.getElementById('katia-consent-banner');if(b)b.remove();}
  function decide(value){write(value);removeBanner();if(value==='accepted')loadAnalytics();}
  function show(){
    if(document.getElementById('katia-consent-banner'))return;
    var b=document.createElement('section');
    b.id='katia-consent-banner';b.setAttribute('role','dialog');b.setAttribute('aria-label','Preferencias de privacidad');
    b.style.cssText='position:fixed;z-index:9999;left:16px;right:16px;bottom:16px;max-width:720px;margin:auto;padding:18px 20px;border:1px solid rgba(106,160,255,.45);border-radius:16px;background:#07112a;color:#eef3ff;box-shadow:0 20px 60px rgba(0,0,0,.45);font:14px/1.5 Inter,system-ui,sans-serif';
    b.innerHTML='<strong style="display:block;font-size:15px;margin-bottom:6px">Su privacidad importa</strong><span>Usamos analítica y medición de campañas solo si usted la acepta. Puede rechazarla y seguir usando el sitio.</span><p style="margin:8px 0 14px"><a href="/privacidad.html" style="color:#9cc0ff">Política de Privacidad</a></p><div style="display:flex;gap:10px;flex-wrap:wrap"><button type="button" data-choice="rejected" style="padding:10px 14px;border:1px solid #60739d;border-radius:9px;background:transparent;color:#fff;font-weight:700;cursor:pointer">Rechazar</button><button type="button" data-choice="accepted" style="padding:10px 14px;border:0;border-radius:9px;background:#3a78ff;color:#fff;font-weight:700;cursor:pointer">Aceptar analítica</button></div>';
    b.addEventListener('click',function(e){var btn=e.target.closest('[data-choice]');if(btn)decide(btn.getAttribute('data-choice'));});
    document.body.appendChild(b);
  }
  window.KATIAPrivacy={accept:function(){decide('accepted');},reject:function(){decide('rejected');},status:read};
  var choice=read();
  if(choice==='accepted')loadAnalytics();
  else if(!choice){if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',show);else show();}
}());
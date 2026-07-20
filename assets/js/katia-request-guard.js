(function () {
  'use strict';
  var prefix='katia_request_guard_v1_';
  function now(){return Date.now();}
  function allow(key,limit,windowMs){
    try{
      var raw=sessionStorage.getItem(prefix+key),list=raw?JSON.parse(raw):[];
      list=list.filter(function(ts){return now()-ts<windowMs;});
      if(list.length>=limit)return false;
      list.push(now());sessionStorage.setItem(prefix+key,JSON.stringify(list));return true;
    }catch(e){return true;}
  }
  function hasSensitiveText(value){
    var s=String(value||'');
    return /\b\d{3}-?\d{2}-?\d{4}\b/.test(s)||/\b(?:\d[ -]?){13,19}\b/.test(s);
  }
  function text(v,max){return String(v||'').trim().slice(0,max);}
  function validateLead(payload){
    if(!allow('lead',3,60*60*1000))return {ok:false,message:'Por seguridad, espere unos minutos antes de enviar otra solicitud.'};
    var body=JSON.stringify(payload);
    if(body.length>12000)return {ok:false,message:'La solicitud es demasiado extensa. Resuma el mensaje e intente de nuevo.'};
    if(hasSensitiveText(payload.dolor)||hasSensitiveText(payload.texto_libre)||hasSensitiveText(payload.notas))return {ok:false,message:'Por seguridad, no envíe números de tarjeta, SSN/ITIN ni datos bancarios por este formulario.'};
    ['nombre','empresa','ciudad','dolor','texto_libre','notas'].forEach(function(k){if(Object.prototype.hasOwnProperty.call(payload,k))payload[k]=text(payload[k],k==='dolor'||k==='texto_libre'||k==='notas'?1200:160);});
    return {ok:true};
  }
  function validateChat(message){
    if(!allow('chat',8,10*60*1000))return {ok:false,message:'Ha alcanzado el límite de mensajes. Escríbanos a ventas@katia.solutions para continuar.'};
    if(!message||message.length>1000)return {ok:false,message:'Escriba un mensaje de hasta 1,000 caracteres.'};
    if(hasSensitiveText(message))return {ok:false,message:'Por seguridad, no envíe números de tarjeta, SSN/ITIN ni datos bancarios por el chat.'};
    return {ok:true};
  }
  window.KatiaRequestGuard={validateLead:validateLead,validateChat:validateChat};
}());
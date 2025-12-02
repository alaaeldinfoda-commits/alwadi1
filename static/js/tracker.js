
(function(){
  // Background GPS tracker: sends point every n seconds when user is logged in and has a current report id
  var intervalSec = 15; // seconds
  var sending = false;

  function sendPoint(lat,lng,report_id){
    if(!report_id) report_id = null;
    fetch('/gps_log', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({lat:lat, lng:lng, report_id: report_id})
    }).catch(function(e){ console.error('gps_log error', e); });
  }

  function startTracking(){
    if (!navigator.geolocation) return;
    // initial send
    navigator.geolocation.getCurrentPosition(function(p){
      var lat = p.coords.latitude, lng=p.coords.longitude;
      var rid = window.report_id || null;
      sendPoint(lat,lng,rid);
    });
    // periodic watch
    setInterval(function(){
      navigator.geolocation.getCurrentPosition(function(pos){
        var lat = pos.coords.latitude, lng = pos.coords.longitude;
        var rid = window.report_id || null;
        sendPoint(lat,lng,rid);
      });
    }, intervalSec*1000);
  }

  // start automatically if logged in
  document.addEventListener('DOMContentLoaded', function(){
    // server injects window.__logged_in = true for logged users
    if(window.__logged_in){
      startTracking();
    }
  });
})();

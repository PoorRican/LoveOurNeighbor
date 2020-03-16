function show_notification(message, tags = null) {
  M.toast({html: message});
}

function get_notifications(url) {
  $.getJSON(url, null, function (data) {
    const notifications = data['notifications'];
    for (let i = 0; i < notifications.length; i++) {
      let n = notifications[i];
      show_notification(n.message, n.tags);
    }
  })
}
function open_collapsible(el) {
  let i = el.getElementsByClassName('collapsible-header')[0].getElementsByClassName('material-icons')[0];
  i.classList.add('rotate-90');
  console.log('open');
}

function close_collapsible(el) {
  let i = el.getElementsByClassName('collapsible-header')[0].getElementsByClassName('material-icons')[0];
  i.classList.remove('rotate-90');
  console.log('close');
}

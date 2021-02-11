const filterWrappers = document.querySelectorAll('.filter-wrapper');

// Change this breakpoint to fit your theme's breakpoint
const breakpoint = 958;

function togglePreventDefault(e) {
  e.stopPropagation();
  e.preventDefault();
}

function preventDefaultOnWrapper(wrapper, button) {
  if (window.innerWidth >= breakpoint) {
    button.addEventListener('click', togglePreventDefault);
    TurnDetailsOn(wrapper);
  } else {
    button.removeEventListener('click', togglePreventDefault);
    TurnDetailsOff(wrapper);
  }
}

function TurnDetailsOn(wrapper) {
  if (!wrapper.hasAttribute('open')) {
    wrapper.setAttribute('open', '');
  }
}

function TurnDetailsOff(wrapper) {
  if (wrapper.hasAttribute('open')) {
    wrapper.removeAttribute('open');
  }
}

filterWrappers.forEach((filterWrapper) => {
  let filterButton = filterWrapper.querySelector('.filter-wrapper__summary')
  preventDefaultOnWrapper(filterWrapper, filterButton);

  window.addEventListener('resize', e => {
    preventDefaultOnWrapper(filterWrapper, filterButton);
  })
})

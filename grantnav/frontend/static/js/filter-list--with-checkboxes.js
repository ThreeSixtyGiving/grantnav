const filterListWithCheckboxes = document.querySelectorAll('.filter-list--with-checkboxes');

filterListWithCheckboxes.forEach(filterList => {
  const checkboxes = filterList.querySelectorAll('.filter-list__form--checkbox-item input');

  const buttonsItem = filterList.querySelectorAll('.filter-list__form--summary-item');

  checkboxes.forEach(checkbox => {
    checkbox.addEventListener('change', e => {
      const checkboxId = checkbox.getAttribute('id');

      if (checkbox.checked) {
        buttonsItem.forEach(buttonItem => {
          let id = buttonItem.getAttribute('data-option-id');

          if (id == checkboxId) {
            buttonItem.classList.add('active');
          }
        })
      } else {
        buttonsItem.forEach(buttonItem => {
          let id = buttonItem.getAttribute('data-option-id');

          if (id == checkboxId) {
            buttonItem.classList.remove('active');
          }
        })
      }
    })
  })

  buttonsItem.forEach(buttonItem => {
    const id = buttonItem.getAttribute('data-option-id');
    const button = buttonItem.querySelector('button');

    button.addEventListener('click', e => {
      e.preventDefault();

      checkboxes.forEach(checkbox => {
        const checkboxId = checkbox.getAttribute('id');

        if (id == checkboxId) {
          checkbox.checked = false;
          buttonItem.classList.remove('active');
        }
      })
    })
  })
})

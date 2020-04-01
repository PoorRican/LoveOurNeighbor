$(function () {
  $.fn.filepond.registerPlugin(FilePondPluginImagePreview);

  /**
   * @brief Load any initial files
   *
   * These are typically hidden elements placed in the form element while in an editing template.
   */
  let files = $('input[name="load"]').map(function () {
    return {
      source: $(this).val(),
      options: {type: 'local'}
    }
  }).get();

  let fp = $('.filepond');

  /**
   * @see https://pqina.nl/filepond/docs/patterns/api/filepond-object/
   */
  fp.filepond({
    allowMultiple: true,
    name: 'media',
    files: files,
    server: {
      url: '/fp',
      process: {
        headers: {"X-CSRFToken": $('input[name="csrfmiddlewaretoken"]').val(),},
        url: '/process/',
        /**
         * @brief used because form element name is not 'filepond'
         *
         * @ignore any linter/static analysis error about this property not being used
         *
         * @see https://github.com/ImperialCollegeLondon/django-drf-filepond/issues/4
         */
        ondata: (formData) => {
          let upload_field = '';
          for (let item of formData.keys()) {
            upload_field = item;
            break;
          }
          if (upload_field !== '') {
            formData.append('fp_upload_field', upload_field);
          }
          return formData;
        },
        onerror: (response) => {
          console.log(response.data);
        }
      },
      revert: '/revert/',
      fetch: '/fetch/?id=',
      load: '/load/?id='

    }
  });
  fp.on('FilePond:addfile', function (e) {
    console.log('file added event', e);
  });

});

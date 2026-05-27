(() => {
  if (window.__psBuilderInjected) return;
  window.__psBuilderInjected = true;

  let recording = false;

  function getSelector(el) {
    if (!el || el.nodeType !== 1) return null;
    if (el.id) return `#${CSS.escape(el.id)}`;
    const path = [];
    let cur = el;
    while (cur && cur.nodeType === 1 && cur !== document.body && path.length < 6) {
      let part = cur.tagName.toLowerCase();
      const cls = (cur.getAttribute('class') || '').trim().split(/\s+/).filter(Boolean).slice(0, 2);
      if (cls.length) part += '.' + cls.map(c => CSS.escape(c)).join('.');
      const parent = cur.parentElement;
      if (parent) {
        const siblings = Array.from(parent.children).filter(c => c.tagName === cur.tagName);
        if (siblings.length > 1) {
          const idx = siblings.indexOf(cur) + 1;
          part += `:nth-of-type(${idx})`;
        }
      }
      path.unshift(part);
      cur = cur.parentElement;
    }
    return path.join(' > ');
  }

  function getAccessibleName(el) {
    if (!el) return '';
    try {
      const labelFor = el.id && document.querySelector(`label[for="${CSS.escape(el.id)}"]`);
      return (
        el.getAttribute('aria-label') ||
        el.getAttribute('title') ||
        (labelFor && labelFor.innerText && labelFor.innerText.trim()) ||
        (el.closest && el.closest('label') && el.closest('label').innerText && el.closest('label').innerText.trim()) ||
        (el.innerText && el.innerText.trim().slice(0, 100)) ||
        el.getAttribute('placeholder') ||
        ''
      );
    } catch (_) {
      return '';
    }
  }

  function describeElement(el) {
    if (!el) return null;
    return {
      tag: el.tagName ? el.tagName.toLowerCase() : null,
      selector: getSelector(el),
      text: el.innerText ? el.innerText.trim().slice(0, 200) : '',
      accessible_name: getAccessibleName(el),
      role: el.getAttribute ? el.getAttribute('role') : null,
      href: el.tagName === 'A' ? el.href : undefined,
    };
  }

  function describeFormField(el) {
    if (!el || !['INPUT', 'SELECT', 'TEXTAREA'].includes(el.tagName)) return undefined;
    const type = (el.type || '').toLowerCase();
    let value = el.value;
    if (type === 'password') value = '[REDACTED]';
    if (typeof value === 'string' && value.length > 500) value = value.slice(0, 500) + '…';
    return {
      name: el.name || el.id || '',
      type,
      value,
      placeholder: el.placeholder || '',
      label: getAccessibleName(el),
    };
  }

  function send(event) {
    try {
      chrome.runtime.sendMessage({ type: 'EVENT_CAPTURED', event }).catch(() => {});
    } catch (_) { /* extension reloaded */ }
  }

  function onClick(e) {
    if (!recording) return;
    const target = (e.target.closest && e.target.closest('a, button, [role="button"], input, select, textarea, label, [onclick]')) || e.target;
    send({
      type: 'click',
      timestamp: new Date().toISOString(),
      url: location.href,
      page_title: document.title,
      element: describeElement(target),
      form_field: describeFormField(target),
    });
  }

  function onChange(e) {
    if (!recording) return;
    const ff = describeFormField(e.target);
    if (!ff) return;
    send({
      type: 'input',
      timestamp: new Date().toISOString(),
      url: location.href,
      page_title: document.title,
      element: describeElement(e.target),
      form_field: ff,
    });
  }

  function onSubmit(e) {
    if (!recording) return;
    send({
      type: 'submit',
      timestamp: new Date().toISOString(),
      url: location.href,
      page_title: document.title,
      element: describeElement(e.target),
    });
  }

  function attach() {
    document.addEventListener('click', onClick, true);
    document.addEventListener('change', onChange, true);
    document.addEventListener('submit', onSubmit, true);
  }

  function detach() {
    document.removeEventListener('click', onClick, true);
    document.removeEventListener('change', onChange, true);
    document.removeEventListener('submit', onSubmit, true);
  }

  chrome.runtime.sendMessage({ type: 'GET_STATE' })
    .then((state) => {
      if (state && state.recording) {
        recording = true;
        attach();
      }
    })
    .catch(() => {});

  chrome.runtime.onMessage.addListener((msg) => {
    if (!msg || !msg.type) return;
    if (msg.type === 'RECORDING_STARTED') { recording = true; attach(); }
    if (msg.type === 'RECORDING_STOPPED') { recording = false; detach(); }
  });
})();

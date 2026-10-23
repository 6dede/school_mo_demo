/* ==========================================================
   公共工具：请求封装 / 提示 / 确认框 / 分页 / 登录态
   ========================================================== */
(function (window) {
  'use strict';

  var LOGIN_KEY = 'edu_admin_login';
  var NAME_KEY = 'edu_admin_name';
  var LOGIN_PAGE = '/static/html/login.html';

  /* ---------- 基础工具 ---------- */
  function escapeHtml(value) {
    if (value === null || value === undefined) return '';
    return String(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function formatDateTime(value) {
    if (!value) return '-';
    var text = String(value).replace('T', ' ').replace(/Z$/, '');
    return text.length > 19 ? text.slice(0, 19) : text;
  }

  function toDateTimeLocal(value) {
    if (!value) return '';
    return String(value).replace(' ', 'T').slice(0, 16);
  }

  function gerderText(value) {
    if (value === 'man') return '男';
    if (value === 'woman') return '女';
    return value || '-';
  }

  function normalizeGerder(value) {
    if (value === 'man') return '男';
    if (value === 'woman') return '女';
    return value || '';
  }

  // 历史数据里可能存在下拉框之外的取值，编辑时补一个选项避免被清空
  function ensureOption(select, value) {
    if (value === null || value === undefined || value === '') return;
    var exists = Array.prototype.some.call(select.options, function (option) {
      return option.value === String(value);
    });
    if (!exists) {
      var option = document.createElement('option');
      option.value = value;
      option.textContent = value;
      select.appendChild(option);
    }
  }

  // 用数据填充下拉框，默认取 name 字段
  function fillSelect(select, items, placeholder, label) {
    if (!select) return;
    select.innerHTML = '<option value="">' + escapeHtml(placeholder || '请选择') + '</option>' +
      (items || []).map(function (item) {
        return '<option value="' + item.id + '">' +
          escapeHtml(label ? label(item) : (item.name || item.subject || item.title || '')) +
          '</option>';
      }).join('');
  }

  function today() {
    var d = new Date();
    d.setMinutes(d.getMinutes() - d.getTimezoneOffset());
    return d.toISOString().slice(0, 10);
  }

  function toDate(value) {
    if (!value) return '';
    return String(value).replace('T', ' ').slice(0, 10);
  }

  /* ---------- 请求封装：统一处理 {code,msg,data} ---------- */
  async function request(url, options) {
    var opts = Object.assign({}, options || {});
    opts.headers = Object.assign({}, opts.headers || {});
    if (opts.body !== undefined && typeof opts.body !== 'string') {
      opts.headers['Content-Type'] = 'application/json';
      opts.body = JSON.stringify(opts.body);
    }

    var response = await fetch(url, opts);
    var payload;
    try {
      payload = await response.json();
    } catch (e) {
      throw new Error('服务返回了无效数据');
    }

    if (!payload || payload.code !== 0) {
      throw new Error((payload && payload.msg) || '请求失败');
    }
    return payload.data;
  }

  /* ---------- 轻提示 ---------- */
  var toastContainer = null;
  function toast(message, type) {
    if (!toastContainer) {
      toastContainer = document.createElement('div');
      toastContainer.className = 'app-toast-container';
      document.body.appendChild(toastContainer);
    }

    var tone = type === 'error' ? 'danger' : type === 'warning' ? 'warning' : type === 'info' ? 'info' : 'success';
    var icon = type === 'error' ? 'bi-x-circle-fill' : type === 'warning' ? 'bi-exclamation-triangle-fill' : type === 'info' ? 'bi-info-circle-fill' : 'bi-check-circle-fill';

    var el = document.createElement('div');
    el.className = 'toast align-items-center text-bg-' + tone;
    el.setAttribute('role', 'alert');
    el.innerHTML =
      '<div class="d-flex">' +
      '<div class="toast-body"><i class="bi ' + icon + ' me-1"></i>' + escapeHtml(message) + '</div>' +
      '<button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>' +
      '</div>';

    toastContainer.appendChild(el);
    var instance = new bootstrap.Toast(el, { delay: 2600 });
    el.addEventListener('hidden.bs.toast', function () {
      el.remove();
    });
    instance.show();
  }

  /* ---------- 确认框 ---------- */
  function confirm(message, title) {
    return new Promise(function (resolve) {
      var wrap = document.createElement('div');
      wrap.className = 'modal fade';
      wrap.setAttribute('tabindex', '-1');
      wrap.innerHTML =
        '<div class="modal-dialog modal-dialog-centered modal-sm">' +
        '<div class="modal-content">' +
        '<div class="modal-header py-3">' +
        '<h5 class="modal-title">' + escapeHtml(title || '操作确认') + '</h5>' +
        '<button type="button" class="btn-close" data-bs-dismiss="modal"></button>' +
        '</div>' +
        '<div class="modal-body">' + escapeHtml(message) + '</div>' +
        '<div class="modal-footer py-2">' +
        '<button type="button" class="btn btn-light btn-sm" data-bs-dismiss="modal">取消</button>' +
        '<button type="button" class="btn btn-danger btn-sm btn-confirm">确定</button>' +
        '</div></div></div>';

      document.body.appendChild(wrap);
      var modal = new bootstrap.Modal(wrap);
      var confirmed = false;

      wrap.querySelector('.btn-confirm').addEventListener('click', function () {
        confirmed = true;
        modal.hide();
      });
      wrap.addEventListener('hidden.bs.modal', function () {
        wrap.remove();
        resolve(confirmed);
      });
      modal.show();
    });
  }

  /* ---------- 分页 ---------- */
  function renderPagination(el, options, onGo) {
    if (!el) return;
    var page = Math.max(1, Number(options.page) || 1);
    var size = Math.max(1, Number(options.size) || 10);
    var total = Math.max(0, Number(options.total) || 0);
    var totalPages = Math.max(1, Math.ceil(total / size));
    var current = Math.min(page, totalPages);

    var start = Math.max(1, current - 2);
    var end = Math.min(totalPages, start + 4);
    start = Math.max(1, end - 4);

    var html =
      '<div class="d-flex flex-wrap justify-content-between align-items-center gap-2">' +
      '<span class="text-muted small">共 ' + total + ' 条，第 ' + current + ' / ' + totalPages + ' 页</span>' +
      '<ul class="pagination pagination-sm mb-0">' +
      '<li class="page-item ' + (current === 1 ? 'disabled' : '') + '">' +
      '<a class="page-link" href="#" data-page="' + (current - 1) + '">上一页</a></li>';

    for (var p = start; p <= end; p++) {
      html +=
        '<li class="page-item ' + (p === current ? 'active' : '') + '">' +
        '<a class="page-link" href="#" data-page="' + p + '">' + p + '</a></li>';
    }

    html +=
      '<li class="page-item ' + (current === totalPages ? 'disabled' : '') + '">' +
      '<a class="page-link" href="#" data-page="' + (current + 1) + '">下一页</a></li>' +
      '</ul></div>';

    el.innerHTML = html;

    el.querySelectorAll('a.page-link').forEach(function (link) {
      link.addEventListener('click', function (event) {
        event.preventDefault();
        var item = link.closest('.page-item');
        if (item.classList.contains('disabled') || item.classList.contains('active')) return;
        var target = Number(link.dataset.page);
        if (target >= 1 && target <= totalPages) onGo(target);
      });
    });
  }

  /* ---------- 登录态 ---------- */
  function isLogin() {
    return sessionStorage.getItem(LOGIN_KEY) === '1';
  }

  function checkLogin() {
    if (!isLogin()) {
      window.top.location.href = LOGIN_PAGE;
      throw new Error('未登录');
    }
  }

  function login(name) {
    sessionStorage.setItem(LOGIN_KEY, '1');
    sessionStorage.setItem(NAME_KEY, name || 'admin');
  }

  function logout() {
    sessionStorage.removeItem(LOGIN_KEY);
    sessionStorage.removeItem(NAME_KEY);
    window.top.location.href = LOGIN_PAGE;
  }

  function adminName() {
    return sessionStorage.getItem(NAME_KEY) || 'admin';
  }

  window.App = {
    LOGIN_PAGE: LOGIN_PAGE,
    request: request,
    toast: toast,
    confirm: confirm,
    renderPagination: renderPagination,
    escapeHtml: escapeHtml,
    formatDateTime: formatDateTime,
    toDateTimeLocal: toDateTimeLocal,
    gerderText: gerderText,
    normalizeGerder: normalizeGerder,
    ensureOption: ensureOption,
    fillSelect: fillSelect,
    today: today,
    toDate: toDate,
    isLogin: isLogin,
    checkLogin: checkLogin,
    login: login,
    logout: logout,
    adminName: adminName
  };
})(window);

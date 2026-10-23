(function () {
  'use strict';

  App.checkLogin();
  if (window.parent && window.parent.setBreadcrumb) {
    window.parent.setBreadcrumb('老师管理', '/static/html/teacher/list.html');
  }

  var state = { page: 1, size: 10, keyword: '', total: 0, rows: [] };

  var tableBody = document.getElementById('tableBody');
  var paginationEl = document.getElementById('pagination');
  var keywordInput = document.getElementById('keyword');
  var pageSizeSelect = document.getElementById('pageSize');

  var modalEl = document.getElementById('teacherModal');
  var modal = new bootstrap.Modal(modalEl);
  var modalTitle = document.getElementById('teacherModalTitle');
  var formError = document.getElementById('teacherFormError');
  var saveBtn = document.getElementById('saveBtn');

  var teaId = document.getElementById('teaId');
  var teaName = document.getElementById('teaName');
  var teaGerder = document.getElementById('teaGerder');
  var teaAge = document.getElementById('teaAge');
  var teaSubject = document.getElementById('teaSubject');
  var teaPhone = document.getElementById('teaPhone');

  var editingId = null;

  function showFormError(message) {
    formError.textContent = message;
    formError.style.display = 'block';
  }

  function hideFormError() {
    formError.style.display = 'none';
  }

  async function load() {
    var url = '/teacher/page?page=' + state.page +
      '&page_size=' + state.size +
      '&keyword=' + encodeURIComponent(state.keyword);
    var data = await App.request(url);
    state.rows = (data && data.rows) || [];
    state.total = (data && data.total) || 0;

    if (!state.rows.length && state.page > 1) {
      state.page -= 1;
      return load();
    }

    render();
  }

  function render() {
    if (!state.rows.length) {
      tableBody.innerHTML = '<tr><td colspan="8" class="empty-row">暂无老师数据</td></tr>';
    } else {
      tableBody.innerHTML = state.rows.map(function (row) {
        return '<tr>' +
          '<td>' + row.id + '</td>' +
          '<td>' + App.escapeHtml(row.name) + '</td>' +
          '<td><span class="badge-soft ' + (App.normalizeGerder(row.gerder) === '女' ? 'orange' : '') + '">' + App.escapeHtml(App.gerderText(row.gerder)) + '</span></td>' +
          '<td>' + App.escapeHtml(row.age) + '</td>' +
          '<td><span class="badge-soft">' + App.escapeHtml(row.subject) + '</span></td>' +
          '<td>' + App.escapeHtml(row.phone) + '</td>' +
          '<td>' + App.formatDateTime(row.create_time) + '</td>' +
          '<td>' +
          '<button type="button" class="btn btn-link btn-sm p-0 me-2" data-action="edit" data-id="' + row.id + '"><i class="bi bi-pencil-square"></i> 编辑</button>' +
          '<button type="button" class="btn btn-link btn-sm p-0 text-danger" data-action="delete" data-id="' + row.id + '"><i class="bi bi-trash"></i> 删除</button>' +
          '</td>' +
          '</tr>';
      }).join('');
    }

    App.renderPagination(paginationEl, { page: state.page, size: state.size, total: state.total }, function (page) {
      state.page = page;
      load().catch(function (error) { App.toast(error.message, 'error'); });
    });
  }

  function openAdd() {
    editingId = null;
    document.getElementById('teacherForm').reset();
    teaId.value = '';
    teaAge.value = 30;
    modalTitle.textContent = '新增老师';
    hideFormError();
    modal.show();
  }

  function openEdit(id) {
    var row = null;
    for (var i = 0; i < state.rows.length; i++) {
      if (Number(state.rows[i].id) === Number(id)) { row = state.rows[i]; break; }
    }
    if (!row) return;

    editingId = row.id;
    teaId.value = row.id;
    teaName.value = row.name || '';
    var gerder = App.normalizeGerder(row.gerder);
    App.ensureOption(teaGerder, gerder);
    teaGerder.value = gerder;
    teaAge.value = row.age === null || row.age === undefined ? '' : row.age;
    App.ensureOption(teaSubject, row.subject);
    teaSubject.value = row.subject || '';
    teaPhone.value = row.phone || '';
    modalTitle.textContent = '编辑老师';
    hideFormError();
    modal.show();
  }

  function buildPayload() {
    return {
      name: teaName.value.trim(),
      gerder: teaGerder.value,
      age: teaAge.value === '' ? 30 : Number(teaAge.value),
      subject: teaSubject.value,
      phone: teaPhone.value.trim()
    };
  }

  function validate(payload) {
    if (!payload.name) return '请输入老师姓名';
    if (!payload.gerder) return '请选择性别';
    if (!payload.subject) return '请选择学科';
    if (isNaN(payload.age) || payload.age < 0 || payload.age > 150) return '年龄需在 0 ~ 150 之间';
    if (!/^\d{9,11}$/.test(payload.phone)) return '联系电话需为 9 ~ 11 位数字';
    return '';
  }

  async function save() {
    var payload = buildPayload();
    var message = validate(payload);
    if (message) {
      showFormError(message);
      return;
    }

    saveBtn.disabled = true;
    try {
      if (editingId) {
        await App.request('/teacher/update', {
          method: 'PUT',
          body: Object.assign({ id: editingId }, payload)
        });
        App.toast('老师信息已更新');
      } else {
        await App.request('/teacher/add', { method: 'POST', body: payload });
        App.toast('老师新增成功');
        state.page = 1;
      }
      modal.hide();
      await load();
    } catch (error) {
      showFormError(error.message);
    } finally {
      saveBtn.disabled = false;
    }
  }

  async function remove(id) {
    var row = null;
    for (var i = 0; i < state.rows.length; i++) {
      if (Number(state.rows[i].id) === Number(id)) { row = state.rows[i]; break; }
    }
    if (!row) return;

    var ok = await App.confirm('确定删除老师「' + row.name + '」吗？删除后不可恢复。');
    if (!ok) return;

    try {
      await App.request('/teacher/delete?tea_id=' + id, { method: 'DELETE' });
      App.toast('删除成功');
      await load();
    } catch (error) {
      App.toast(error.message, 'error');
    }
  }

  document.getElementById('addBtn').addEventListener('click', openAdd);
  saveBtn.addEventListener('click', save);

  document.getElementById('searchForm').addEventListener('submit', function (event) {
    event.preventDefault();
    state.keyword = keywordInput.value.trim();
    state.page = 1;
    load().catch(function (error) { App.toast(error.message, 'error'); });
  });

  document.getElementById('resetBtn').addEventListener('click', function () {
    keywordInput.value = '';
    state.keyword = '';
    state.page = 1;
    load().catch(function (error) { App.toast(error.message, 'error'); });
  });

  pageSizeSelect.addEventListener('change', function () {
    state.size = Number(pageSizeSelect.value) || 10;
    state.page = 1;
    load().catch(function (error) { App.toast(error.message, 'error'); });
  });

  tableBody.addEventListener('click', function (event) {
    var button = event.target.closest('button[data-action]');
    if (!button) return;
    var id = Number(button.dataset.id);
    if (button.dataset.action === 'edit') openEdit(id);
    if (button.dataset.action === 'delete') remove(id);
  });

  load().catch(function (error) {
    App.toast(error.message, 'error');
    tableBody.innerHTML = '<tr><td colspan="8" class="empty-row">数据加载失败</td></tr>';
  });
})();

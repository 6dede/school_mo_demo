(function () {
  'use strict';

  App.checkLogin();
  if (window.parent && window.parent.setBreadcrumb) {
    window.parent.setBreadcrumb('班级管理', '/static/html/classroom/list.html');
  }

  var state = { page: 1, size: 10, keyword: '', total: 0, rows: [] };

  var tableBody = document.getElementById('tableBody');
  var paginationEl = document.getElementById('pagination');
  var keywordInput = document.getElementById('keyword');
  var pageSizeSelect = document.getElementById('pageSize');

  var modalEl = document.getElementById('classModal');
  var modal = new bootstrap.Modal(modalEl);
  var modalTitle = document.getElementById('classModalTitle');
  var formError = document.getElementById('classFormError');
  var saveBtn = document.getElementById('saveBtn');

  var clsId = document.getElementById('clsId');
  var clsName = document.getElementById('clsName');
  var clsAddress = document.getElementById('clsAddress');

  var editingId = null;

  function showFormError(message) {
    formError.textContent = message;
    formError.style.display = 'block';
  }

  function hideFormError() {
    formError.style.display = 'none';
  }

  async function load() {
    var url = '/classroom/page?page=' + state.page +
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
      tableBody.innerHTML = '<tr><td colspan="5" class="empty-row">暂无班级数据</td></tr>';
    } else {
      tableBody.innerHTML = state.rows.map(function (row) {
        return '<tr>' +
          '<td>' + row.id + '</td>' +
          '<td>' + App.escapeHtml(row.name) + '</td>' +
          '<td>' + App.escapeHtml(row.address) + '</td>' +
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
    document.getElementById('classForm').reset();
    clsId.value = '';
    modalTitle.textContent = '新增班级';
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
    clsId.value = row.id;
    clsName.value = row.name || '';
    clsAddress.value = row.address || '';
    modalTitle.textContent = '编辑班级';
    hideFormError();
    modal.show();
  }

  async function save() {
    var payload = {
      name: clsName.value.trim(),
      address: clsAddress.value.trim()
    };

    if (!payload.name) {
      showFormError('请输入班级名称');
      return;
    }
    if (!payload.address) {
      showFormError('请输入班级地址');
      return;
    }

    saveBtn.disabled = true;
    try {
      if (editingId) {
        await App.request('/classroom/update', {
          method: 'PUT',
          body: Object.assign({ id: editingId }, payload)
        });
        App.toast('班级信息已更新');
      } else {
        await App.request('/classroom/add', { method: 'POST', body: payload });
        App.toast('班级新增成功');
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

    var ok = await App.confirm('确定删除班级「' + row.name + '」吗？删除后不可恢复。');
    if (!ok) return;

    try {
      await App.request('/classroom/delete?class_id=' + id, { method: 'DELETE' });
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

  (async function init() {
    try {
      await load();
    } catch (error) {
      App.toast(error.message, 'error');
      tableBody.innerHTML = '<tr><td colspan="5" class="empty-row">数据加载失败</td></tr>';
    }
  })();
})();

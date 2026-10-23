(function () {
  'use strict';

  App.checkLogin();
  if (window.parent && window.parent.setBreadcrumb) {
    window.parent.setBreadcrumb('公告管理', '/static/html/notice/list.html');
  }

  var state = { page: 1, size: 10, keyword: '', total: 0, rows: [] };

  var tableBody = document.getElementById('tableBody');
  var paginationEl = document.getElementById('pagination');
  var keywordInput = document.getElementById('keyword');
  var pageSizeSelect = document.getElementById('pageSize');

  var modal = new bootstrap.Modal(document.getElementById('noticeModal'));
  var modalTitle = document.getElementById('noticeModalTitle');
  var formError = document.getElementById('noticeFormError');
  var saveBtn = document.getElementById('saveBtn');

  var noticeId = document.getElementById('noticeId');
  var noticeTitle = document.getElementById('noticeTitle');
  var noticeContent = document.getElementById('noticeContent');
  var publisher = document.getElementById('publisher');

  var editingId = null;

  function showFormError(message) { formError.textContent = message; formError.style.display = 'block'; }
  function hideFormError() { formError.style.display = 'none'; }

  async function load() {
    var url = '/notice/page?page=' + state.page + '&page_size=' + state.size +
      '&keyword=' + encodeURIComponent(state.keyword);
    var data = await App.request(url);
    state.rows = (data && data.rows) || [];
    state.total = (data && data.total) || 0;
    if (!state.rows.length && state.page > 1) { state.page -= 1; return load(); }
    render();
  }

  function render() {
    if (!state.rows.length) {
      tableBody.innerHTML = '<tr><td colspan="6" class="empty-row">暂无公告</td></tr>';
    } else {
      tableBody.innerHTML = state.rows.map(function (row) {
        return '<tr>' +
          '<td>' + row.id + '</td>' +
          '<td>' + App.escapeHtml(row.title) + '</td>' +
          '<td><span class="text-truncate d-inline-block align-middle" style="max-width: 320px;">' + App.escapeHtml(row.content) + '</span></td>' +
          '<td>' + App.escapeHtml(row.publisher) + '</td>' +
          '<td>' + App.formatDateTime(row.publish_time) + '</td>' +
          '<td>' +
          '<button type="button" class="btn btn-link btn-sm p-0 me-2" data-action="edit" data-id="' + row.id + '"><i class="bi bi-pencil-square"></i> 编辑</button>' +
          '<button type="button" class="btn btn-link btn-sm p-0 text-danger" data-action="delete" data-id="' + row.id + '"><i class="bi bi-trash"></i> 删除</button>' +
          '</td></tr>';
      }).join('');
    }
    App.renderPagination(paginationEl, { page: state.page, size: state.size, total: state.total }, function (page) {
      state.page = page;
      load().catch(function (error) { App.toast(error.message, 'error'); });
    });
  }

  function openAdd() {
    editingId = null;
    document.getElementById('noticeForm').reset();
    noticeId.value = '';
    publisher.value = '管理员';
    modalTitle.textContent = '发布公告';
    hideFormError();
    modal.show();
  }

  function openEdit(id) {
    var row = state.rows.find(function (item) { return Number(item.id) === Number(id); });
    if (!row) return;
    editingId = row.id;
    noticeId.value = row.id;
    noticeTitle.value = row.title || '';
    noticeContent.value = row.content || '';
    publisher.value = row.publisher || '';
    modalTitle.textContent = '编辑公告';
    hideFormError();
    modal.show();
  }

  async function save() {
    var payload = {
      title: noticeTitle.value.trim(),
      content: noticeContent.value.trim(),
      publisher: publisher.value.trim() || '管理员'
    };
    if (!payload.title) { showFormError('请输入公告标题'); return; }
    if (!payload.content) { showFormError('请输入公告内容'); return; }

    saveBtn.disabled = true;
    try {
      if (editingId) {
        await App.request('/notice/update', { method: 'PUT', body: Object.assign({ id: editingId }, payload) });
        App.toast('公告已更新');
      } else {
        await App.request('/notice/add', { method: 'POST', body: payload });
        App.toast('公告发布成功');
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
    var row = state.rows.find(function (item) { return Number(item.id) === Number(id); });
    if (!row) return;
    if (!(await App.confirm('确定删除公告「' + row.title + '」吗？'))) return;
    try {
      await App.request('/notice/delete?notice_id=' + id, { method: 'DELETE' });
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
    if (button.dataset.action === 'edit') openEdit(Number(button.dataset.id));
    if (button.dataset.action === 'delete') remove(Number(button.dataset.id));
  });

  (async function init() {
    try {
      await load();
    } catch (error) {
      App.toast(error.message, 'error');
      tableBody.innerHTML = '<tr><td colspan="6" class="empty-row">数据加载失败</td></tr>';
    }
  })();
})();

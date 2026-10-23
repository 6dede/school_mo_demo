(function () {
  'use strict';

  App.checkLogin();
  if (window.parent && window.parent.setBreadcrumb) {
    window.parent.setBreadcrumb('学科管理', '/static/html/subject/list.html');
  }

  var state = { page: 1, size: 10, keyword: '', total: 0, rows: [], teachers: [] };

  var tableBody = document.getElementById('tableBody');
  var paginationEl = document.getElementById('pagination');
  var keywordInput = document.getElementById('keyword');
  var pageSizeSelect = document.getElementById('pageSize');

  var modalEl = document.getElementById('subjectModal');
  var modal = new bootstrap.Modal(modalEl);
  var modalTitle = document.getElementById('subjectModalTitle');
  var formError = document.getElementById('subjectFormError');
  var saveBtn = document.getElementById('saveBtn');

  var subId = document.getElementById('subId');
  var subName = document.getElementById('subName');

  var editingId = null;

  function showFormError(message) {
    formError.textContent = message;
    formError.style.display = 'block';
  }

  function hideFormError() {
    formError.style.display = 'none';
  }

  async function loadTeachers() {
    state.teachers = (await App.request('/teacher/all')) || [];
  }

  function teacherCount(subject) {
    return state.teachers.filter(function (teacher) {
      return teacher.subject === subject;
    }).length;
  }

  async function load() {
    var url = '/subject/page?page=' + state.page +
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
      tableBody.innerHTML = '<tr><td colspan="4" class="empty-row">暂无学科数据</td></tr>';
    } else {
      tableBody.innerHTML = state.rows.map(function (row) {
        var count = teacherCount(row.subject);
        return '<tr>' +
          '<td>' + row.id + '</td>' +
          '<td>' + App.escapeHtml(row.subject) + '</td>' +
          '<td><span class="badge-soft ' + (count ? 'green' : 'gray') + '">' + count + ' 人</span></td>' +
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
    document.getElementById('subjectForm').reset();
    subId.value = '';
    modalTitle.textContent = '新增学科';
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
    subId.value = row.id;
    subName.value = row.subject || '';
    modalTitle.textContent = '编辑学科';
    hideFormError();
    modal.show();
  }

  async function save() {
    var name = subName.value.trim();
    if (!name) {
      showFormError('请输入学科名称');
      return;
    }

    saveBtn.disabled = true;
    try {
      if (editingId) {
        await App.request('/subject/update', {
          method: 'PUT',
          body: { id: editingId, subject: name }
        });
        App.toast('学科信息已更新');
      } else {
        await App.request('/subject/add', { method: 'POST', body: { subject: name } });
        App.toast('学科新增成功');
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

    var ok = await App.confirm('确定删除学科「' + row.subject + '」吗？删除后不可恢复。');
    if (!ok) return;

    try {
      await App.request('/subject/delete?sub_id=' + id, { method: 'DELETE' });
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
      await loadTeachers();
    } catch (error) {
      App.toast('老师数据加载失败：' + error.message, 'error');
    }
    try {
      await load();
    } catch (error) {
      App.toast(error.message, 'error');
      tableBody.innerHTML = '<tr><td colspan="4" class="empty-row">数据加载失败</td></tr>';
    }
  })();
})();

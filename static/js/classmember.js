(function () {
  'use strict';

  App.checkLogin();
  if (window.parent && window.parent.setBreadcrumb) {
    window.parent.setBreadcrumb('分班管理', '/static/html/classmember/list.html');
  }

  var state = { page: 1, size: 10, keyword: '', classId: '', total: 0, rows: [], students: [], classes: [] };

  var tableBody = document.getElementById('tableBody');
  var paginationEl = document.getElementById('pagination');
  var keywordInput = document.getElementById('keyword');
  var classFilter = document.getElementById('classFilter');
  var pageSizeSelect = document.getElementById('pageSize');

  var modal = new bootstrap.Modal(document.getElementById('memberModal'));
  var modalTitle = document.getElementById('memberModalTitle');
  var formError = document.getElementById('memberFormError');
  var saveBtn = document.getElementById('saveBtn');

  var memberId = document.getElementById('memberId');
  var studentSelect = document.getElementById('studentSelect');
  var classSelect = document.getElementById('classSelect');
  var joinDate = document.getElementById('joinDate');

  var editingId = null;

  function showFormError(message) { formError.textContent = message; formError.style.display = 'block'; }
  function hideFormError() { formError.style.display = 'none'; }

  async function loadRefs() {
    var results = await Promise.all([App.request('/student/all'), App.request('/classroom/all')]);
    state.students = results[0] || [];
    state.classes = results[1] || [];
    App.fillSelect(classFilter, state.classes, '全部班级');
    App.fillSelect(studentSelect, state.students, '请选择学生');
    App.fillSelect(classSelect, state.classes, '请选择班级');
  }

  async function load() {
    var url = '/classmember/page?page=' + state.page + '&page_size=' + state.size +
      '&keyword=' + encodeURIComponent(state.keyword) +
      (state.classId ? '&class_id=' + state.classId : '');
    var data = await App.request(url);
    state.rows = (data && data.rows) || [];
    state.total = (data && data.total) || 0;
    if (!state.rows.length && state.page > 1) { state.page -= 1; return load(); }
    render();
  }

  function render() {
    if (!state.rows.length) {
      tableBody.innerHTML = '<tr><td colspan="7" class="empty-row">暂无分班数据</td></tr>';
    } else {
      tableBody.innerHTML = state.rows.map(function (row) {
        return '<tr>' +
          '<td>' + row.id + '</td>' +
          '<td>' + App.escapeHtml(row.student_name || '-') + '</td>' +
          '<td>' + App.escapeHtml(App.gerderText(row.gerder)) + '</td>' +
          '<td>' + App.escapeHtml(row.age) + '</td>' +
          '<td><span class="badge-soft">' + App.escapeHtml(row.class_name || '-') + '</span></td>' +
          '<td>' + App.formatDateTime(row.join_date) + '</td>' +
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
    document.getElementById('memberForm').reset();
    memberId.value = '';
    joinDate.value = App.today();
    modalTitle.textContent = '新增分班';
    hideFormError();
    modal.show();
  }

  function openEdit(id) {
    var row = state.rows.find(function (item) { return Number(item.id) === Number(id); });
    if (!row) return;
    editingId = row.id;
    memberId.value = row.id;
    studentSelect.value = row.student_id;
    classSelect.value = row.class_id;
    joinDate.value = App.toDate(row.join_date);
    modalTitle.textContent = '编辑分班';
    hideFormError();
    modal.show();
  }

  async function save() {
    var payload = {
      student_id: Number(studentSelect.value),
      class_id: Number(classSelect.value),
      join_date: joinDate.value
    };
    if (!payload.student_id) { showFormError('请选择学生'); return; }
    if (!payload.class_id) { showFormError('请选择班级'); return; }
    if (!payload.join_date) { showFormError('请选择分班日期'); return; }

    saveBtn.disabled = true;
    try {
      if (editingId) {
        await App.request('/classmember/update', { method: 'PUT', body: Object.assign({ id: editingId }, payload) });
        App.toast('分班信息已更新');
      } else {
        await App.request('/classmember/add', { method: 'POST', body: payload });
        App.toast('分班成功');
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
    if (!(await App.confirm('确定删除「' + (row.student_name || '') + '」的分班记录吗？'))) return;
    try {
      await App.request('/classmember/delete?member_id=' + id, { method: 'DELETE' });
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
    state.classId = classFilter.value;
    state.page = 1;
    load().catch(function (error) { App.toast(error.message, 'error'); });
  });
  document.getElementById('resetBtn').addEventListener('click', function () {
    keywordInput.value = '';
    classFilter.value = '';
    state.keyword = '';
    state.classId = '';
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
      await loadRefs();
    } catch (error) {
      App.toast('基础数据加载失败：' + error.message, 'error');
    }
    try {
      await load();
    } catch (error) {
      App.toast(error.message, 'error');
      tableBody.innerHTML = '<tr><td colspan="7" class="empty-row">数据加载失败</td></tr>';
    }
  })();
})();

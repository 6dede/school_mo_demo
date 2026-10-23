(function () {
  'use strict';

  App.checkLogin();
  if (window.parent && window.parent.setBreadcrumb) {
    window.parent.setBreadcrumb('奖惩管理', '/static/html/award/list.html');
  }

  var state = { page: 1, size: 10, keyword: '', type: '', total: 0, rows: [], students: [] };

  var tableBody = document.getElementById('tableBody');
  var paginationEl = document.getElementById('pagination');
  var keywordInput = document.getElementById('keyword');
  var typeFilter = document.getElementById('typeFilter');
  var pageSizeSelect = document.getElementById('pageSize');

  var modal = new bootstrap.Modal(document.getElementById('awardModal'));
  var modalTitle = document.getElementById('awardModalTitle');
  var formError = document.getElementById('awardFormError');
  var saveBtn = document.getElementById('saveBtn');

  var awardId = document.getElementById('awardId');
  var studentSelect = document.getElementById('studentSelect');
  var typeSelect = document.getElementById('typeSelect');
  var awardTitle = document.getElementById('awardTitle');
  var awardReason = document.getElementById('awardReason');
  var recordDate = document.getElementById('recordDate');

  var editingId = null;

  function showFormError(message) { formError.textContent = message; formError.style.display = 'block'; }
  function hideFormError() { formError.style.display = 'none'; }

  async function loadRefs() {
    state.students = (await App.request('/student/all')) || [];
    App.fillSelect(studentSelect, state.students, '请选择学生');
  }

  async function load() {
    var url = '/award/page?page=' + state.page + '&page_size=' + state.size +
      '&keyword=' + encodeURIComponent(state.keyword) +
      '&type=' + encodeURIComponent(state.type);
    var data = await App.request(url);
    state.rows = (data && data.rows) || [];
    state.total = (data && data.total) || 0;
    if (!state.rows.length && state.page > 1) { state.page -= 1; return load(); }
    render();
  }

  function render() {
    if (!state.rows.length) {
      tableBody.innerHTML = '<tr><td colspan="8" class="empty-row">暂无奖惩记录</td></tr>';
    } else {
      tableBody.innerHTML = state.rows.map(function (row) {
        return '<tr>' +
          '<td>' + row.id + '</td>' +
          '<td>' + App.escapeHtml(row.student_name || '-') + '</td>' +
          '<td>' + App.escapeHtml(row.class_name || '-') + '</td>' +
          '<td><span class="badge-soft ' + (row.type === '奖励' ? 'green' : 'red') + '">' + App.escapeHtml(row.type) + '</span></td>' +
          '<td>' + App.escapeHtml(row.title) + '</td>' +
          '<td>' + App.escapeHtml(row.reason || '-') + '</td>' +
          '<td>' + App.formatDateTime(row.record_date) + '</td>' +
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
    document.getElementById('awardForm').reset();
    awardId.value = '';
    typeSelect.value = '奖励';
    recordDate.value = App.today();
    modalTitle.textContent = '新增奖惩';
    hideFormError();
    modal.show();
  }

  function openEdit(id) {
    var row = state.rows.find(function (item) { return Number(item.id) === Number(id); });
    if (!row) return;
    editingId = row.id;
    awardId.value = row.id;
    studentSelect.value = row.student_id;
    typeSelect.value = row.type;
    awardTitle.value = row.title || '';
    awardReason.value = row.reason || '';
    recordDate.value = App.toDate(row.record_date);
    modalTitle.textContent = '编辑奖惩';
    hideFormError();
    modal.show();
  }

  async function save() {
    var payload = {
      student_id: Number(studentSelect.value),
      type: typeSelect.value,
      title: awardTitle.value.trim(),
      reason: awardReason.value.trim(),
      record_date: recordDate.value
    };
    if (!payload.student_id) { showFormError('请选择学生'); return; }
    if (!payload.title) { showFormError('请输入奖惩标题'); return; }
    if (!payload.record_date) { showFormError('请选择记录日期'); return; }

    saveBtn.disabled = true;
    try {
      if (editingId) {
        await App.request('/award/update', { method: 'PUT', body: Object.assign({ id: editingId }, payload) });
        App.toast('奖惩记录已更新');
      } else {
        await App.request('/award/add', { method: 'POST', body: payload });
        App.toast('奖惩新增成功');
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
    if (!(await App.confirm('确定删除「' + row.title + '」吗？'))) return;
    try {
      await App.request('/award/delete?award_id=' + id, { method: 'DELETE' });
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
    state.type = typeFilter.value;
    state.page = 1;
    load().catch(function (error) { App.toast(error.message, 'error'); });
  });
  document.getElementById('resetBtn').addEventListener('click', function () {
    keywordInput.value = '';
    typeFilter.value = '';
    state.keyword = '';
    state.type = '';
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
      App.toast('学生数据加载失败：' + error.message, 'error');
    }
    try {
      await load();
    } catch (error) {
      App.toast(error.message, 'error');
      tableBody.innerHTML = '<tr><td colspan="8" class="empty-row">数据加载失败</td></tr>';
    }
  })();
})();

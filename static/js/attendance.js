(function () {
  'use strict';

  App.checkLogin();
  if (window.parent && window.parent.setBreadcrumb) {
    window.parent.setBreadcrumb('考勤管理', '/static/html/attendance/list.html');
  }

  var state = { page: 1, size: 10, keyword: '', status: '', courseId: '', total: 0, rows: [], students: [], courses: [] };
  var TONE = { '正常': 'green', '迟到': 'orange', '缺勤': 'red', '请假': 'gray' };

  var tableBody = document.getElementById('tableBody');
  var paginationEl = document.getElementById('pagination');
  var keywordInput = document.getElementById('keyword');
  var statusFilter = document.getElementById('statusFilter');
  var courseFilter = document.getElementById('courseFilter');
  var pageSizeSelect = document.getElementById('pageSize');

  var modal = new bootstrap.Modal(document.getElementById('attendanceModal'));
  var modalTitle = document.getElementById('attendanceModalTitle');
  var formError = document.getElementById('attendanceFormError');
  var saveBtn = document.getElementById('saveBtn');

  var attendanceId = document.getElementById('attendanceId');
  var studentSelect = document.getElementById('studentSelect');
  var courseSelect = document.getElementById('courseSelect');
  var statusSelect = document.getElementById('statusSelect');
  var attendanceDate = document.getElementById('attendanceDate');
  var remark = document.getElementById('remark');

  var editingId = null;

  function showFormError(message) { formError.textContent = message; formError.style.display = 'block'; }
  function hideFormError() { formError.style.display = 'none'; }

  function courseLabel(course) {
    return course.name + '（' + (course.class_name || '-') + '）';
  }

  async function loadRefs() {
    var results = await Promise.all([App.request('/student/all'), App.request('/course/all')]);
    state.students = results[0] || [];
    state.courses = results[1] || [];
    App.fillSelect(courseFilter, state.courses, '全部课程', courseLabel);
    App.fillSelect(studentSelect, state.students, '请选择学生');
    App.fillSelect(courseSelect, state.courses, '请选择课程', courseLabel);
  }

  async function load() {
    var url = '/attendance/page?page=' + state.page + '&page_size=' + state.size +
      '&keyword=' + encodeURIComponent(state.keyword) +
      '&status=' + encodeURIComponent(state.status) +
      (state.courseId ? '&course_id=' + state.courseId : '');
    var data = await App.request(url);
    state.rows = (data && data.rows) || [];
    state.total = (data && data.total) || 0;
    if (!state.rows.length && state.page > 1) { state.page -= 1; return load(); }
    render();
  }

  function render() {
    if (!state.rows.length) {
      tableBody.innerHTML = '<tr><td colspan="8" class="empty-row">暂无考勤数据</td></tr>';
    } else {
      tableBody.innerHTML = state.rows.map(function (row) {
        return '<tr>' +
          '<td>' + row.id + '</td>' +
          '<td>' + App.escapeHtml(row.student_name || '-') + '</td>' +
          '<td>' + App.escapeHtml(row.class_name || '-') + '</td>' +
          '<td>' + App.escapeHtml(row.course_name || '-') + '</td>' +
          '<td><span class="badge-soft ' + (TONE[row.status] || 'gray') + '">' + App.escapeHtml(row.status) + '</span></td>' +
          '<td>' + App.formatDateTime(row.attendance_date) + '</td>' +
          '<td>' + App.escapeHtml(row.remark || '-') + '</td>' +
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
    document.getElementById('attendanceForm').reset();
    attendanceId.value = '';
    statusSelect.value = '正常';
    attendanceDate.value = App.today();
    modalTitle.textContent = '新增考勤';
    hideFormError();
    modal.show();
  }

  function openEdit(id) {
    var row = state.rows.find(function (item) { return Number(item.id) === Number(id); });
    if (!row) return;
    editingId = row.id;
    attendanceId.value = row.id;
    studentSelect.value = row.student_id;
    courseSelect.value = row.course_id;
    statusSelect.value = row.status;
    attendanceDate.value = App.toDate(row.attendance_date);
    remark.value = row.remark || '';
    modalTitle.textContent = '编辑考勤';
    hideFormError();
    modal.show();
  }

  async function save() {
    var payload = {
      student_id: Number(studentSelect.value),
      course_id: Number(courseSelect.value),
      status: statusSelect.value,
      attendance_date: attendanceDate.value,
      remark: remark.value.trim()
    };
    if (!payload.student_id) { showFormError('请选择学生'); return; }
    if (!payload.course_id) { showFormError('请选择课程'); return; }
    if (!payload.attendance_date) { showFormError('请选择考勤日期'); return; }

    saveBtn.disabled = true;
    try {
      if (editingId) {
        await App.request('/attendance/update', { method: 'PUT', body: Object.assign({ id: editingId }, payload) });
        App.toast('考勤信息已更新');
      } else {
        await App.request('/attendance/add', { method: 'POST', body: payload });
        App.toast('考勤新增成功');
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
    if (!(await App.confirm('确定删除该条考勤记录吗？'))) return;
    try {
      await App.request('/attendance/delete?attendance_id=' + id, { method: 'DELETE' });
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
    state.status = statusFilter.value;
    state.courseId = courseFilter.value;
    state.page = 1;
    load().catch(function (error) { App.toast(error.message, 'error'); });
  });
  document.getElementById('resetBtn').addEventListener('click', function () {
    keywordInput.value = '';
    statusFilter.value = '';
    courseFilter.value = '';
    state.keyword = '';
    state.status = '';
    state.courseId = '';
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
      tableBody.innerHTML = '<tr><td colspan="8" class="empty-row">数据加载失败</td></tr>';
    }
  })();
})();

(function () {
  'use strict';

  App.checkLogin();
  if (window.parent && window.parent.setBreadcrumb) {
    window.parent.setBreadcrumb('成绩管理', '/static/html/score/list.html');
  }

  var state = { page: 1, size: 10, keyword: '', courseId: '', total: 0, rows: [], students: [], courses: [] };

  var tableBody = document.getElementById('tableBody');
  var paginationEl = document.getElementById('pagination');
  var keywordInput = document.getElementById('keyword');
  var courseFilter = document.getElementById('courseFilter');
  var pageSizeSelect = document.getElementById('pageSize');

  var modal = new bootstrap.Modal(document.getElementById('scoreModal'));
  var modalTitle = document.getElementById('scoreModalTitle');
  var formError = document.getElementById('scoreFormError');
  var saveBtn = document.getElementById('saveBtn');

  var scoreId = document.getElementById('scoreId');
  var studentSelect = document.getElementById('studentSelect');
  var courseSelect = document.getElementById('courseSelect');
  var examName = document.getElementById('examName');
  var scoreValue = document.getElementById('scoreValue');

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
    var url = '/score/page?page=' + state.page + '&page_size=' + state.size +
      '&keyword=' + encodeURIComponent(state.keyword) +
      (state.courseId ? '&course_id=' + state.courseId : '');
    var data = await App.request(url);
    state.rows = (data && data.rows) || [];
    state.total = (data && data.total) || 0;
    if (!state.rows.length && state.page > 1) { state.page -= 1; return load(); }
    render();
  }

  function render() {
    if (!state.rows.length) {
      tableBody.innerHTML = '<tr><td colspan="8" class="empty-row">暂无成绩数据</td></tr>';
    } else {
      tableBody.innerHTML = state.rows.map(function (row) {
        var pass = Number(row.score) >= 60;
        return '<tr>' +
          '<td>' + row.id + '</td>' +
          '<td>' + App.escapeHtml(row.student_name || '-') + '</td>' +
          '<td>' + App.escapeHtml(row.class_name || '-') + '</td>' +
          '<td>' + App.escapeHtml(row.course_name || '-') + '</td>' +
          '<td>' + App.escapeHtml(row.exam_name) + '</td>' +
          '<td><span class="badge-soft ' + (pass ? 'green' : 'red') + '">' + Number(row.score).toFixed(1) + '</span></td>' +
          '<td>' + App.formatDateTime(row.create_time) + '</td>' +
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
    document.getElementById('scoreForm').reset();
    scoreId.value = '';
    modalTitle.textContent = '录入成绩';
    hideFormError();
    modal.show();
  }

  function openEdit(id) {
    var row = state.rows.find(function (item) { return Number(item.id) === Number(id); });
    if (!row) return;
    editingId = row.id;
    scoreId.value = row.id;
    studentSelect.value = row.student_id;
    courseSelect.value = row.course_id;
    examName.value = row.exam_name || '';
    scoreValue.value = row.score;
    modalTitle.textContent = '编辑成绩';
    hideFormError();
    modal.show();
  }

  async function save() {
    var payload = {
      student_id: Number(studentSelect.value),
      course_id: Number(courseSelect.value),
      exam_name: examName.value.trim(),
      score: Number(scoreValue.value)
    };
    if (!payload.student_id) { showFormError('请选择学生'); return; }
    if (!payload.course_id) { showFormError('请选择课程'); return; }
    if (!payload.exam_name) { showFormError('请输入考试名称'); return; }
    if (scoreValue.value === '' || isNaN(payload.score) || payload.score < 0 || payload.score > 100) {
      showFormError('分数需在 0 ~ 100 之间');
      return;
    }

    saveBtn.disabled = true;
    try {
      if (editingId) {
        await App.request('/score/update', { method: 'PUT', body: Object.assign({ id: editingId }, payload) });
        App.toast('成绩已更新');
      } else {
        await App.request('/score/add', { method: 'POST', body: payload });
        App.toast('成绩录入成功');
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
    if (!(await App.confirm('确定删除「' + (row.student_name || '') + ' - ' + row.exam_name + '」的成绩吗？'))) return;
    try {
      await App.request('/score/delete?score_id=' + id, { method: 'DELETE' });
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
    state.courseId = courseFilter.value;
    state.page = 1;
    load().catch(function (error) { App.toast(error.message, 'error'); });
  });
  document.getElementById('resetBtn').addEventListener('click', function () {
    keywordInput.value = '';
    courseFilter.value = '';
    state.keyword = '';
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

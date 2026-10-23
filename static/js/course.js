(function () {
  'use strict';

  App.checkLogin();
  if (window.parent && window.parent.setBreadcrumb) {
    window.parent.setBreadcrumb('课程管理', '/static/html/course/list.html');
  }

  var state = { page: 1, size: 10, keyword: '', classId: '', total: 0, rows: [], refs: { subjects: [], teachers: [], classes: [] } };

  var tableBody = document.getElementById('tableBody');
  var paginationEl = document.getElementById('pagination');
  var keywordInput = document.getElementById('keyword');
  var classFilter = document.getElementById('classFilter');
  var pageSizeSelect = document.getElementById('pageSize');

  var modal = new bootstrap.Modal(document.getElementById('courseModal'));
  var modalTitle = document.getElementById('courseModalTitle');
  var formError = document.getElementById('courseFormError');
  var saveBtn = document.getElementById('saveBtn');

  var courseId = document.getElementById('courseId');
  var courseName = document.getElementById('courseName');
  var subjectSelect = document.getElementById('subjectSelect');
  var teacherSelect = document.getElementById('teacherSelect');
  var classSelect = document.getElementById('classSelect');
  var daySelect = document.getElementById('daySelect');
  var startTime = document.getElementById('startTime');
  var endTime = document.getElementById('endTime');

  var editingId = null;

  function showFormError(message) {
    formError.textContent = message;
    formError.style.display = 'block';
  }

  function hideFormError() {
    formError.style.display = 'none';
  }

  async function loadRefs() {
    var results = await Promise.all([
      App.request('/subject/all'),
      App.request('/teacher/all'),
      App.request('/classroom/all')
    ]);
    state.refs.subjects = results[0] || [];
    state.refs.teachers = results[1] || [];
    state.refs.classes = results[2] || [];
    App.fillSelect(classFilter, state.refs.classes, '全部班级');
    App.fillSelect(subjectSelect, state.refs.subjects, '请选择学科', function (s) { return s.subject; });
    App.fillSelect(teacherSelect, state.refs.teachers, '请选择老师', function (t) { return t.name + '（' + (t.subject || '-') + '）'; });
    App.fillSelect(classSelect, state.refs.classes, '请选择班级');
  }

  async function load() {
    var url = '/course/page?page=' + state.page + '&page_size=' + state.size +
      '&keyword=' + encodeURIComponent(state.keyword) +
      (state.classId ? '&class_id=' + state.classId : '');
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
      tableBody.innerHTML = '<tr><td colspan="7" class="empty-row">暂无课程数据</td></tr>';
    } else {
      tableBody.innerHTML = state.rows.map(function (row) {
        return '<tr>' +
          '<td>' + row.id + '</td>' +
          '<td>' + App.escapeHtml(row.name) + '</td>' +
          '<td><span class="badge-soft">' + App.escapeHtml(row.subject_name || '-') + '</span></td>' +
          '<td>' + App.escapeHtml(row.teacher_name || '-') + '</td>' +
          '<td>' + App.escapeHtml(row.class_name || '-') + '</td>' +
          '<td>' + App.escapeHtml(row.schedule_day + ' ' + row.start_time + '-' + row.end_time) + '</td>' +
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
    document.getElementById('courseForm').reset();
    courseId.value = '';
    daySelect.value = '周一';
    startTime.value = '08:00';
    endTime.value = '09:40';
    modalTitle.textContent = '新增课程';
    hideFormError();
    modal.show();
  }

  function openEdit(id) {
    var row = state.rows.find(function (item) { return Number(item.id) === Number(id); });
    if (!row) return;
    editingId = row.id;
    courseId.value = row.id;
    courseName.value = row.name || '';
    subjectSelect.value = row.subject_id;
    teacherSelect.value = row.teacher_id;
    classSelect.value = row.class_id;
    daySelect.value = row.schedule_day || '周一';
    startTime.value = row.start_time || '';
    endTime.value = row.end_time || '';
    modalTitle.textContent = '编辑课程';
    hideFormError();
    modal.show();
  }

  function buildPayload() {
    return {
      name: courseName.value.trim(),
      subject_id: Number(subjectSelect.value),
      teacher_id: Number(teacherSelect.value),
      class_id: Number(classSelect.value),
      schedule_day: daySelect.value,
      start_time: startTime.value,
      end_time: endTime.value
    };
  }

  function validate(p) {
    if (!p.name) return '请输入课程名称';
    if (!p.subject_id) return '请选择学科';
    if (!p.teacher_id) return '请选择任课老师';
    if (!p.class_id) return '请选择班级';
    if (!p.start_time || !p.end_time) return '请选择上课时间';
    if (p.end_time <= p.start_time) return '结束时间需晚于开始时间';
    return '';
  }

  async function save() {
    var payload = buildPayload();
    var message = validate(payload);
    if (message) { showFormError(message); return; }

    saveBtn.disabled = true;
    try {
      if (editingId) {
        await App.request('/course/update', { method: 'PUT', body: Object.assign({ id: editingId }, payload) });
        App.toast('课程信息已更新');
      } else {
        await App.request('/course/add', { method: 'POST', body: payload });
        App.toast('课程新增成功');
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
    if (!(await App.confirm('确定删除课程「' + row.name + '」吗？'))) return;
    try {
      await App.request('/course/delete?course_id=' + id, { method: 'DELETE' });
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

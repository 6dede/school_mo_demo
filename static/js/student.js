(function () {
  'use strict';

  App.checkLogin();
  if (window.parent && window.parent.setBreadcrumb) {
    window.parent.setBreadcrumb('学生管理', '/static/html/student/list.html');
  }

  var state = { page: 1, size: 10, keyword: '', total: 0, rows: [], teachers: [] };

  var tableBody = document.getElementById('tableBody');
  var paginationEl = document.getElementById('pagination');
  var keywordInput = document.getElementById('keyword');
  var pageSizeSelect = document.getElementById('pageSize');

  var modalEl = document.getElementById('studentModal');
  var modal = new bootstrap.Modal(modalEl);
  var modalTitle = document.getElementById('studentModalTitle');
  var formError = document.getElementById('studentFormError');
  var saveBtn = document.getElementById('saveBtn');

  var stuId = document.getElementById('stuId');
  var stuName = document.getElementById('stuName');
  var stuGerder = document.getElementById('stuGerder');
  var stuAge = document.getElementById('stuAge');
  var stuTeacher = document.getElementById('stuTeacher');
  var stuGrade = document.getElementById('stuGrade');
  var stuEnroll = document.getElementById('stuEnroll');

  var editingId = null;

  /* ---------- 工具 ---------- */
  function nowLocal() {
    var d = new Date();
    d.setMinutes(d.getMinutes() - d.getTimezoneOffset());
    return d.toISOString().slice(0, 16);
  }

  function teacherName(id) {
    for (var i = 0; i < state.teachers.length; i++) {
      if (Number(state.teachers[i].id) === Number(id)) return state.teachers[i].name;
    }
    return '-';
  }

  function showFormError(message) {
    formError.textContent = message;
    formError.style.display = 'block';
  }

  function hideFormError() {
    formError.style.display = 'none';
  }

  /* ---------- 数据加载 ---------- */
  async function loadTeachers() {
    state.teachers = (await App.request('/teacher/all')) || [];
    stuTeacher.innerHTML = '<option value="">请选择</option>' + state.teachers.map(function (teacher) {
      return '<option value="' + teacher.id + '">' +
        App.escapeHtml(teacher.name) + '（' + App.escapeHtml(teacher.subject) + '）' +
        '</option>';
    }).join('');
  }

  async function load() {
    var url = '/student/page?page=' + state.page +
      '&page_size=' + state.size +
      '&keyword=' + encodeURIComponent(state.keyword);
    var data = await App.request(url);
    state.rows = (data && data.rows) || [];
    state.total = (data && data.total) || 0;

    // 删除后当前页可能为空，自动回到上一页
    if (!state.rows.length && state.page > 1) {
      state.page -= 1;
      return load();
    }

    render();
  }

  function render() {
    if (!state.rows.length) {
      tableBody.innerHTML = '<tr><td colspan="8" class="empty-row">暂无学生数据</td></tr>';
    } else {
      tableBody.innerHTML = state.rows.map(function (row) {
        return '<tr>' +
          '<td>' + row.id + '</td>' +
          '<td>' + App.escapeHtml(row.name) + '</td>' +
          '<td><span class="badge-soft ' + (App.normalizeGerder(row.gerder) === '女' ? 'orange' : '') + '">' + App.escapeHtml(App.gerderText(row.gerder)) + '</span></td>' +
          '<td>' + App.escapeHtml(row.age) + '</td>' +
          '<td>' + App.escapeHtml(teacherName(row.teacher_id)) + '</td>' +
          '<td>' + App.escapeHtml(row.grade) + '</td>' +
          '<td>' + App.formatDateTime(row.enrollment_date) + '</td>' +
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

  /* ---------- 弹窗 ---------- */
  function openAdd() {
    editingId = null;
    document.getElementById('studentForm').reset();
    stuId.value = '';
    stuAge.value = 18;
    stuEnroll.value = nowLocal();
    modalTitle.textContent = '新增学生';
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
    stuId.value = row.id;
    stuName.value = row.name || '';
    var gerder = App.normalizeGerder(row.gerder);
    App.ensureOption(stuGerder, gerder);
    stuGerder.value = gerder;
    stuAge.value = row.age === null || row.age === undefined ? '' : row.age;
    stuTeacher.value = row.teacher_id === null || row.teacher_id === undefined ? '' : row.teacher_id;
    App.ensureOption(stuGrade, row.grade);
    stuGrade.value = row.grade || '';
    stuEnroll.value = App.toDateTimeLocal(row.enrollment_date);
    modalTitle.textContent = '编辑学生';
    hideFormError();
    modal.show();
  }

  function buildPayload() {
    return {
      name: stuName.value.trim(),
      gerder: stuGerder.value,
      age: stuAge.value === '' ? 18 : Number(stuAge.value),
      teacher_id: Number(stuTeacher.value),
      grade: stuGrade.value,
      enrollment_date: stuEnroll.value.replace('T', ' ')
    };
  }

  function validate(payload) {
    if (!payload.name) return '请输入学生姓名';
    if (!payload.gerder) return '请选择性别';
    if (!payload.teacher_id) return '请选择任课老师';
    if (!payload.grade) return '请选择年级';
    if (!payload.enrollment_date) return '请选择入学日期';
    if (isNaN(payload.age) || payload.age < 0 || payload.age > 150) return '年龄需在 0 ~ 150 之间';
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
        await App.request('/student/update', {
          method: 'PUT',
          body: Object.assign({ id: editingId }, payload)
        });
        App.toast('学生信息已更新');
      } else {
        await App.request('/student/add', { method: 'POST', body: payload });
        App.toast('学生新增成功');
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

    var ok = await App.confirm('确定删除学生「' + row.name + '」吗？删除后不可恢复。');
    if (!ok) return;

    try {
      await App.request('/student/delete?stu_id=' + id, { method: 'DELETE' });
      App.toast('删除成功');
      await load();
    } catch (error) {
      App.toast(error.message, 'error');
    }
  }

  /* ---------- 事件 ---------- */
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

  /* ---------- 初始化 ---------- */
  (async function init() {
    try {
      await loadTeachers();
    } catch (error) {
      App.toast('老师列表加载失败：' + error.message, 'error');
    }
    try {
      await load();
    } catch (error) {
      App.toast(error.message, 'error');
      tableBody.innerHTML = '<tr><td colspan="8" class="empty-row">数据加载失败</td></tr>';
    }
  })();
})();

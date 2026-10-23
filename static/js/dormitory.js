(function () {
  'use strict';

  App.checkLogin();
  if (window.parent && window.parent.setBreadcrumb) {
    window.parent.setBreadcrumb('宿舍管理', '/static/html/dormitory/list.html');
  }

  var state = { page: 1, size: 10, keyword: '', classId: '', total: 0, rows: [], classes: [] };

  var tableBody = document.getElementById('tableBody');
  var paginationEl = document.getElementById('pagination');
  var keywordInput = document.getElementById('keyword');
  var classFilter = document.getElementById('classFilter');
  var pageSizeSelect = document.getElementById('pageSize');

  var modal = new bootstrap.Modal(document.getElementById('dormModal'));
  var modalTitle = document.getElementById('dormModalTitle');
  var formError = document.getElementById('dormFormError');
  var saveBtn = document.getElementById('saveBtn');

  var dormId = document.getElementById('dormId');
  var building = document.getElementById('building');
  var room = document.getElementById('room');
  var capacity = document.getElementById('capacity');
  var occupied = document.getElementById('occupied');
  var classSelect = document.getElementById('classSelect');

  var editingId = null;

  function showFormError(message) { formError.textContent = message; formError.style.display = 'block'; }
  function hideFormError() { formError.style.display = 'none'; }

  async function loadRefs() {
    state.classes = (await App.request('/classroom/all')) || [];
    App.fillSelect(classFilter, state.classes, '全部班级');
    App.fillSelect(classSelect, state.classes, '请选择班级');
  }

  async function load() {
    var url = '/dormitory/page?page=' + state.page + '&page_size=' + state.size +
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
      tableBody.innerHTML = '<tr><td colspan="8" class="empty-row">暂无宿舍数据</td></tr>';
    } else {
      tableBody.innerHTML = state.rows.map(function (row) {
        var free = Number(row.capacity) - Number(row.occupied);
        return '<tr>' +
          '<td>' + row.id + '</td>' +
          '<td>' + App.escapeHtml(row.building) + '</td>' +
          '<td>' + App.escapeHtml(row.room) + '</td>' +
          '<td>' + App.escapeHtml(row.class_name || '-') + '</td>' +
          '<td>' + row.capacity + '</td>' +
          '<td>' + row.occupied + '</td>' +
          '<td><span class="badge-soft ' + (free > 0 ? 'green' : 'red') + '">' + free + '</span></td>' +
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
    document.getElementById('dormForm').reset();
    dormId.value = '';
    capacity.value = 4;
    occupied.value = 0;
    modalTitle.textContent = '新增宿舍';
    hideFormError();
    modal.show();
  }

  function openEdit(id) {
    var row = state.rows.find(function (item) { return Number(item.id) === Number(id); });
    if (!row) return;
    editingId = row.id;
    dormId.value = row.id;
    building.value = row.building || '';
    room.value = row.room || '';
    capacity.value = row.capacity;
    occupied.value = row.occupied;
    classSelect.value = row.class_id;
    modalTitle.textContent = '编辑宿舍';
    hideFormError();
    modal.show();
  }

  async function save() {
    var payload = {
      building: building.value.trim(),
      room: room.value.trim(),
      capacity: Number(capacity.value),
      occupied: Number(occupied.value),
      class_id: Number(classSelect.value)
    };
    if (!payload.building) { showFormError('请输入宿舍楼'); return; }
    if (!payload.room) { showFormError('请输入房间号'); return; }
    if (!payload.capacity || payload.capacity < 1) { showFormError('请输入床位容量'); return; }
    if (payload.occupied < 0 || payload.occupied > payload.capacity) { showFormError('入住人数需在 0 ~ 床位容量之间'); return; }
    if (!payload.class_id) { showFormError('请选择所属班级'); return; }

    saveBtn.disabled = true;
    try {
      if (editingId) {
        await App.request('/dormitory/update', { method: 'PUT', body: Object.assign({ id: editingId }, payload) });
        App.toast('宿舍信息已更新');
      } else {
        await App.request('/dormitory/add', { method: 'POST', body: payload });
        App.toast('宿舍新增成功');
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
    if (!(await App.confirm('确定删除「' + row.building + ' ' + row.room + '」吗？'))) return;
    try {
      await App.request('/dormitory/delete?dorm_id=' + id, { method: 'DELETE' });
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
      App.toast('班级数据加载失败：' + error.message, 'error');
    }
    try {
      await load();
    } catch (error) {
      App.toast(error.message, 'error');
      tableBody.innerHTML = '<tr><td colspan="8" class="empty-row">数据加载失败</td></tr>';
    }
  })();
})();

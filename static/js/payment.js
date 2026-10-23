(function () {
  'use strict';

  App.checkLogin();
  if (window.parent && window.parent.setBreadcrumb) {
    window.parent.setBreadcrumb('缴费管理', '/static/html/payment/list.html');
  }

  var state = { page: 1, size: 10, keyword: '', status: '', total: 0, rows: [], students: [] };

  var tableBody = document.getElementById('tableBody');
  var paginationEl = document.getElementById('pagination');
  var keywordInput = document.getElementById('keyword');
  var statusFilter = document.getElementById('statusFilter');
  var pageSizeSelect = document.getElementById('pageSize');

  var modal = new bootstrap.Modal(document.getElementById('paymentModal'));
  var modalTitle = document.getElementById('paymentModalTitle');
  var formError = document.getElementById('paymentFormError');
  var saveBtn = document.getElementById('saveBtn');

  var paymentId = document.getElementById('paymentId');
  var studentSelect = document.getElementById('studentSelect');
  var feeType = document.getElementById('feeType');
  var amount = document.getElementById('amount');
  var statusSelect = document.getElementById('statusSelect');
  var payDate = document.getElementById('payDate');

  var editingId = null;

  function showFormError(message) { formError.textContent = message; formError.style.display = 'block'; }
  function hideFormError() { formError.style.display = 'none'; }

  function syncPayDate() {
    if (statusSelect.value === '已缴费' && !payDate.value) payDate.value = App.today();
    if (statusSelect.value === '未缴费') payDate.value = '';
  }

  async function loadRefs() {
    state.students = (await App.request('/student/all')) || [];
    App.fillSelect(studentSelect, state.students, '请选择学生');
  }

  async function load() {
    var url = '/payment/page?page=' + state.page + '&page_size=' + state.size +
      '&keyword=' + encodeURIComponent(state.keyword) +
      '&status=' + encodeURIComponent(state.status);
    var data = await App.request(url);
    state.rows = (data && data.rows) || [];
    state.total = (data && data.total) || 0;
    if (!state.rows.length && state.page > 1) { state.page -= 1; return load(); }
    render();
  }

  function render() {
    if (!state.rows.length) {
      tableBody.innerHTML = '<tr><td colspan="8" class="empty-row">暂无缴费记录</td></tr>';
    } else {
      tableBody.innerHTML = state.rows.map(function (row) {
        return '<tr>' +
          '<td>' + row.id + '</td>' +
          '<td>' + App.escapeHtml(row.student_name || '-') + '</td>' +
          '<td>' + App.escapeHtml(row.class_name || '-') + '</td>' +
          '<td>' + App.escapeHtml(row.fee_type) + '</td>' +
          '<td>￥' + Number(row.amount).toFixed(2) + '</td>' +
          '<td><span class="badge-soft ' + (row.status === '已缴费' ? 'green' : 'orange') + '">' + App.escapeHtml(row.status) + '</span></td>' +
          '<td>' + (row.pay_date ? App.formatDateTime(row.pay_date) : '-') + '</td>' +
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
    document.getElementById('paymentForm').reset();
    paymentId.value = '';
    statusSelect.value = '未缴费';
    payDate.value = '';
    modalTitle.textContent = '新增缴费';
    hideFormError();
    modal.show();
  }

  function openEdit(id) {
    var row = state.rows.find(function (item) { return Number(item.id) === Number(id); });
    if (!row) return;
    editingId = row.id;
    paymentId.value = row.id;
    studentSelect.value = row.student_id;
    feeType.value = row.fee_type || '';
    amount.value = row.amount;
    statusSelect.value = row.status;
    payDate.value = App.toDate(row.pay_date);
    modalTitle.textContent = '编辑缴费';
    hideFormError();
    modal.show();
  }

  async function save() {
    var payload = {
      student_id: Number(studentSelect.value),
      fee_type: feeType.value.trim(),
      amount: Number(amount.value),
      status: statusSelect.value,
      pay_date: payDate.value || null
    };
    if (!payload.student_id) { showFormError('请选择学生'); return; }
    if (!payload.fee_type) { showFormError('请输入费用类型'); return; }
    if (amount.value === '' || isNaN(payload.amount) || payload.amount <= 0) { showFormError('请输入正确的金额'); return; }

    saveBtn.disabled = true;
    try {
      if (editingId) {
        await App.request('/payment/update', { method: 'PUT', body: Object.assign({ id: editingId }, payload) });
        App.toast('缴费记录已更新');
      } else {
        await App.request('/payment/add', { method: 'POST', body: payload });
        App.toast('缴费新增成功');
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
    if (!(await App.confirm('确定删除「' + (row.student_name || '') + ' - ' + row.fee_type + '」的缴费记录吗？'))) return;
    try {
      await App.request('/payment/delete?payment_id=' + id, { method: 'DELETE' });
      App.toast('删除成功');
      await load();
    } catch (error) {
      App.toast(error.message, 'error');
    }
  }

  document.getElementById('addBtn').addEventListener('click', openAdd);
  saveBtn.addEventListener('click', save);
  statusSelect.addEventListener('change', syncPayDate);
  document.getElementById('searchForm').addEventListener('submit', function (event) {
    event.preventDefault();
    state.keyword = keywordInput.value.trim();
    state.status = statusFilter.value;
    state.page = 1;
    load().catch(function (error) { App.toast(error.message, 'error'); });
  });
  document.getElementById('resetBtn').addEventListener('click', function () {
    keywordInput.value = '';
    statusFilter.value = '';
    state.keyword = '';
    state.status = '';
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

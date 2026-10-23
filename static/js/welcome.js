(function () {
  'use strict';

  App.checkLogin();
  if (window.parent && window.parent.setBreadcrumb) {
    window.parent.setBreadcrumb('首页', '/static/html/welcome.html');
  }

  document.getElementById('welcomeUser').textContent = App.adminName();

  var classStats = document.getElementById('classStats');
  var noticeList = document.getElementById('noticeList');
  var noticeDetail = document.getElementById('noticeDetail');
  var noticeModalEl = document.getElementById('noticeModal');
  var noticeModal = noticeModalEl ? new bootstrap.Modal(noticeModalEl) : null;

  function go(url, title) {
    if (window.parent && window.parent.navigate) {
      window.parent.navigate(url, title);
    } else {
      window.location.href = url;
    }
  }

  document.querySelectorAll('[data-url]').forEach(function (button) {
    button.addEventListener('click', function () {
      go(button.dataset.url, button.dataset.title);
    });
  });

  function setText(id, value) {
    var el = document.getElementById(id);
    if (el) el.textContent = value;
  }

  async function load() {
    var data = await App.request('/dashboard/overview');
    var counts = data.counts || {};
    setText('studentCount', counts.students || 0);
    setText('teacherCount', counts.teachers || 0);
    setText('subjectCount', counts.subjects || 0);
    setText('classCount', counts.classes || 0);
    setText('courseCount', counts.courses || 0);
    setText('assignmentCount', counts.assignments || 0);

    var score = data.score || {};
    setText('scoreAverage', Number(score.average || 0).toFixed(1));
    setText('passRate', '及格率 ' + Number(score.pass_rate || 0).toFixed(1) + '%');
    setText('scoreTotal', score.total || 0);

    var awards = data.awards || {};
    setText('awardSummary', '奖励 ' + (awards['奖励'] || 0) + ' / 处分 ' + (awards['处分'] || 0));

    var attendance = data.attendance || {};
    setText('attendanceTotal', attendance.total || 0);
    setText('attendanceNormal', attendance['正常'] || 0);
    setText('attendanceLate', attendance['迟到'] || 0);
    setText('attendanceAbsent', attendance['缺勤'] || 0);
    setText('attendanceLeave', attendance['请假'] || 0);

    var payment = data.payment || {};
    setText('paidAmount', '￥' + Number(payment.paid_amount || 0).toFixed(2));
    setText('unpaidCount', payment.unpaid_count || 0);
    setText('paymentTip', (payment.unpaid_count || 0) > 0 ? '有待缴费用' : '收缴正常');

    var dorm = data.dormitory || {};
    var capacity = Number(dorm.capacity || 0);
    var occupied = Number(dorm.occupied || 0);
    setText('dormOccupied', occupied);
    setText('dormCapacity', capacity);
    setText('dormRate', (capacity ? Math.round(occupied / capacity * 100) : 0) + '%');

    renderClasses(data.class_distribution || []);
    renderNotices(data.notices || []);
  }

  function renderClasses(rows) {
    if (!rows.length) {
      classStats.innerHTML = '<tr><td colspan="3" class="empty-row">暂无分班数据</td></tr>';
      return;
    }
    classStats.innerHTML = rows.map(function (row, index) {
      return '<tr>' +
        '<td>' + (index + 1) + '</td>' +
        '<td>' + App.escapeHtml(row.name) + '</td>' +
        '<td><span class="badge-soft ' + (row.total ? 'green' : 'gray') + '">' + row.total + ' 人</span></td>' +
        '</tr>';
    }).join('');
  }

  function renderNotices(rows) {
    if (!rows.length) {
      noticeList.innerHTML = '<li class="empty-row">暂无公告</li>';
      return;
    }
    noticeList.innerHTML = rows.map(function (row) {
      return '<li data-id="' + row.id + '" title="点击查看公告全文">' +
        '<div class="notice-item-head">' +
        '<div class="notice-title">' + App.escapeHtml(row.title) + '</div>' +
        '<i class="bi bi-chevron-right notice-arrow"></i>' +
        '</div>' +
        '<div class="notice-meta">' + App.escapeHtml(row.publisher) + ' · ' + App.formatDateTime(row.publish_time) + '</div>' +
        '</li>';
    }).join('');
  }

  function chineseDate(value) {
    var parts = String(value || '').slice(0, 10).split('-');
    if (parts.length !== 3) return App.formatDateTime(value);
    return parts[0] + '年' + Number(parts[1]) + '月' + Number(parts[2]) + '日';
  }

  function renderNoticeDoc(row) {
    var lines = String(row.content || '').split(/\r?\n/).map(function (line) {
      return line.trim();
    }).filter(function (line) {
      return line.length > 0;
    });
    if (!lines.length) lines = ['暂无内容'];

    var paragraphs = lines.map(function (line) {
      return '<p>' + App.escapeHtml(line) + '</p>';
    }).join('');

    noticeDetail.innerHTML =
      '<div class="notice-doc">' +
      '<h3 class="notice-doc-title">' + App.escapeHtml(row.title) + '</h3>' +
      '<div class="notice-doc-meta">发布部门：' + App.escapeHtml(row.publisher) +
      ' · 发布时间：' + App.formatDateTime(row.publish_time) + '</div>' +
      '<hr>' +
      '<div class="notice-doc-body">' +
      '<p class="notice-doc-to">各处室、各年级组、各班级：</p>' +
      paragraphs +
      '<p class="notice-doc-sign">' + App.escapeHtml(row.publisher) + '</p>' +
      '<p class="notice-doc-date">' + chineseDate(row.publish_time) + '</p>' +
      '</div>' +
      '</div>';
  }

  async function openNotice(id) {
    if (!noticeModal) return;
    noticeDetail.innerHTML = '<div class="text-center text-muted py-4">公告加载中...</div>';
    noticeModal.show();
    try {
      var row = await App.request('/notice/one?notice_id=' + encodeURIComponent(id));
      renderNoticeDoc(row);
    } catch (error) {
      noticeDetail.innerHTML = '<div class="text-center text-muted py-4">' +
        App.escapeHtml(error.message) + '</div>';
    }
  }

  noticeList.addEventListener('click', function (event) {
    var item = event.target.closest('li[data-id]');
    if (!item) return;
    openNotice(item.dataset.id);
  });

  load().catch(function (error) {
    App.toast(error.message, 'error');
    classStats.innerHTML = '<tr><td colspan="3" class="empty-row">数据加载失败</td></tr>';
    noticeList.innerHTML = '<li class="empty-row">数据加载失败</li>';
  });
})();

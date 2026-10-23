(function () {
  'use strict';

  App.checkLogin();
  if (window.parent && window.parent.setBreadcrumb) {
    window.parent.setBreadcrumb('课表中心', '/static/html/timetable/list.html');
  }

  var DAYS = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
  var body = document.getElementById('timetableBody');
  var classSelect = document.getElementById('classSelect');
  var summary = document.getElementById('summary');

  async function loadClasses() {
    var classes = (await App.request('/classroom/all')) || [];
    App.fillSelect(classSelect, classes, '请选择班级');
    if (classes.length) {
      classSelect.value = classes[0].id;
      await load();
    }
  }

  async function load() {
    var classId = classSelect.value;
    if (!classId) {
      summary.textContent = '-';
      body.innerHTML = '<tr><td colspan="7" class="empty-row">请选择班级</td></tr>';
      return;
    }
    var courses = (await App.request('/course/timetable?class_id=' + classId)) || [];
    summary.textContent = '共 ' + courses.length + ' 门课程';
    if (!courses.length) {
      body.innerHTML = '<tr><td colspan="7" class="empty-row">该班级暂无课程安排</td></tr>';
      return;
    }

    var groups = {};
    DAYS.forEach(function (day) { groups[day] = []; });
    courses.forEach(function (course) {
      (groups[course.schedule_day] || groups['周一']).push(course);
    });

    body.innerHTML = '<tr>' + DAYS.map(function (day) {
      var items = groups[day].map(function (course) {
        return '<div class="timetable-item">' +
          '<strong>' + App.escapeHtml(course.name) + '</strong>' +
          '<div class="small text-muted">' + App.escapeHtml(course.start_time + '-' + course.end_time) + '</div>' +
          '<div class="small">' + App.escapeHtml(course.teacher_name || '-') + ' · ' + App.escapeHtml(course.subject_name || '-') + '</div>' +
          '</div>';
      }).join('');
      return '<td class="timetable-cell">' + (items || '<span class="text-muted small">无课</span>') + '</td>';
    }).join('') + '</tr>';
  }

  classSelect.addEventListener('change', function () {
    load().catch(function (error) { App.toast(error.message, 'error'); });
  });

  (async function init() {
    try {
      await loadClasses();
    } catch (error) {
      App.toast(error.message, 'error');
      body.innerHTML = '<tr><td colspan="7" class="empty-row">数据加载失败</td></tr>';
    }
  })();
})();

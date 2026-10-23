(function () {
  'use strict';

  App.checkLogin();

  var frame = document.getElementById('contentFrame');
  var breadcrumb = document.getElementById('breadcrumb');
  var links = Array.prototype.slice.call(
    document.querySelectorAll('.sidebar-menu .nav-link[data-page]')
  );

  document.getElementById('adminName').textContent = App.adminName();

  function markActive(url) {
    links.forEach(function (link) {
      link.classList.toggle('active', link.dataset.page === url);
    });
  }

  function navigate(url, title) {
    frame.src = url;
    breadcrumb.textContent = title;
    document.title = title + ' - 教务管理系统';
    markActive(url);
  }

  links.forEach(function (link) {
    link.addEventListener('click', function (event) {
      event.preventDefault();
      navigate(link.dataset.page, link.dataset.title);
    });
  });

  // 供 iframe 内页面调用：设置面包屑并同步菜单高亮
  window.navigate = navigate;
  window.setBreadcrumb = function (title, url) {
    breadcrumb.textContent = title;
    document.title = title + ' - 教务管理系统';
    if (url) markActive(url);
  };

  document.getElementById('logoutBtn').addEventListener('click', function () {
    App.confirm('确定要退出登录吗？', '退出确认').then(function (ok) {
      if (ok) App.logout();
    });
  });

  document.getElementById('sidebarToggle').addEventListener('click', function () {
    document.body.classList.toggle('sidebar-collapsed');
  });

  if (window.innerWidth < 768) {
    document.body.classList.add('sidebar-collapsed');
  }

  markActive('/static/html/welcome.html');
})();

(function () {
  'use strict';

  if (App.isLogin()) {
    window.location.replace('/static/html/index.html');
    return;
  }

  var form = document.getElementById('loginForm');
  var usernameInput = document.getElementById('username');
  var passwordInput = document.getElementById('password');
  var errorBox = document.getElementById('loginError');

  function showError(message) {
    errorBox.textContent = message;
    errorBox.style.display = 'block';
  }

  form.addEventListener('submit', async function (event) {
    event.preventDefault();
    errorBox.style.display = 'none';

    var username = usernameInput.value.trim();
    var password = passwordInput.value;

    if (!username) {
      showError('请输入账号');
      usernameInput.focus();
      return;
    }
    if (!password) {
      showError('请输入密码');
      passwordInput.focus();
      return;
    }

    var button = form.querySelector('button[type="submit"]');
    button.disabled = true;
    try {
      var user = await App.request('/user/login', {
        method: 'POST',
        body: { username: username, password: password }
      });
      App.login(user.nickname || user.username);
      window.location.href = '/static/html/index.html';
    } catch (error) {
      showError(error.message);
      button.disabled = false;
    }
  });
})();

(function () {
  'use strict';

  if (App.isLogin()) {
    window.location.replace('/static/html/index.html');
    return;
  }

  var form = document.getElementById('registerForm');
  var errorBox = document.getElementById('registerError');
  var button = document.getElementById('registerBtn');

  function showError(message) {
    errorBox.textContent = message;
    errorBox.style.display = 'block';
  }

  form.addEventListener('submit', async function (event) {
    event.preventDefault();
    errorBox.style.display = 'none';

    var username = document.getElementById('username').value.trim();
    var nickname = document.getElementById('nickname').value.trim();
    var password = document.getElementById('password').value;
    var confirmPassword = document.getElementById('confirmPassword').value;

    if (username.length < 3) {
      showError('用户名至少 3 个字符');
      return;
    }
    if (password.length < 6) {
      showError('密码至少 6 位');
      return;
    }
    if (password !== confirmPassword) {
      showError('两次输入的密码不一致');
      return;
    }

    button.disabled = true;
    try {
      await App.request('/user/register', {
        method: 'POST',
        body: { username: username, password: password, nickname: nickname }
      });
      App.toast('注册成功，即将跳转登录');
      setTimeout(function () {
        window.location.href = '/static/html/login.html';
      }, 900);
    } catch (error) {
      showError(error.message);
      button.disabled = false;
    }
  });
})();

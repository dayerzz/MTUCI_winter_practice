fetch("http://127.0.0.1:8000/history")
  .then(res => res.json())
  .then(data => {
    const table = document.getElementById("table");

    let totalMotos = 0;
    let totalViol = 0;

    data.forEach(item => {
      totalMotos += item.motorcycles;
      totalViol += item.violations;

      table.innerHTML += `
        <tr>
          <td>${item.filename}</td>
          <td>${item.date}</td>
          <td>${item.motorcycles}</td>
          <td>${item.violations}</td>
        </tr>
      `;
    });

    document.getElementById("checks").textContent =
      `Проверок: ${data.length}`;

    document.getElementById("motos").textContent =
      `Мотоциклов: ${totalMotos}`;

    document.getElementById("viol").textContent =
      `Нарушений: ${totalViol}`;
  })
  .catch(() => {
    alert("Ошибка загрузки статистики");
  });
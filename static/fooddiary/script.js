$(document).ready(function() {
      // Переключение даты
      $('#prevDay').click(function() {
          let currentDate = new Date($('#selectedDate').val());
          currentDate.setDate(currentDate.getDate() - 1);
          updateDate(currentDate);
      });

      $('#nextDay').click(function() {
          let currentDate = new Date($('#selectedDate').val());
          currentDate.setDate(currentDate.getDate() + 1);
          updateDate(currentDate);
      });

      $('#chooseDateBtn').click(function() {
          let input = document.createElement('input');
          input.type = 'date';
          input.onchange = function() {
              let selectedDate = new Date(this.value);
              updateDate(selectedDate);
          };
          input.click();
      });

      function updateDate(date) {
          let formatted = date.toISOString().split('T')[0];
          $('#selectedDate').val(formatted);
          $('#currentDateDisplay').text(date.toLocaleDateString('ru-RU'));
          window.location.href = '?date=' + formatted;
      }

      // Поиск продуктов
      $('#searchInput').on('input', function() {
          let query = $(this).val();
          if (query.length < 2) {
              $('#searchResults').empty();
              return;
          }

          $.ajax({
              url: $('#searchFoodsUrl').val(),
              data: { q: query },
              success: function(data) {
                  $('#searchResults').empty();
                  data.results.forEach(function(item) {
                      let resultItem = `
                          <div class="list-group-item search-results-item" data-food-id="${item.id}">
                              ${item.name} (${item.calories} ккал/100г)
                          </div>`;
                      $('#searchResults').append(resultItem);
                  });
              }
          });
      });

      // Открытие модального окна для добавления продукта
      $(document).on('click', '.search-results-item', function() {
          let foodId = $(this).data('food-id');
          let foodLabel = $(this).text().trim();
          $('#foodId').val(foodId);
          $('#selectedFoodLabel').text(foodLabel);
          $('#quantity').val('');
          $('#addFoodModal').modal('show');
      });

      // Добавление продукта в дневник
      $('#addFoodForm').submit(function(e) {
          e.preventDefault();
          $.ajax({
              url: $('#addFoodUrl').val(),
              method: 'POST',
              data: $(this).serialize(),
              beforeSend: function(xhr, settings) {
                  xhr.setRequestHeader('X-CSRFToken', $('input[name=csrfmiddlewaretoken]').val());
              },
              success: function() {
                  $('#addFoodModal').modal('hide');
                  location.reload();
              },
              error: function(xhr) {
                  console.error('Ошибка при добавлении продукта:', xhr.responseText);
              }
          });
      });

      // Создание нового продукта
      $('#createFoodForm').submit(function(e) {
          e.preventDefault();
          $.ajax({
              url: $('#createFoodUrl').val(),
              method: 'POST',
              data: $(this).serialize(),
              beforeSend: function(xhr, settings) {
                  xhr.setRequestHeader('X-CSRFToken', $('input[name=csrfmiddlewaretoken]').val());
              },
              success: function() {
                  $('#createFoodModal').modal('hide');
                  alert('Продукт успешно добавлен!');
                  location.reload();
              },
              error: function(xhr) {
                  console.error('Ошибка при создании продукта:', xhr.responseText);
              }
          });
      });

      // Удаление записи
      $(document).on('click', '.delete-entry-btn', function() {
          let entryId = $(this).data('entry-id');
          if (confirm('Вы уверены, что хотите удалить эту запись?')) {
              $.ajax({
                  url: $('#deleteEntryUrlBase').val() + entryId + '/',
                  method: 'GET',
                  success: function() {
                      location.reload();
                  },
                  error: function(xhr) {
                      console.error('Ошибка при удалении записи:', xhr.responseText);
                  }
              });
          }
      });
  });

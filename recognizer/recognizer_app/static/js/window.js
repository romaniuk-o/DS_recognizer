  const fileInput = document.getElementById("fileInput");
  const fileStatusLabel = document.getElementById("fileStatusLabel");
  const fileNameSpan = document.getElementById("fileNameSpan");

  fileInput.addEventListener("change", function() {
    if (fileInput.files.length > 0) {
      const fileName = fileInput.files[0].name;
      const fileExtension = fileName.split('.').pop();
      const maxLength = 15; // Максимальна довжина назви файлу
      const truncatedFileName = truncateString(fileName, maxLength);
      const truncatedFileNameWithExtension = truncatedFileName + '.' + fileExtension;
      fileStatusLabel.textContent = "Selected file:";
      fileNameSpan.textContent = truncatedFileNameWithExtension;
    } else {
      fileStatusLabel.textContent = "File not selected";
      fileNameSpan.textContent = "";
    }
  });

  // Функція для обмеження довжини рядка
  function truncateString(str, maxLength) {
    if (str.length > maxLength) {
      const truncatedStr = str.substring(0, maxLength / 2) + '...' + str.substring(str.length - maxLength / 2);
      return truncatedStr;
    }
    return str;
  }


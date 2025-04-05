function showToast(message, type) {
    const toastElement = document.getElementById("customToast");
    const toastMessage = document.getElementById("toastMessage");

    toastMessage.innerText = message;

    toastElement.classList.remove("text-bg-primary", "text-bg-success", "text-bg-danger");

    if (type === "success") {
        toastElement.classList.add("text-bg-success");
    } else if (type === "error") {
        toastElement.classList.add("text-bg-danger");
    } else {
        toastElement.classList.add("text-bg-primary");
    }

    const toast = new bootstrap.Toast(toastElement);
    toast.show();
}
function copyCommand() {
    var copyText = document.getElementById("command");
    copyText.select();
    copyText.setSelectionRange(0, 99999);
    document.execCommand("copy");
}

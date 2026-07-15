function focus_in() {
    console.log("in")
    document.getElementById("ext_display").style.opacity = 1
    document.getElementById("ext_display").style.userSelect = 'auto'
}

function focus_out() {
    console.log("out")
    document.getElementById("ext_display").style.opacity = 0
    document.getElementById("ext_display").style.userSelect = 'none'
}

function validate_url() {
    let text = document.getElementById('steam_url_input').value.trim()
    let err_label = document.getElementById('err_url_label')

    const xhttp = new XMLHttpRequest();
    xhttp.onload = function () {
        const res = JSON.parse(this.responseText)

        if (res.valid_url === false) {
            err_label.style.animation = 'none'
            err_label.offsetWidth
            err_label.style.animation = 'show_invalid_label 1s normal forwards'
        }
        console.log(this.responseText)
        console.log(res.valid_url)
    }
    xhttp.open("GET", `/validate/?url=${encodeURIComponent(text)}`)
    xhttp.send();
}

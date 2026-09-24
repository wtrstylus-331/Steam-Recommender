function focus_in() {
    //console.log("in")
    document.getElementById("ext_display").style.opacity = 1
    document.getElementById("ext_display").style.userSelect = 'auto'
}

function focus_out() {
    //console.log("out")
    document.getElementById("ext_display").style.opacity = 0
    document.getElementById("ext_display").style.userSelect = 'none'
}

async function validate_url() {
    let text = document.getElementById('steam_url_input').value.trim()
    let err_label = document.getElementById('err_url_label')

    let jsonResponse = await req();

    async function req() {
        return fetch(`/validate/?url=${encodeURIComponent(text)}`, {
        method: 'GET'
        }).then(response => response.json());
    }

    console.log(jsonResponse)

    if (jsonResponse.valid_url === false) {
        if (text === '') {
            //console.log("no text")
            err_label.children[0].innerHTML = 'No entry provided'
        } else {
            err_label.children[0].innerHTML = 'Invalid Entry'
        }

        err_label.style.animation = 'none'
        err_label.offsetWidth
        err_label.style.animation = 'show_invalid_label 1s normal forwards'
    } else {
        window.location.href = `/profile/?url=${encodeURIComponent(text)}`
    }
}

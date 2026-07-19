function image_load_error(img) {
    console.log("Failed to load game capsule for " + img.alt)
    img.src = "/static/images/not_found.png"
}

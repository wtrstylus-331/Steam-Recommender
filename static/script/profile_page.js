let shownGames = 0;
const gameIncrement = 8;

document.addEventListener("DOMContentLoaded", () => {
    expand()
})

function image_load_error(img) {
    console.log("Failed to load game capsule for " + img.alt)
    img.src = "/static/images/not_found.png"
}

function expand() {
    const games = document.querySelectorAll(".owned-game-card");

    for (let i = shownGames; i < shownGames + gameIncrement && i < games.length; i++) {
        games[i].style.display = "flex";
    }

    shownGames += gameIncrement;

    if (shownGames >= games.length) {
        document.querySelector(".owned-display-btn").style.display = "none";
    }
}

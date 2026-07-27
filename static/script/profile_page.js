let shownGames = 0;
const gameIncrement = 8;

const sortMethod = {
    Name: "name",
    Playtime_Ascending: "playtime_ascending",
    Playtime_Descending: "playtime_descending"
}
let currSortMethod = null

document.addEventListener("DOMContentLoaded", () => {
    currSortMethod = sortMethod.Name
})

function image_load_error(img) {
    console.log("Failed to load game capsule for " + img.alt)
    img.src = "/static/images/not_found.png"
}

function expand(count) {
    lazyLoad()

    const games = Array.from(document.querySelectorAll(".owned-game-card"));

    for (let i = shownGames; i < shownGames + gameIncrement && i < games.length; i++) {
        games[i].style.display = "flex";
    }

    shownGames += gameIncrement;

    if (shownGames >= count) {
        document.querySelector(".owned-display-btn").style.display = "none";
    }
}

async function lazyLoad() {
    const response = await fetch("/lazyload/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        }
    })

    if (!response.ok) {
        return
    }

    const data = await response.json();
    console.log(data)

    let grid = document.getElementById('owned-grid-id')
    data.games.forEach(game => {
        const card = document.createElement("div");
        card.className = "owned-game-card";
        card.style.display = "flex";

        card.innerHTML = `
            <img src="https://cdn.cloudflare.steamstatic.com/steam/apps/${game.app_id}/library_600x900.jpg"
                 alt="image-${game.app_name}"
                 class="game-image"
                 onerror="image_load_error(this)">
            <h3 class="game-name">${game.app_name}</h3>
            <h1 class="game-playtime">${game.playtime_forever_hrs} hrs</h1>
        `;

        grid.appendChild(card);
    });

    const games = Array.from(document.querySelectorAll(".owned-game-card"));

    switch (currSortMethod) {
        case sortMethod.Name:
            sortNames(games);
            grid.innerHTML = "";
            games.forEach(card => grid.appendChild(card));
            break;
        default:
            sortPlaytime(games, currSortMethod);
            grid.innerHTML = "";
            games.forEach(card => grid.appendChild(card));
            break;
    }
}

function getCookie(name) {
    const value = `; ${document.cookie}`
    console.log(document.cookie)
    const parts = value.split(`; ${name}=`)
    if (parts.length === 2) return parts.pop().split(";").shift()
}

function sortBy(type) {
    const games = Array.from(document.querySelectorAll(".owned-game-card"));

    if (type === 'playtime') {
        if (document.querySelector("#playtime-btn span").textContent === "Playtime (Descending)") {
            document.querySelector("#playtime-btn span").textContent = "Playtime (Ascending)"
            currSortMethod = sortMethod.Playtime_Descending
            sortPlaytime(games, sortMethod.Playtime_Descending)
        } else {
            document.querySelector("#playtime-btn span").textContent = "Playtime (Descending)"
            currSortMethod = sortMethod.Playtime_Ascending
            sortPlaytime(games, sortMethod.Playtime_Ascending)
        }
    } else {
        currSortMethod = sortMethod.Name
        sortNames(games)
    }

    let grid = document.getElementById('owned-grid-id')
    grid.innerHTML = "";
    games.forEach(card => grid.appendChild(card));
}

function sortNames(games) {
    games.sort((a, b) => {
        const game1 = a.querySelector(".game-name").textContent.toLowerCase();
        const game2 = b.querySelector(".game-name").textContent.toLowerCase();
        return game1.localeCompare(game2);
    });
}

function sortPlaytime(games, type) {
    games.sort((a, b) => {
        const a_text = a.querySelector(".game-playtime").textContent.toLowerCase().split(" ")[0].trim()
        const b_text = b.querySelector(".game-playtime").textContent.toLowerCase().split(" ")[0].trim()
        const game1 = parseInt(a_text)
        const game2 = parseInt(b_text)

        if (type === sortMethod.Playtime_Ascending) {
            return game1 - game2;
        } else {
            return game2 - game1;
        }
    });
}

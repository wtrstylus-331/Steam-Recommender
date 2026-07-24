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

function getCookie(name) {
    const value = `; ${document.cookie}`
    console.log(document.cookie)
    const parts = value.split(`; ${name}=`)
    if (parts.length === 2) return parts.pop().split(";").shift()
}

async function sortBy(type) {
    let curr_type = ""

    if (type === 'playtime') {
        if (document.querySelector("#playtime-btn span").textContent === "Playtime (Descending)") {
            document.querySelector("#playtime-btn span").textContent = "Playtime (Ascending)"
            curr_type = "playtime-descending"
        } else {
            document.querySelector("#playtime-btn span").textContent = "Playtime (Descending)"
            curr_type = "playtime-ascending"
        }
    } else {
        curr_type = "name"
    }

    const response = await fetch("/sortgames/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({ type: curr_type }),
    })

    console.log(response)

    if (!response.ok) {
        return
    }

    const data = await response.json();
    console.log(data)
    refreshGrid(data)
}

function refreshGrid(data) {
    let grid = document.getElementById('owned-grid-id')
    grid.replaceChildren()

    data.games.forEach(game => {
        const card = document.createElement("div");
        card.className = "owned-game-card";
        card.style.display = "none";

        card.innerHTML = `
            <img src="https://cdn.cloudflare.steamstatic.com/steam/apps/${game.app_id}/library_600x900.jpg"
                 alt="image-${game.app_name}"
                 class="game-image"
                 onerror="image_load_error(this)">
            <h3 class="game-name">${game.app_name}</h3>
        `;

        grid.appendChild(card);
    });

    shownGames = 0
    if (document.querySelector(".owned-display-btn").style.display === "none") {
        document.querySelector(".owned-display-btn").style.display = "block";
    }
    expand()
}

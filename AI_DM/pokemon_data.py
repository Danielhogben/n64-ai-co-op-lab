"""Constants for the Pokemon Region Generator."""

POKEMON_REGIONS = [
    {
        "id": "kanto",
        "name": "Kanto",
        "generation": 1,
        "dex": 151,
        "starter_trio": ["Bulbasaur", "Charmander", "Squirtle"],
    },
    {
        "id": "johto",
        "name": "Johto",
        "generation": 2,
        "dex": 100,
        "starter_trio": ["Chikorita", "Cyndaquil", "Totodile"],
    },
    {
        "id": "hoenn",
        "name": "Hoenn",
        "generation": 3,
        "dex": 135,
        "starter_trio": ["Treecko", "Torchic", "Mudkip"],
    },
    {
        "id": "sinnoh",
        "name": "Sinnoh",
        "generation": 4,
        "dex": 107,
        "starter_trio": ["Turtwig", "Chimchar", "Piplup"],
    },
    {
        "id": "unova",
        "name": "Unova",
        "generation": 5,
        "dex": 156,
        "starter_trio": ["Snivy", "Tepig", "Oshawott"],
    },
    {
        "id": "kalos",
        "name": "Kalos",
        "generation": 6,
        "dex": 72,
        "starter_trio": ["Chespin", "Fennekin", "Froakie"],
    },
    {
        "id": "alola",
        "name": "Alola",
        "generation": 7,
        "dex": 88,
        "starter_trio": ["Rowlet", "Litten", "Popplio"],
    },
    {
        "id": "galar",
        "name": "Galar",
        "generation": 8,
        "dex": 89,
        "starter_trio": ["Grookey", "Scorbunny", "Sobble"],
    },
    {
        "id": "paldea",
        "name": "Paldea",
        "generation": 9,
        "dex": 103,
        "starter_trio": ["Sprigatito", "Fuecoco", "Quaxly"],
    },
]

POKEMON_STORY_ARCHETYPES = [
    "Team {villain} has returned! They are using the {artifact} to {goal} the legendary {legend}. If they succeed, the entire region will {purge} and be replaced by a {type}-type paradise. You, the {chosen_one}, must find Professor {oak} and stop them before the {ruins} are destroyed.",
    "A strange {disease} is spreading through the Pokémon of {facility}. The {mythical} Pokémon has begun to {malfunction}. Team {villain} claims they can fix it with their {artifact}, but they actually want to {goal} the {guardian}. You must intervene!",
    "The {guardian} has been awakened by the {cult}. They are searching for the {artifact} to control the {legend}. You must explore the {ruins} and gather the {type} energy to seal them away forever.",
]

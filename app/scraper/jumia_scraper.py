def search_jumia(query: str) -> list[dict]:
    """
    MOCK temporaire - à remplacer par le vrai scraper de l'équipe.
    Retourne des résultats factices respectant le contrat d'interface.
    """
    return [
        {
            "nom": f"{query} - Résultat {i}",
            "image_url": "https://via.placeholder.com/150",
            "lien": "https://www.jumia.com",
            "prix": f"{1000 * i} FCFA",
        }
        for i in range(1, 4)
    ]
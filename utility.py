class Utility():
    """
    Utility class containing helper functions for the game.
    """

    def remove_duplicates(lst):
        """
        Remove duplicates from a list.

        Args:
            lst (list): The list from which duplicates need to be removed.

        Returns:
            list: A list with duplicates removed.
        """
        return list(set([i for i in lst]))

    def reverse_lookup_submarine(submarine: tuple) -> str:
        """
        Reverse lookup to find the country of a submarine.

        Args:
            submarine (tuple): The coordinates of the submarine.

        Returns:
            str: The country to which the submarine belongs.
        """
        for country in countries:
            if countries[country]['subs']:
                if submarine in countries[country]['subs']:
                    return country

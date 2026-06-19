class ColorDice:
    def __init__(self, color, rect, distances=None, bad_colors=None):
        self.color, self.rect = color, rect
        self.distances = distances if distances is not None else {}
        self.bad_colors = bad_colors if bad_colors is not None else []

    def __str__(self):
        return f"ColorDice {self.color} : {self.distances}"


class MemoryCar:
    def __init__(self, id_car, name, color, genetic, best_scores):
        self.id, self.name = id_car, name
        self.color, self.genetic = color, genetic
        self.best_scores = best_scores

    def __str__(self):
        string = f"{self.id} {self.name} {self.color} {self.genetic}"
        for score in self.best_scores:
            string += f" {score}"
        return string

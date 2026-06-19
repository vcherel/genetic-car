# genetic-car

Interactive genetic algorithm demonstrator built with pygame. Cars navigate a circuit using detection cones; each generation is evolved via selection, crossover, and mutation. Car parameters can also be set by capturing colored dice via webcam.

## Running

```bash
bash install_env.sh   # create venv and install deps (uv)
bash start.sh         # run the app
```

Or directly:

```bash
uv run python src/main.py
```

## Key files

- `src/main.py` — main loop: window, game turns, generation transitions, test runners
- `src/game/car.py` — `Car` class: movement, detection cone, scoring
- `src/game/genetic.py` — `Genetic` class: cone parameters (6 dice values)
- `src/game/genetic_algorithm.py` — selection, crossover, mutation
- `src/data/variables.py` — global mutable state
- `src/data/constants.py` — per-map constants (start positions, car sizes)
- `src/other/camera.py` / `camera_utils.py` — dice detection via OpenCV
- `src/render/` — pygame drawing helpers (buttons, UI, explosions)
- `src/menus/` — settings, garage, dice menus
- `data/checkpoints/` — checkpoint coordinates per map (0–7)
- `data/cars/` — saved cars (JSON-like format)

## Dependencies

Managed with uv (`pyproject.toml`). Main deps: pygame, numpy, opencv-python-headless, matplotlib.

## Code style

- ruff lint + ruff format enforced via pre-commit
- No unnecessary comments: only add WHY comments, never WHAT comments
- src/ layout: all source under `src/`

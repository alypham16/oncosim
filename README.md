# OncoSim Overview
OncoSim (tentative name) is a computational tool used to simulate population dynamics and evolution of the highly heterogenous intratumoral environment. The system utilizes tumor populations as a mixture of several different states based on marker expression and simulates these shifts under drug treatments.

To build and run with Docker:

```bash
docker build -t tumor-sim .
docker run --rm -v $(pwd)/output:/app/output tumor-sim
```

## Current Files
- README.md: This file, used to describe the contents and mechanics of the project. Will include future set-up requirements as the project is built.
- Dockerfile: a Dockerfile containerizing the code
- cell_state.py: basic cell population definitions
- drug_models.py: defining how drugs will affect the cell population dynamics.

Names, contents, etc. of the repository are subject to change as OncoSim is built. 

## AI Usage
# Curve Building Calculation Engine

This module implements methods for constructing forward curves and swap curves using various numerical techniques.

## Features:

- Spline fitting
- Polynomial interpolation
- Bootstrapping methods
- Recalibration logic

## Installation

To install the required dependencies, run:
```bash
pip install -r requirements.txt
```

## Usage

### Creating Forward Curves

```python
from curve_builder import create_forward_curve

# Example usage
forward_curve = create_forward_curve(data)
```

### Creating Swap Curves

```python
from curve_builder import create_swap_curve

# Example usage
swap_curve = create_swap_curve(data)
```

## Implementation Details

- **Spline Fitting:** Utilizes cubic spline fitting for smooth interpolation.
- **Polynomial Interpolation:** Employs polynomial fitting techniques for curve creation.
- **Bootstrapping:** Implements bootstrapping to derive yield curves.
- **Recalibration Logic:** Includes methods for recalibrating curves based on new data.

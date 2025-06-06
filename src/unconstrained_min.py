from abc import abstractmethod, ABC
import numpy as np
from src.common import Function


class Solver(ABC):
    def __init__(self, obj_tol, param_tol, wolfe_const, backtracking_const):
        self.f = None
        self.obj_tol = obj_tol
        self.param_tol = param_tol
        self.wolfe_const = wolfe_const
        self.backtracking_const = backtracking_const
        self.history = None
        self.success = False
        self.is_valid = True

    def solve(self, f: Function, x0, max_iter):
        name = self.__class__.__name__
        print(f"\nSolving {f.name} using {name} solver...")
        self.history = []
        self.f = f
        i = 0
        x = x0
        y = None
        self.success = False
        self.is_valid = True

        while i <= max_iter:
            y, g, h = self.f.eval(x)

            self.history.append(np.append(x, y))
            print(f"[{name}:{i}] x: {x}, y: {y}")

            if self.success:
                break

            p = self.next_direction(x, y, g, h)

            if p is None:
                self.success = False
                self.is_valid = False
                break

            alpha = self.next_step_size(x, p)
            x_next = x + alpha * p

            if np.linalg.norm(x_next - x) < self.param_tol or self.should_terminate(x, x_next, y, g, h, p):
                self.success = True

            x = x_next
            i += 1

        self.history = np.asarray(self.history)
        i -= 0 if self.success else 1

        return name, i, x, y, self.success, self.is_valid

    def next_step_size(self, x, p):
        alpha = 1

        while self.f.y(x + alpha * p) > self.f.y(x) + self.wolfe_const * alpha * self.f.g(x).T @ p:
            alpha *= self.backtracking_const

        return alpha

    @abstractmethod
    def next_direction(self, x, y, g, h):
        pass

    @abstractmethod
    def should_terminate(self, x, x_next, y, g, h, p):
        pass


class GD(Solver):
    def next_direction(self, x, y, g, h):
        return None if g is None else -g

    def should_terminate(self, x, x_next, y, g, h, p):
        return np.linalg.norm(y - self.f.y(x_next)) < self.obj_tol


class Newton(Solver):
    def next_direction(self, x, y, g, h):
        return None if h is None else np.linalg.solve(h, -g)

    def should_terminate(self, x, x_next, y, g, h, p):
        return 0.5 * p.T @ h @ p < self.obj_tol

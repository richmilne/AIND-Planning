clf;
hold on;
axis([-1 55 -5 230])
set(gca, "YTick", 0:10:250)
set(gca, "XTick", 0:5:55)
grid on;

plot(-99,-1, 'ko;1. Breadth-first;')
plot(-98,-1, 'kx;2. Breadth-first Tree;')
plot(-95,-1, 'k+;5. Uniform Cost;')
plot(-94,-1, 'k*;6. Recursive Best-first (Constant Heuristic);')
plot(-92,-1, 'ks;8. A* (Constant Heuristic);')
plot(-91,-1, 'kd;9. A* (Ignore Preconditions Heuristic);')
plot(-90,-1, 'kp;10. A* (Planning Graph LevelSum Heuristic);')

plot(-99,-2, 'b-;Problem 1;')
plot(-99,-2, 'r-;Problem 2;')
plot(-99,-2, 'g-;Problem 3;')

xlabel('Memory (normalised)')
ylabel('Time (normalised)')

plot(2.04761904761905, 11.4235498474259, 'bo')
plot(69.4285714285714, 341.6809236898, 'bx')
plot(2.85714285714286, 13.1379501293463, 'b+')
plot(201.380952380952, 1011.50681444381, 'b*')
plot(2.85714285714286, 15.0759751941572, 'bs')
plot(2.38095238095238, 1, 'bd')
plot(1.33333333333333, 145.273663214676, 'bp')

# Pareto for problem 1 - heuristics 9, 1, 10
pareto = [
    2.38095238095238, 1
    2.04761904761905, 11.4235498474259
    1.33333333333333, 145.273663214676
];
plot(pareto(:, 1), pareto(:, 2), 'b-')

plot(9.36414565826331, 13.4455324108917, 'ro')
plot(14.436974789916, 1.43090943075807, 'r+')
plot(14.436974789916, 1.41826184926772, 'rs')
plot(6.91036414565826, 1, 'rd')
plot(1, 188.647540743656, 'rp')

# Pareto for problem 2 - heuristics 9, 10
pareto = [
    6.91036414565826   1
    1                188.647540743656
];
plot(pareto(:, 1), pareto(:, 2), 'r-')

plot(39.7371273712737, 86.7898342458762, 'go')
plot(50.1626016260163, 3.26602354642761, 'g+')
plot(50.1626016260163, 3.47676755219419, 'gs')
plot(20.0216802168022, 2.02205919914756, 'gd')
plot(1, 220.268373007876, 'gp')

# Pareto for problem 2 - also heuristics 9, 10
pareto = [
    20.0216802168022    2.02205919914756
     1               220.268373007876
];
plot(pareto(:, 1), pareto(:, 2), 'g-')

print -dsvg results-chart.svg
print -dpng results-chart.png
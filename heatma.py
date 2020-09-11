# This import registers the 3D projection, but is otherwise unused.
import numpy
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import

import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np


fig = plt.figure()
ax = fig.gca(projection='3d')

# Make data.
import csv
reader = csv.reader(open('opt_report.csv'))
points = {}
for row in reader:
    points[(float(row[0]), float(row[1]))] = float(row[2])


# This import registers the 3D projection, but is otherwise unused.
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import

import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

n = 100

good_points = [x for x in points.items() if abs(x[1]) < 0.016]

ps, zs = zip(*[x for x in points.items() if abs(x[1]) >= 0.016])
gps, gzs = zip(*good_points)
xs, ys = zip(*ps)
gxs, gys = zip(*gps)

ax.scatter(xs, ys, zs)
ax.scatter(gxs, gys, gzs, color='red')

ax.set_xlabel('holders_to_seekers_ratio')
ax.set_ylabel('prior_ask_probability')
ax.set_zlabel('error')

plt.show()
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import numpy as np

fig = plt.figure()
ax1 = fig.add_subplot(1, 1, 1)

x = []
score = []

def animate(i):
	x.append(i)
	r = np.random.randint(1, 10)
	score.append(i + (r - 5))

	ax1.clear()
	ax1.plot(x, score)

ani = animation.FuncAnimation(fig, animate, interval=100)
plt.show()
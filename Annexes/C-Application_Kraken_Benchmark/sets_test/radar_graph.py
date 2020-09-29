"""
radar_graph.py

the script has been adapted for the needs of Lectaurep. @Lucas Terriel

This script provides from https://python-graph-gallery.com/391-radar-chart-with-several-individuals/
"""


# Libraries
import matplotlib.pyplot as plt
import pandas as pd
from math import pi

# Average of result for dataset



# Set data in dataframe
df = pd.DataFrame({
    'group': ['different_control_set', 'homogeneous_control_set', 'Set_writing_defects', 'Set_material_defects'],
    'CER_AVG (%)': [69.21, 69.68333333, 72.69666667, 72.77666667],
    'WER_AVG (%)': [93.62, 96.16, 96.70333333, 97.45666667],
    'Word_Accuracy_AVG (%)': [6, 3.666666667, 2.666666667, 2.333333333],
    })

# ------- PART 1: Create background

# number of variable
categories = list(df)[1:]
N = len(categories)

# What will be the angle of each axis in the plot? (we divide the plot / number of variable)
angles = [n / float(N) * 2 * pi for n in range(N)]
angles += angles[:1]

# Initialise the spider plot
ax = plt.subplot(111, polar=True)

# If you want the first axis to be on top:
ax.set_theta_offset(pi / 2)
ax.set_theta_direction(-1)

# Draw one axe per variable + add labels labels yet
plt.xticks(angles[:-1], categories)

# Draw ylabels
ax.set_rlabel_position(0)
plt.yticks([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
           ["0","10", "20", "30", "40", "50", "60", "70", "80", "90", "100"],
           color="grey",
           size=7)
plt.ylim(0, 100)

# ------- PART 2: Add plots

# Plot each individual = each line of the data
# I don't do a loop, because plotting more than 3 groups makes the chart unreadable

# Ind1
values = df.loc[0].drop('group').values.flatten().tolist()
values += values[:1]
ax.plot(angles, values, linewidth=1, linestyle='solid', label="different_control_set")
ax.fill(angles, values, 'b', alpha=0.1)

# Ind2
values = df.loc[1].drop('group').values.flatten().tolist()
values += values[:1]
ax.plot(angles, values, linewidth=1, linestyle='solid', label="homogeneous_control_set")
ax.fill(angles, values, 'r', alpha=0.1)

# Ind3
values = df.loc[2].drop('group').values.flatten().tolist()
values += values[:1]
ax.plot(angles, values, linewidth=1, linestyle='solid', label="Set_writing_defects")
ax.fill(angles, values, 'g', alpha=0.1)

# Ind4
values = df.loc[3].drop('group').values.flatten().tolist()
values += values[:1]
ax.plot(angles, values, linewidth=1, linestyle='solid', label="Set_material_defects")
ax.fill(angles, values, 'y', alpha=0.1)

# Add legend
plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))

# Add Title
plt.title('Moyenne des indicateurs WER, CER et Word Accuracy sur 4 sets pour les tests du modèle avec accuracy à 0.8164\n',
          family='serif',
          fontsize=10)

plt.show()
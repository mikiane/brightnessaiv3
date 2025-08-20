import pandas as pd
import matplotlib.pyplot as plt

# Récupération des données des crues de la Seine depuis 50 ans au niveau de Samois-sur-Seine
df = pd.read_csv("https://www.data.gouv.fr/fr/datasets/crues-de-la-seine-a-samois-sur-seine-depuis-1971/csv/crues-de-la-seine-a-samois-sur-seine-depuis-1971.csv")

# Construction du graphique
plt.plot(df["Date"], df["Hauteur"])
plt.title("Crues de la Seine à Samois-sur-Seine depuis 1971")
plt.xlabel("Date")
plt.ylabel("Hauteur (mètres)")
plt.show()
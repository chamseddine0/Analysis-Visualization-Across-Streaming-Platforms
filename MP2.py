import pandas as pd                             # Traitement des données tabulaires
import numpy as np                              # Statistiques et calculs
import matplotlib.pyplot as plt                 # Visualisation simple
import seaborn as sns                           # Visualisation avancée et heatmap
from datetime import datetime                   # Manipulation de dates
import calendar                                 # Noms des jours de la semaine         
import os

## Partie 1 - Préparation & Nettoyage des données 

# Créer le dossier pour les graphiques
os.makedirs('graphiques', exist_ok=True)

# Charger les données 
df = pd.read_csv('visionnage_series.csv')

# 1. Conversion des dates et heures
df['date'] = pd.to_datetime(df['date'])

# Solution robuste pour la conversion de l'heure
def convert_time(time_val):
    if pd.isna(time_val):
        return np.nan
    try:
        return pd.to_datetime(str(time_val).split('+')[0]).hour
    except:
        return int(str(time_val).split(':')[0])

df['heure_arrondie'] = df['heure_debut'].apply(convert_time)

# 2. Extraire le jour de la semaine
df['jour_semaine'] = df['date'].dt.day_name()
jours_fr = {
    'Monday': 'Lundi', 'Tuesday': 'Mardi', 'Wednesday': 'Mercredi',
    'Thursday': 'Jeudi', 'Friday': 'Vendredi', 'Saturday': 'Samedi',
    'Sunday': 'Dimanche'
}
df['jour_semaine'] = df['jour_semaine'].map(jours_fr)

# 3. Gestion des valeurs manquantes et doublons
df = df.dropna().drop_duplicates()

## Partie 2 - Analyse temporelle (Corrigée)

# 1. Répartition par heure
plt.figure(figsize=(10, 6))
sns.countplot(x='heure_arrondie', data=df, color='skyblue')
plt.title('Répartition des sessions par heure')
plt.savefig('graphiques/repartition_heures.png')
plt.close()

# 2. Répartition par jour
ordre_jours = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
plt.figure(figsize=(10, 6))
sns.countplot(x='jour_semaine', data=df, order=ordre_jours, color='lightgreen')
plt.title('Répartition par jour de semaine')
plt.savefig('graphiques/repartition_jours.png')
plt.close()

# 3. Heatmap
heatmap_data = df.groupby(['jour_semaine', 'heure_arrondie']).size().unstack().fillna(0)
heatmap_data = heatmap_data.reindex(ordre_jours)

plt.figure(figsize=(12, 8))
sns.heatmap(heatmap_data, cmap='YlOrRd', annot=True, fmt='g')
plt.title('Heatmap des sessions')
plt.savefig('graphiques/heatmap_jour_heure.png')
plt.close()

## Partie 3 - Analyse qualitative 

# 1. Séries les plus regardées
top_series = df.groupby(['plateforme', 'série']).size().reset_index(name='count')
top_series = top_series.loc[top_series.groupby('plateforme')['count'].idxmax()]

# 2. Genres dominants
top_genres = df.groupby(['plateforme', 'genre']).size().reset_index(name='count')
top_genres = top_genres.loc[top_genres.groupby('plateforme')['count'].idxmax()]

# 3. Durée moyenne par genre 
plt.figure(figsize=(12, 6))
sns.barplot(x='genre', y='durée', hue='genre', data=df, 
            estimator=np.mean, palette='viridis', legend=False)
plt.title('Durée moyenne par genre')
plt.xticks(rotation=45)
plt.savefig('graphiques/duree_moyenne_genre.png')
plt.close()

# Diagramme circulaire
plt.figure(figsize=(8, 8))
df['genre'].value_counts().plot.pie(autopct='%1.1f%%')
plt.title('Répartition des genres')
plt.savefig('graphiques/repartition_genres.png')
plt.close()

## Partie 4 - Comparaison inter-plateformes 

# 1. Visionnage le soir
soir = df[df['heure_arrondie'].between(18, 23)]
temps_soir = soir.groupby('plateforme')['durée'].mean().reset_index()

plt.figure(figsize=(10, 6))
sns.barplot(x='plateforme', y='durée', data=temps_soir)
plt.title('Durée moyenne le soir (18h-23h)')
plt.savefig('graphiques/duree_soir.png')
plt.close()

# 2. Sessions longues
longues = df[df['durée'] > 60].groupby('plateforme').size().reset_index(name='count')

plt.figure(figsize=(10, 6))
sns.barplot(x='plateforme', y='count', data=longues)
plt.title('Sessions longues (>60 min)')
plt.savefig('graphiques/sessions_longues.png')
plt.close()

# 3. Comparaison semaine/week-end
df['type_jour'] = df['jour_semaine'].apply(lambda x: 'Week-end' if x in ['Samedi', 'Dimanche'] else 'Semaine')
comparaison = df.groupby(['plateforme', 'type_jour'])['durée'].mean().unstack()

comparaison.plot(kind='bar', figsize=(10, 6))
plt.title('Durée moyenne: semaine vs week-end')
plt.savefig('graphiques/comparaison_semaine_weekend.png')
plt.close()

## Partie 5 - Export et synthèse

# Graphiques supplémentaires
df.groupby('plateforme')['durée'].sum().plot.bar(figsize=(10, 6))
plt.title('Durée totale par plateforme')
plt.savefig('graphiques/duree_totale.png')
plt.close()

df.groupby('plateforme')['durée'].mean().plot.bar(figsize=(10, 6))
plt.title('Durée moyenne par plateforme')
plt.savefig('graphiques/duree_moyenne_plateforme.png')
plt.close()

# Sauvegarde des résultats
resultats = pd.concat([
    top_series.assign(analyse='Série la plus regardée'),
    top_genres.assign(analyse='Genre dominant'),
    temps_soir.assign(analyse='Durée moyenne soir'),
    longues.assign(analyse='Sessions longues')
])

resultats.to_csv('resultats_analyse.csv', index=False)

print("Analyse terminée avec succès!") 
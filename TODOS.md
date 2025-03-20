# Les Tâches (Backend)
- [x] Création de compte
- [x] Conxion à son compte
- [x] Reinitiliser son mot de passe
- [x] Changer son mot de passe
- [ ] Ecrire les tests unitaire pour chaque EndPoint.
  - [x] Tester la création de compte
  - [x] Valider le compte (email)
  - [x] Tester la connexion (login)
  - [x] Tester le changement du mot de passe
  - [x] Tester la modofication des information de profil
  - [x] Tester le mot de passe Oublié
  - [ ] Tester la création d'activité
  - [ ] Tester la recuperation des activités (avec les stats)
- [x] Mettre à jour ses informations de profile
- [ ] Créer une activité
  - [x] Recuperation de Images (Upload)
  - [x] Obtenir les resultats
  - [x] Sauvegarder l'activité
  - [x] Exposer l'Endpoint
  - [ ] Interoger le model avec ces Images
- [x] Voir les resultats d'une activité
- [x] Voir l'historique de ses activité
  
# Frontend
- [x] Login  ok
- [x] Register OK
- [x] Update profile
- [x] Change password
- [x] Reset password
- [x ] Create an activity
- [X] Voir les results d'une activity
- [x] Voir l'historique des ses activté
  
## Notes
- [x] Gérer les tokens autrement (Bearer Authentication)
- [x] Déplacer les thmplate de mail sur des .html (Se servir de Jinja2 pour les rendre)
- [x] deconn apres le update password
- [x] Finir avec les config mail sending (Recours à des srtvices tiers)
- [x] Revoir le Flow de création de compte (Validation de compte pour eviter les spams)
- [ ] Retravailler les messages d'error (Register tel inval : register, compte non validé: login...)
- [x] L'upload de fichier ne prend pas plus d'un certain nombre de fichier (> 5)
- [ ] Au premier lancement de l'app, il arrive pas creer les tables
- [ ] Quand on se connecte (la redirect sur le dashbord est pas immediate au niveau du front)
- [ ] Apres l'upload sur create_activity sur Front
- [x] Lier le loader sur le dashboard à celle de la req au niveau front.
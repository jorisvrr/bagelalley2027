# Gearchiveerd: admin-dashboard

Het admin-dashboard (`admin.html`) is gearchiveerd omdat het nu niet wordt gebruikt.
De code staat er nog, maar is uitgeschakeld:

- Elke `/admin`-URL geeft een 404, zolang `ADMIN_ENABLED` niet aan staat.
- Er is geen standaardwachtwoord: zonder `ADMIN_PASS` kan niemand inloggen.
- Het dashboard staat niet in `robots.txt` of de sitemap.

## Weer aanzetten

Op Railway, onder Variables:

```
ADMIN_ENABLED=1
ADMIN_PASS=<nieuw, sterk wachtwoord>
SECRET_KEY=<lange willekeurige string>
```

Gebruik niet het oude wachtwoord: dat staat in de git-historie.
Het dashboard heeft alleen zin als online reserveren ook aan staat (`ONLINE_RESERVEREN=1`).

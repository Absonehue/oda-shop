from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'oda_shop_secret_key'

# --- CONFIGURATION BASE DE DONNÉES ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'odashop.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class ClientRDV(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    parfum = db.Column(db.String(100))
    date_enregistrement = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

PARFUMS_DATA = [
    {"id": 1, "nom": "Bois d'Argent", "image": "bois_dargent.jpg", "prix": 5000, "desc": "Un sillage boisé iconique."},
    {"id": 2, "nom": "Intense", "image": "intense.png", "prix": 5000, "desc": "Une fragrance profonde."},
    {"id": 3, "nom": "Addict", "image": "addict.png", "prix": 5000, "desc": "Une essence captivante."},
    {"id": 4, "nom": "Chanel", "image": "chanel.jpg", "prix": 5000, "desc": "L'élégance intemporelle."},
    {"id": 5, "nom": "Coco Vanille", "image": "coco vanille.jpg", "prix": 5000, "desc": "Douceur exotique."},
    {"id": 6, "nom": "Fuel For Life", "image": "fuel for life.png", "prix": 5000, "desc": "Un concentré d'énergie."},
    {"id": 7, "nom": "L'immensité", "image": "l'immensité.png", "prix": 5000, "desc": "Un voyage sensoriel."},
    {"id": 8, "nom": "Lacoste Rouge", "image": "lacoste rouge.png", "prix": 5000, "desc": "Énergie pure."},
    {"id": 9, "nom": "Pure XS", "image": "pure xs.jpg", "prix": 5000, "desc": "Magnétique et brûlant."},
    {"id": 10, "nom": "Scandal", "image": "scandal.png", "prix": 5000, "desc": "Une aura gourmande."},
    {"id": 11, "nom": "Sculpture", "image": "sculpture.png", "prix": 5000, "desc": "Classique frais."},
    {"id": 12, "nom": "The One H", "image": "the one H.png", "prix": 5000, "desc": "Le charisme absolu."},
    {"id": 13, "nom": "Ultra Male", "image": "ultra male.png", "prix": 5000, "desc": "Puissant et séducteur."}
]

@app.template_filter('format_prix')
def format_prix(value):
    return "{:,.0f} FCFA".format(value).replace(',', ' ')

# --- ROUTES ---

@app.route('/')
def index():
    if 'panier' not in session:
        session['panier'] = {}
    nb_articles = sum(session['panier'].values())
    return render_template('index.html', parfums=PARFUMS_DATA, nb_articles=nb_articles)

@app.route('/ajouter_au_panier/<int:id_produit>')
def ajouter_au_panier(id_produit):
    if 'panier' not in session: session['panier'] = {}
    panier = session['panier']
    id_s = str(id_produit)
    panier[id_s] = panier.get(id_s, 0) + 1
    session['panier'] = panier
    session.modified = True
    
    nb_articles = sum(session['panier'].values())
    return jsonify({"status": "success", "nb_articles": nb_articles})

@app.route('/rdv', methods=['POST'])
def prendre_rdv():
    nom = request.form.get('nom')
    email = request.form.get('email')
    parfum = request.form.get('parfum')
    
    nouveau_rdv = ClientRDV(nom=nom, email=email, parfum=parfum)
    db.session.add(nouveau_rdv)
    db.session.commit()
    
    flash("Votre demande de rendez-vous a été enregistrée !")
    return redirect(url_for('index'))

@app.route('/panier')
def afficher_panier():
    panier_session = session.get('panier', {})
    produits_panier = []
    total_general = 0
    
    for id_s, qte in panier_session.items():
        for p in PARFUMS_DATA:
            if p['id'] == int(id_s):
                item = p.copy()
                item['quantite'] = qte
                item['sous_total'] = p['prix'] * qte
                produits_panier.append(item)
                total_general += item['sous_total']
    
    # AJOUT : On calcule nb_articles pour que le header reste à jour sur la page panier
    nb_articles = sum(panier_session.values())
                
    return render_template('panier.html', produits=produits_panier, total=total_general, nb_articles=nb_articles)

@app.route('/retirer_produit/<int:id_produit>')
def retirer_produit(id_produit):
    panier = session.get('panier', {})
    id_s = str(id_produit)
    if id_s in panier:
        del panier[id_s]
        session['panier'] = panier
        session.modified = True
    return redirect(url_for('afficher_panier'))

# AJOUT : Route pour vider totalement le panier
@app.route('/vider_panier')
def vider_panier():
    session['panier'] = {}
    session.modified = True
    return redirect(url_for('afficher_panier'))

if __name__ == '__main__':
    app.run()
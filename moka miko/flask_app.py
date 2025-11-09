from flask import Flask, request, jsonify, render_template
import json
import numpy as np
import faiss
import torch
import os
from langdetect import detect
from transformers import AutoTokenizer, AutoModel
from groq import Groq
import os
from dotenv import load_dotenv


app = Flask(__name__)

class ChatbotRH:
    def __init__(self, json_path, groq_api_key):
        """Initialise le système RAG avec FAISS et le modèle Groq."""
        self.data_store = []
        self.index = faiss.IndexFlatL2(384)  # 384 dimensions pour MiniLM

        # Modèle de vectorisation de texte
        self.text_tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        self.text_model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

        # Client Groq
        self.groq_client = Groq(api_key=groq_api_key)

        # Charger et indexer les données JSON
        self.load_json_data(json_path)

    def load_json_data(self, json_path):
        """Charge les données JSON et les indexe dans FAISS"""
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for entry in data:
            # Créer un texte combiné pour la recherche
            combined_text = f"{entry.get('question', '')} {entry.get('answer', '')} {' '.join(entry.get('paraphrases', []))}"
            
            if not combined_text.strip():
                continue  # Ignorer les entrées vides
            
            text_embedding = self._vectorize_text(combined_text)

            # Stocker les données
            self.data_store.append({
                "category": entry.get("category", ""),
                "subcategory": entry.get("subcategory", ""),
                "question": entry.get("question", ""),
                "answer": entry.get("answer", ""),
                "paraphrases": entry.get("paraphrases", []),
                "combined_text": combined_text
            })

            # Ajouter l'embedding à FAISS
            self.index.add(np.array([text_embedding]))

    def _vectorize_text(self, text):
        """Convertit un texte en vecteur"""
        inputs = self.text_tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.text_model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).numpy().flatten()

    def detect_language(self, text):
        """Détecte la langue de la question (français ou anglais)"""
        try:
            lang = detect(text)
            return "fr" if lang == "fr" else "en"
        except:
            return "fr"  # Par défaut, répondre en français pour les RH

    def query(self, question, k=3):
        """Recherche dans FAISS et génère une réponse avec Groq"""
        query_embedding = self._vectorize_text(question)

        # Recherche des k meilleurs résultats
        distances, indices = self.index.search(np.array([query_embedding]), k)

        # Vérifier si des résultats sont retournés
        valid_indices = [i for i in indices[0] if i >= 0 and i < len(self.data_store)]
        if not valid_indices:
            return "Désolé, je n'ai pas trouvé d'information pertinente dans ma base de connaissances RH. Pouvez-vous reformuler votre question ?"

        # Construire un contexte détaillé
        context_entries = []
        for i in valid_indices:
            entry = self.data_store[i]
            context_entries.append(f"""
Catégorie: {entry['category']} - {entry['subcategory']}
Question: {entry['question']}
Réponse: {entry['answer']}
""")
        
        context = "\n".join(context_entries)

        # Détection de la langue de la question
        lang = self.detect_language(question)

        # Créer le prompt adapté à la langue
        if lang == "fr":
            system_prompt = """Vous êtes un assistant RH expert et bienveillant. Votre rôle est d'aider les employés avec leurs questions relatives aux ressources humaines.

Instructions:
- Répondez de manière claire, précise et professionnelle
- Utilisez les informations du contexte fourni pour donner des réponses exactes
- Si l'information n'est pas dans le contexte, dites-le clairement
- Soyez empathique et serviable
- Répondez en français

Contexte RH disponible:
{context}

Question de l'employé: {question}

Réponse:"""
        else:
            system_prompt = """You are an expert and helpful HR assistant. Your role is to help employees with their human resources questions.

Instructions:
- Answer clearly, precisely and professionally
- Use the information from the provided context to give accurate answers
- If the information is not in the context, state it clearly
- Be empathetic and helpful
- Respond in English

Available HR context:
{context}

Employee question: {question}

Answer:"""

        try:
            # Appel à l'API Groq
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "Vous êtes un assistant RH expert et bienveillant." if lang == "fr" else "You are an expert and helpful HR assistant."
                    },
                    {
                        "role": "user",
                        "content": system_prompt.format(context=context, question=question)
                    }
                ],
               model="llama-3.1-8b-instant",
                temperature=0.3,
                max_tokens=1024,
            )
            
            response = chat_completion.choices[0].message.content

            # Ajouter les sources utilisées
            sources_info = "\n\n📚 **Sources consultées:**\n"
            for i, idx in enumerate(valid_indices):
                entry = self.data_store[idx]
                sources_info += f"• {entry['category']} - {entry['subcategory']}\n"
            
            response += sources_info
            
            return response

        except Exception as e:
            return f"Erreur lors de la génération de la réponse: {str(e)}"

# Variables globales
chatbot = None

def initialize_chatbot():
    """Initialise le chatbot au démarrage de l'application"""
    global chatbot
   # Charger les variables d'environnement à partir d'un fichier .env
load_dotenv()

# Configuration
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
JSON_PATH = "data.json"

# Vérifier que la clé d'API a bien été chargée
if not GROQ_API_KEY:
    raise ValueError("La clé d'API GROQ_API_KEY n'a pas été trouvée. Veuillez la définir dans un fichier .env")
    
    # Vérifier que le fichier existe
    if not os.path.exists(JSON_PATH):
        raise FileNotFoundError(f"Le fichier {JSON_PATH} n'existe pas. Assurez-vous qu'il est dans le même répertoire que l'application.")
    
    print("🚀 Initialisation du chatbot RH...")
    chatbot = ChatbotRH(JSON_PATH, GROQ_API_KEY)
    print("✅ Chatbot RH initialisé avec succès!")

# Configuration Flask pour les templates
app.template_folder = 'templates'

# Routes Flask
@app.route('/')
def home():
    """Page d'accueil avec interface chat ESPRIT"""
    return render_template('index.html')

@app.route('/api/ask', methods=['POST'])
def ask_question():
    """API endpoint pour poser une question au chatbot"""
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({
                'success': False,
                'error': 'Question manquante dans la requête'
            }), 400
        
        question = data['question'].strip()
        
        if not question:
            return jsonify({
                'success': False,
                'error': 'La question ne peut pas être vide'
            }), 400
        
        if chatbot is None:
            return jsonify({
                'success': False,
                'error': 'Chatbot non initialisé'
            }), 500
        
        # Générer la réponse
        response = chatbot.query(question)
        
        return jsonify({
            'success': True,
            'response': response,
            'question': question
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur interne: {str(e)}'
        }), 500

@app.route('/api/status')
def status():
    """Vérifier le statut du chatbot"""
    return jsonify({
        'status': 'active' if chatbot is not None else 'inactive',
        'data_count': len(chatbot.data_store) if chatbot else 0
    })

@app.route('/api/test')
def test():
    """Endpoint de test"""
    test_questions = [
        "Comment récupérer ma fiche de paie ?",
        "Quand est-ce que je suis payé ?",
        "Comment poser des congés ?"
    ]
    
    results = []
    for question in test_questions:
        if chatbot:
            response = chatbot.query(question)
            results.append({
                'question': question,
                'response': response[:200] + '...' if len(response) > 200 else response
            })
    
    return jsonify({
        'test_results': results,
        'chatbot_status': 'active' if chatbot else 'inactive'
    })

# Gestion des erreurs
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint non trouvé'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Erreur interne du serveur'}), 500

if __name__ == '__main__':
    try:
        # Initialiser le chatbot au démarrage
        initialize_chatbot()
        
        # Lancer l'application Flask
        print("🌐 Démarrage de l'application Flask...")
        print("📱 Interface web disponible sur: http://localhost:5000")
        print("🔗 API disponible sur: http://localhost:5000/api/ask")
        print("❌ Arrêt avec Ctrl+C")
        
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except FileNotFoundError as e:
        print(f"❌ Erreur: {e}")
        print("📁 Assurez-vous que le fichier 'data.json' est présent dans le répertoire.")
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")
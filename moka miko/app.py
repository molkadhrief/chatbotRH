import json
import numpy as np
import faiss
import torch
import os
from langdetect import detect
from transformers import AutoTokenizer, AutoModel
from groq import Groq

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
                model="llama3-8b-8192",  # ou "mixtral-8x7b-32768" selon vos préférences
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

    def chat_interactive(self):
        """Mode chat interactif"""
        print("🤖 Chatbot RH - Tapez 'quit' pour quitter")
        print("=" * 50)
        
        while True:
            question = input("\n👤 Votre question RH: ").strip()
            
            if question.lower() in ['quit', 'exit', 'quitter']:
                print("👋 Au revoir ! N'hésitez pas à revenir si vous avez d'autres questions RH.")
                break
            
            if not question:
                continue
                
            print("\n🤖 Réponse:")
            response = self.query(question)
            print(response)
            print("-" * 50)


# === Exemple d'utilisation ===
if __name__ == "__main__":
   
    
    # Initialiser le chatbot
    chatbot = ChatbotRH("data.json", GROQ_API_KEY)
    
    # Test avec quelques questions
    print("🧪 Tests du chatbot RH:")
    print("=" * 50)
    
    questions_test = [
        "Comment récupérer ma fiche de paie ?",
        "Quand est-ce que je suis payé ?",
        "Comment poser des congés ?",
        "Quel est le remboursement pour les lunettes ?",
        "How can I check my leave balance?"
    ]
    
    for question in questions_test:
        print(f"\n❓ Question: {question}")
        response = chatbot.query(question)
        print(f"🤖 Réponse: {response}")
        print("-" * 50)
    
    # Lancer le mode interactif (décommentez si souhaité)
    # chatbot.chat_interactive()
    
    
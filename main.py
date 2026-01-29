import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

class TalentAgentSystem:
    def __init__(self):
        # LLM Orchestratore
        self.llm = ChatGroq(model_name="llama-3.1-8b-instant", temperature=0.1)
        # Embeddings locali (Gratis)
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vector_db_path = "faiss_talent_index"
        self.vector_db = None
        
        # CARICAMENTO MEMORIA PERSISTENTE
        if os.path.exists(self.vector_db_path):
            print("[*] Caricamento memoria competenze esistente...")
            try:
                self.vector_db = FAISS.load_local(self.vector_db_path, self.embeddings, allow_dangerous_deserialization=True)
            except Exception as e:
                print(f"Errore caricamento database: {e}")

    def agente_parser(self, file_path):
        """Estrae dati dai PDF e aggiorna il database."""
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        splits = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100).split_documents(docs)
        
        if self.vector_db is None:
            self.vector_db = FAISS.from_documents(splits, self.embeddings)
        else:
            self.vector_db.add_documents(splits)
            
        self.vector_db.save_local(self.vector_db_path)
        return f"Documento {os.path.basename(file_path)} indicizzato."

    def agente_scout(self, query):
        """Cerca i frammenti più rilevanti."""
        if not self.vector_db: return "Non ho ancora letto documenti."
        docs = self.vector_db.similarity_search(query, k=3)
        return "\n---\n".join([d.page_content for d in docs])

    def agente_critic(self, query, contesti):
        """Genera risposta validata."""
        prompt = f"Basati su questi documenti:\n{contesti}\n\nDomanda: {query}\nRispondi in italiano citando i nomi se presenti."
        return self.llm.invoke(prompt).content

    def esegui_ricerca(self, domanda):
        """Ponte per la chat."""
        contesto = self.agente_scout(domanda)
        return self.agente_critic(domanda, contesto)

import os
import sqlite3
import asyncio
from core.event_bus import EventBus
from core.logger import arya_logger

try:
    import PyPDF2  # Lightweight PDF text extraction
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

class MedicalAssistantRAG:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.db_path = "memory_system/user_memory.db"
        self.pdf_directory = "/storage/emulated/0/Documents/MBBS"
        
        self._init_db()
        
        self.event_bus.subscribe("knowledge.rag.index", self.index_pdfs)
        self.event_bus.subscribe("knowledge.rag.query", self.query_medical_knowledge)
        
        if HAS_PDF:
            self.logger.info("Medical Assistant RAG initialized. I am ready to be your personal medical encyclopedia, Sir.")
        else:
            self.logger.warning("PyPDF2 not found. Medical RAG is disabled, Sir.")

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # A simple table to store extracted text chunks for keyword searching
        # In a full RAG, this would store vector embeddings (e.g., using Chroma or FAISS)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS medical_knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_name TEXT,
                page_number INTEGER,
                content TEXT
            )
        ''')
        conn.commit()
        conn.close()

    async def index_pdfs(self, data: dict = None):
        if not HAS_PDF:
            self.logger.error("PyPDF2 is not installed. Cannot index PDFs.")
            await self.event_bus.publish("speak", {"text": "I lack the PDF library to read your textbooks, Sir."})
            return

        if not os.path.exists(self.pdf_directory):
            self.logger.warning(f"PDF directory {self.pdf_directory} does not exist.")
            return

        self.logger.info(f"Starting to index medical PDFs in {self.pdf_directory}...")
        await self.event_bus.publish("speak", {"text": "Indexing your medical textbooks, Sir. This might take a while, as there are a lot of big words."})
        
        # Run heavy extraction in a thread
        await asyncio.to_thread(self._extract_and_store_sync)
        
        await self.event_bus.publish("speak", {"text": "Indexing complete. I am now significantly smarter than I was five minutes ago."})

    def _extract_and_store_sync(self):
        if not HAS_PDF: return
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear old index to prevent duplicates for this simple implementation
        cursor.execute("DELETE FROM medical_knowledge")
        
        for filename in os.listdir(self.pdf_directory):
            if filename.lower().endswith(".pdf"):
                filepath = os.path.join(self.pdf_directory, filename)
                try:
                    with open(filepath, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        for page_num in range(len(reader.pages)):
                            page = reader.pages[page_num]
                            text = page.extract_text().strip()
                            if text:
                                # Store chunks (here, page by page)
                                cursor.execute('''
                                    INSERT INTO medical_knowledge (document_name, page_number, content)
                                    VALUES (?, ?, ?)
                                ''', (filename, page_num + 1, text))
                    self.logger.debug(f"Indexed {filename}")
                except Exception as e:
                    self.logger.error(f"Failed to index {filename}: {e}")
                    
        conn.commit()
        conn.close()

    async def query_medical_knowledge(self, data: dict):
        query = data.get("query", "").lower()
        if not query:
            return

        self.logger.info(f"Querying medical RAG for: {query}")
        await self.event_bus.publish("speak", {"text": f"Consulting your medical texts for '{query}', Sir."})
        
        results = await asyncio.to_thread(self._search_db_sync, query)
        
        if results:
            # Get the best match (first result)
            doc_name, page, content = results[0]
            snippet = content[:200].replace('\n', ' ') + "..."
            
            response = f"According to {doc_name}, page {page}: {snippet}"
            self.logger.info(f"RAG Match found in {doc_name} pg {page}")
            await self.event_bus.publish("speak", {"text": response})
            
            # Publish full result for UI or further LLM processing
            await self.event_bus.publish("knowledge.rag.result", {"query": query, "results": results})
        else:
            await self.event_bus.publish("speak", {"text": "I could not find any reference to that in your indexed textbooks, Sir. Perhaps you should consult a real doctor."})

    def _search_db_sync(self, query: str) -> list:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Simple keyword search. 
        # For a true RAG, we would embed the query and do a cosine similarity search against the DB.
        # This SQLite LIKE query is a lightweight mobile-friendly placeholder.
        keywords = query.split()
        sql_query = "SELECT document_name, page_number, content FROM medical_knowledge WHERE "
        sql_query += " AND ".join(["content LIKE ?" for _ in keywords])
        sql_query += " LIMIT 3"
        
        params = [f"%{kw}%" for kw in keywords]
        
        cursor.execute(sql_query, params)
        results = cursor.fetchall()
        conn.close()
        
        return results

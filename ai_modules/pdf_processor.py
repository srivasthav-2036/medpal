import os
from PyPDF2 import PdfReader
import pdfplumber
import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.schema import Document
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PDFProcessor:
    def __init__(self):
        # Configure Gemini
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.vector_store_path = "vector_stores/faiss_index"
    
    def get_pdf_text(self, pdf_files):
        """Extract text from PDF files using multiple methods for better accuracy"""
        all_text = ""
        
        for file_info in pdf_files:
            if file_info['type'] == 'pdf':
                filepath = file_info['filepath']
                filename = file_info['original_name']
                print(f"Processing PDF: {filename}")
                
                text = self._extract_text_multiple_methods(filepath, filename)
                if text:
                    all_text += f"\n\n--- Document: {filename} ---\n\n{text}\n"
                else:
                    print(f"Warning: Could not extract text from {filename}")
        
        return all_text
    
    def _extract_text_multiple_methods(self, filepath, filename):
        """Try multiple PDF text extraction methods"""
        text = ""
        
        # Method 1: pdfplumber
        try:
            with pdfplumber.open(filepath) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
            if text.strip():
                print(f"Successfully extracted text using pdfplumber from {filename}")
                return text
        except:
            pass
        
        # Method 2: PyMuPDF
        try:
            doc = fitz.open(filepath)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                if page_text:
                    text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
            doc.close()
            if text.strip():
                print(f"Successfully extracted text using PyMuPDF from {filename}")
                return text
        except:
            pass
        
        # Method 3: PyPDF2
        try:
            pdf_reader = PdfReader(filepath)
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
            if text.strip():
                print(f"Successfully extracted text using PyPDF2 from {filename}")
                return text
        except:
            pass
        
        return text
    
    def get_text_chunks(self, text):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=10000,
            chunk_overlap=1000
        )
        chunks = text_splitter.split_text(text)
        return chunks
    
    def get_vector_store(self, text_chunks):
        """Create vector store with HuggingFace embeddings"""
        try:
            print("Creating vector store with Hugging Face embeddings...")
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            
            vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
            vector_store.save_local(self.vector_store_path)
            print("Vector store created successfully")
            return vector_store
        
        except Exception as e:
            print(f"HuggingFace Embeddings failed: {e}")
            print("Falling back to FakeEmbeddings...")
            from langchain_community.embeddings import FakeEmbeddings
            fake_emb = FakeEmbeddings(size=384)
            vector_store = FAISS.from_texts(text_chunks, embedding=fake_emb)
            vector_store.save_local(self.vector_store_path)
            return vector_store
    
    def get_conversational_chain(self):
        """Modern QA chain replacing load_qa_chain"""
        
        prompt_template = """
        You are a medical assistant.
        Answer ONLY using the context below.
        If the information is not present, say: "I DONT KNOW".

        Context:
        {context}

        Question:
        {question}

        Answer:
        """

        model = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.3
        )

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )

        chain = create_stuff_documents_chain(
            llm=model,
            prompt=prompt
        )

        return chain
    
    def process_pdfs(self, uploaded_files):
        pdf_files = [f for f in uploaded_files if f['type'] == 'pdf']
        
        if not pdf_files:
            return "No PDF files found"
        
        try:
            raw_text = self.get_pdf_text(pdf_files)
            
            if not raw_text.strip():
                return "No text extracted from PDFs"
            
            cleaned_text = self._clean_text(raw_text)
            text_chunks = self.get_text_chunks(cleaned_text)
            
            if not text_chunks:
                return "No text chunks could be created"
            
            self.get_vector_store(text_chunks)
            return f"Processed {len(pdf_files)} PDF(s) successfully."
        
        except Exception as e:
            return f"Error processing PDFs: {e}"
    
    def _clean_text(self, text):
        import re
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'--- Page \d+ ---', '', text)
        text = re.sub(r'--- Document: .+? ---', '', text)
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}\"\'\/\@\#\$\%\&\*\+\=\<\>\~\`\|]', '', text)
        return text.strip()
    
    def answer_question(self, user_question):
        try:
            if not os.path.exists(self.vector_store_path):
                return "Please upload and process PDF files first"
            
            try:
                embeddings = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2",
                    model_kwargs={'device': 'cpu'},
                    encode_kwargs={'normalize_embeddings': True}
                )
                new_db = FAISS.load_local(
                    self.vector_store_path,
                    embeddings,
                    allow_dangerous_deserialization=True
                )
            except:
                from langchain_community.embeddings import FakeEmbeddings
                fake_embeddings = FakeEmbeddings(size=384)
                new_db = FAISS.load_local(
                    self.vector_store_path,
                    fake_embeddings,
                    allow_dangerous_deserialization=True
                )
            
            docs = new_db.similarity_search(user_question)

            # 🔧 FIX: Convert strings → Document objects
            if docs and isinstance(docs[0], str):
                docs = [Document(page_content=d) for d in docs]

            chain = self.get_conversational_chain()

            response = chain.invoke({
                "context": docs,
                "question": user_question
            })

            return response
        
        except Exception as e:
            return f"Error answering question: {e}"
# import os
# from PyPDF2 import PdfReader
# import pdfplumber
# import fitz  # PyMuPDF
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_huggingface import HuggingFaceEmbeddings
# import google.generativeai as genai
# from langchain_community.vectorstores import FAISS
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_core.prompts import PromptTemplate
# from langchain.chains.combine_documents import create_stuff_documents_chain
# from langchain.schema import Document
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# class PDFProcessor:
#     def __init__(self):
#         # Configure Gemini
#         api_key = os.getenv('GOOGLE_API_KEY')
#         if not api_key:
#             raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
#         genai.configure(api_key=api_key)
#         self.vector_store_path = "vector_stores/faiss_index"
    
#     def get_pdf_text(self, pdf_files):
#         """Extract text from PDF files using multiple methods for better accuracy"""
#         all_text = ""
        
#         for file_info in pdf_files:
#             if file_info['type'] == 'pdf':
#                 filepath = file_info['filepath']
#                 filename = file_info['original_name']
#                 print(f"Processing PDF: {filename}")
                
#                 text = self._extract_text_multiple_methods(filepath, filename)
#                 if text:
#                     all_text += f"\n\n--- Document: {filename} ---\n\n{text}\n"
#                 else:
#                     print(f"Warning: Could not extract text from {filename}")
        
#         return all_text
    
#     def _extract_text_multiple_methods(self, filepath, filename):
#         """Try multiple PDF text extraction methods"""
#         text = ""
        
#         # Method 1: pdfplumber
#         try:
#             with pdfplumber.open(filepath) as pdf:
#                 for page_num, page in enumerate(pdf.pages):
#                     page_text = page.extract_text()
#                     if page_text:
#                         text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
#             if text.strip():
#                 print(f"Successfully extracted text using pdfplumber from {filename}")
#                 return text
#         except:
#             pass
        
#         # Method 2: PyMuPDF
#         try:
#             doc = fitz.open(filepath)
#             for page_num in range(len(doc)):
#                 page = doc.load_page(page_num)
#                 page_text = page.get_text()
#                 if page_text:
#                     text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
#             doc.close()
#             if text.strip():
#                 print(f"Successfully extracted text using PyMuPDF from {filename}")
#                 return text
#         except:
#             pass
        
#         # Method 3: PyPDF2
#         try:
#             pdf_reader = PdfReader(filepath)
#             for page_num, page in enumerate(pdf_reader.pages):
#                 page_text = page.extract_text()
#                 if page_text:
#                     text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
#             if text.strip():
#                 print(f"Successfully extracted text using PyPDF2 from {filename}")
#                 return text
#         except:
#             pass
        
#         return text
    
#     def get_text_chunks(self, text):
#         text_splitter = RecursiveCharacterTextSplitter(
#             chunk_size=10000,
#             chunk_overlap=1000
#         )
#         chunks = text_splitter.split_text(text)
#         return chunks
    
#     def get_vector_store(self, text_chunks):
#         """Create vector store with HuggingFace embeddings"""
#         try:
#             print("Creating vector store with Hugging Face embeddings...")
#             embeddings = HuggingFaceEmbeddings(
#                 model_name="sentence-transformers/all-MiniLM-L6-v2",
#                 model_kwargs={'device': 'cpu'},
#                 encode_kwargs={'normalize_embeddings': True}
#             )
            
#             vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
#             vector_store.save_local(self.vector_store_path)
#             print("Vector store created successfully")
#             return vector_store
        
#         except Exception as e:
#             print(f"HuggingFace Embeddings failed: {e}")
#             print("Falling back to FakeEmbeddings...")
#             from langchain_community.embeddings import FakeEmbeddings
#             fake_emb = FakeEmbeddings(size=384)
#             vector_store = FAISS.from_texts(text_chunks, embedding=fake_emb)
#             vector_store.save_local(self.vector_store_path)
#             return vector_store
    
#     def get_conversational_chain(self):
#         """Modern QA chain replacing load_qa_chain"""
        
#         prompt_template = """
#         You are a medical assistant.
#         Answer ONLY using the context below.
#         If the information is not present, say: "I DONT KNOW".

#         Context:
#         {context}

#         Question:
#         {question}

#         Answer:
#         """

#         model = ChatGoogleGenerativeAI(
#             model="gemini-2.0-flash",
#             temperature=0.3
#         )

#         prompt = PromptTemplate(
#             template=prompt_template,
#             input_variables=["context", "question"]
#         )

#         chain = create_stuff_documents_chain(
#             llm=model,
#             prompt=prompt
#         )

#         return chain
    
#     def process_pdfs(self, uploaded_files):
#         pdf_files = [f for f in uploaded_files if f['type'] == 'pdf']
        
#         if not pdf_files:
#             return "No PDF files found"
        
#         try:
#             raw_text = self.get_pdf_text(pdf_files)
            
#             if not raw_text.strip():
#                 return "No text extracted from PDFs"
            
#             cleaned_text = self._clean_text(raw_text)
#             text_chunks = self.get_text_chunks(cleaned_text)
            
#             if not text_chunks:
#                 return "No text chunks could be created"
            
#             self.get_vector_store(text_chunks)
#             return f"Processed {len(pdf_files)} PDF(s) successfully."
        
#         except Exception as e:
#             return f"Error processing PDFs: {e}"
    
#     def _clean_text(self, text):
#         import re
#         text = re.sub(r'\s+', ' ', text)
#         text = re.sub(r'--- Page \d+ ---', '', text)
#         text = re.sub(r'--- Document: .+? ---', '', text)
#         text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}\"\'\/\@\#\$\%\&\*\+\=\<\>\~\`\|]', '', text)
#         return text.strip()
    
#     def answer_question(self, user_question):
#         try:
#             if not os.path.exists(self.vector_store_path):
#                 return "Please upload and process PDF files first"
            
#             try:
#                 embeddings = HuggingFaceEmbeddings(
#                     model_name="sentence-transformers/all-MiniLM-L6-v2",
#                     model_kwargs={'device': 'cpu'},
#                     encode_kwargs={'normalize_embeddings': True}
#                 )
#                 new_db = FAISS.load_local(
#                     self.vector_store_path,
#                     embeddings,
#                     allow_dangerous_deserialization=True
#                 )
#             except:
#                 from langchain_community.embeddings import FakeEmbeddings
#                 fake_embeddings = FakeEmbeddings(size=384)
#                 new_db = FAISS.load_local(
#                     self.vector_store_path,
#                     fake_embeddings,
#                     allow_dangerous_deserialization=True
#                 )
            
#             docs = new_db.similarity_search(user_question)

#             # 🔧 FIX: Convert strings → Document objects
#             if docs and isinstance(docs[0], str):
#                 docs = [Document(page_content=d) for d in docs]

#             chain = self.get_conversational_chain()

#             response = chain.invoke({
#                 "context": docs,
#                 "question": user_question
#             })

#             return response
        
#         except Exception as e:
#             return f"Error answering question: {e}"



# new code

import os
from PyPDF2 import PdfReader
import pdfplumber
import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
import google.generativeai as genai
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
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
        
        # Configure Pinecone
        self.pinecone_api_key = os.getenv('PINECONE_API_KEY')
        if not self.pinecone_api_key:
            raise ValueError("PINECONE_API_KEY not found in environment variables")
            
        self.index_name = os.getenv('PINECONE_INDEX_NAME', 'medpal-index')
    
    def get_pdf_text(self, pdf_files):
        """Extract text from PDF files using multiple methods for better accuracy"""
        all_text = ""
        
        for file_info in pdf_files:
            if file_info['type'] == 'pdf':
                filepath = file_info['filepath']
                filename = file_info['original_name']
                print(f"Processing PDF: {filename}")
                
                # Try multiple extraction methods
                text = self._extract_text_multiple_methods(filepath, filename)
                if text:
                    all_text += f"\n\n--- Document: {filename} ---\n\n{text}\n"
                else:
                    print(f"Warning: Could not extract text from {filename}")
        
        return all_text
    
    def _extract_text_multiple_methods(self, filepath, filename):
        """Try multiple PDF text extraction methods"""
        text = ""
        
        # Method 1: pdfplumber (best for complex PDFs)
        try:
            with pdfplumber.open(filepath) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
            if text.strip():
                print(f"Successfully extracted text using pdfplumber from {filename}")
                return text
        except Exception as e:
            print(f"pdfplumber failed for {filename}: {str(e)}")
        
        # Method 2: PyMuPDF (fitz) - good for most PDFs
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
        except Exception as e:
            print(f"PyMuPDF failed for {filename}: {str(e)}")
        
        # Method 3: PyPDF2 (fallback)
        try:
            pdf_reader = PdfReader(filepath)
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
            if text.strip():
                print(f"Successfully extracted text using PyPDF2 from {filename}")
                return text
        except Exception as e:
            print(f"PyPDF2 failed for {filename}: {str(e)}")
        
        return text
    
    def get_text_chunks(self, text):
        """Split text into chunks for processing"""
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
        chunks = text_splitter.split_text(text)
        return chunks
    
    def get_vector_store(self, text_chunks):
        """Create vector store from text chunks using Hugging Face embeddings and Pinecone"""
        try:
            # Use Hugging Face embeddings (no API quota issues)
            print("Creating vector store with Hugging Face embeddings...")
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            
            print(f"Uploading vectors to Pinecone index: {self.index_name}")
            vector_store = PineconeVectorStore.from_texts(
                texts=text_chunks,
                embedding=embeddings,
                index_name=self.index_name
            )
            print("Vector store created successfully in Pinecone")
            return vector_store
        except Exception as e:
            print(f"Failed to create vector store: {str(e)}")
            # Fallback logic removed as Pinecone is required
            raise e
    
    def get_conversational_chain(self):
        """Create conversational chain for question answering"""
        prompt_template = """
        You are a madical assistant. Read the document and try to figure out the 
        patients problem. Answer the questions based on the uploaded document.
        If you cant answer the question, say I DONT KNOW instead of making up some answer. 
        Make sure you answer like a professional medical assistant. 
        Context:
        {context}

        Question: 
        {question}

        Answer:
        """
        
        model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3)
        prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        chain = load_qa_chain(model, chain_type='stuff', prompt=prompt)
        return chain
    
    def process_pdfs(self, uploaded_files):
        """Process uploaded PDF files and create vector store"""
        pdf_files = [f for f in uploaded_files if f['type'] == 'pdf']
        
        if not pdf_files:
            return "No PDF files found"
        
        print(f"Found {len(pdf_files)} PDF file(s) to process")
        
        try:
            raw_text = self.get_pdf_text(pdf_files)
            print(f"Extracted text length: {len(raw_text)} characters")
            
            if not raw_text.strip():
                return "No text could be extracted from the PDF files. The PDFs might be image-based or corrupted."
            
            # Clean and preprocess text
            cleaned_text = self._clean_text(raw_text)
            print(f"Cleaned text length: {len(cleaned_text)} characters")
            
            if not cleaned_text.strip():
                return "No meaningful text could be extracted from the PDF files."
            
            text_chunks = self.get_text_chunks(cleaned_text)
            print(f"Created {len(text_chunks)} text chunks")
            
            if not text_chunks:
                return "No text chunks could be created from the PDF files."
            
            self.get_vector_store(text_chunks)
            print("Vector store created successfully")
            
            return f"Successfully processed {len(pdf_files)} PDF file(s) with {len(text_chunks)} text chunks"
        
        except Exception as e:
            print(f"Error processing PDFs: {str(e)}")
            return f"Error processing PDFs: {str(e)}"
    
    def _clean_text(self, text):
        """Clean and preprocess extracted text"""
        import re
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page markers and headers
        text = re.sub(r'--- Page \d+ ---', '', text)
        text = re.sub(r'--- Document: .+? ---', '', text)
        
        # Remove common PDF artifacts (fixed regex pattern)
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}\"\'\/\@\#\$\%\&\*\+\=\<\>\~\`\|]', '', text)
        
        # Remove multiple consecutive periods
        text = re.sub(r'\.{3,}', '...', text)
        
        return text.strip()
    
    def answer_question(self, user_question):
        """Answer user questions based on processed PDFs"""
        try:
            try:
                # Use Hugging Face embeddings (no API quota issues)
                print("Loading vector store with Hugging Face embeddings...")
                embeddings = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2",
                    model_kwargs={'device': 'cpu'},
                    encode_kwargs={'normalize_embeddings': True}
                )
                
                vector_store = PineconeVectorStore.from_existing_index(
                    index_name=self.index_name,
                    embedding=embeddings
                )
            except Exception as e:
                print(f"Failed to load vector store: {str(e)}")
                raise e
            
            docs = vector_store.similarity_search(user_question)
            
            chain = self.get_conversational_chain()
            response = chain.invoke({"input_documents": docs, "question": user_question})
            return response["output_text"]
        
        except Exception as e:
            return f"Error answering question: {str(e)}"

import os
import sys
import asyncio
import nest_asyncio
from dotenv import load_dotenv
import streamlit as st
from streamlit_chat import message as st_message

# Собственные классы
from scrap.scrapper import WebScrapper
from rag.summarization import WebSummarizer
from rag.ingest import EmbeddingIngestor
from rag.chatbot import ChatBot

# Настройка политики цикла событий для Windows
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

load_dotenv()
nest_asyncio.apply()

# Путь к файлу истории чата
CHAT_HISTORY_FILE = "history/chat_history.txt"


# Функция для загрузки истории чата из файла
def load_chat_history():
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    return []


# Функция для сохранения истории чата в файл
def save_chat_history(history):
    with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as f:
        for entry in history:
            f.write(f"{entry}\n")


# Переменные сессии
if "url_submitted" not in st.session_state:
    st.session_state.url_submitted = False
if "extraction_done" not in st.session_state:
    st.session_state.extraction_done = False
if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = ""
if "embedding_done" not in st.session_state:
    st.session_state.embedding_done = False
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # Только текущая сессия
if "full_chat_history" not in st.session_state:
    st.session_state.full_chat_history = load_chat_history()  # Вся история из файла
if "summary" not in st.session_state:
    st.session_state.summary = ""
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "deepseek"  # Модель по умолчанию

# ---------------------------
# Конфигурация страницы в Streamlit
# ---------------------------

st.set_page_config(layout="wide", page_title="Web-ChatBot")
st.title("Project Chatbot with LLM + RAG")

# ---------------------------
# Интерфейс Streamlit
# ---------------------------

page = st.sidebar.selectbox("Menu", ["Home", "AI Chatbot"])

if page == "Home":
    st.markdown(
        """
        ## Welcome to Web-Chatbot
        **Web-Chatbot** is a small chatbot empowered by integration of LLM with RAG of website knowledge extraction through LangChain.

        **Functionalities:**
        - **Web Scraping:** Crawl and extract web page content.
        - **Web Summarization:** Generate detailed summaries of the extracted content.
        - **Create Embeddings:** Embeddings with FAISS for vector representation and retrieval of web-scraped information
        - **Chatbot Interface:** Execute Question-Answering task via a conversational agent.

        **Technologies:**
        - **LLM:** Model deepseek-r1, llama3.2, qwen2.5, gemma2
        - **FAISS:** vector database to store embeddings
        - **LangChain:** framework to integrate LLM, external data and tools
        - **Streamlit:** python library to fast prototype web apps

        Get started!
        """
    )

elif page == "AI Chatbot":
    # Выбор модели
    st.session_state.selected_model = st.sidebar.selectbox(
        "Выберите модель:",
        ["deepseek", "llama3.2", "qwen2.5", "gemma2"],
        index=0  # По умолчанию выбрана первая модель
    )

    with st.form("url_form"):
        url_input = st.text_input("Enter a URL to crawl:")
        submit_url = st.form_submit_button("Submit URL")

        if submit_url and url_input:
            st.session_state.url_submitted = True
            st.session_state.extraction_done = False
            st.session_state.embedding_done = False
            st.session_state.chat_history = []  # Очистка текущей сессии
            st.session_state.summary = ""

    if st.session_state.url_submitted:
        col1, col2 = st.columns(2)

        with col1:
            st.header("1. Web-Scrapping")

            if not st.session_state.extraction_done:
                with st.spinner("Extracting website..."):
                    scraper = WebScrapper()
                    extracted = asyncio.run(scraper.crawl(url_input))
                    st.session_state.extracted_text = extracted
                    st.session_state.extraction_done = True
                st.success("Extraction complete!")

            preview = "\n".join([line for line in st.session_state.extracted_text.splitlines() if line.strip()][:5])
            st.text_area("Extracted Text Preview", preview, height=150)

            st.download_button(
                label="Download Extracted Text",
                data=st.session_state.extracted_text,
                file_name="extract_text.txt",
                mime="text/plain",
            )

            st.markdown("---")

            st.header("2. Web-Summarization")

            if st.button("Summarize Web Page", key="summarize_button"):
                with st.spinner("Summarizing..."):
                    summarizer = WebSummarizer(model_name=st.session_state.selected_model)
                    summary, summary_time = summarizer.summarize(st.session_state.extracted_text)
                    st.session_state.summary = summary
                st.success(f"Summarization complete! Time: {summary_time:.2f} seconds")

            if st.session_state.summary:
                st.subheader("Summarized Output")
                st.markdown(st.session_state.summary, unsafe_allow_html=False)

        with col2:
            st.header("3. Create Embeddings")

            if st.session_state.extraction_done and not st.session_state.embedding_done:
                if st.button("Create Embeddings"):
                    with st.spinner("Creating embeddings..."):
                        embeddings = EmbeddingIngestor()
                        st.session_state.vectorstore = embeddings.create_embeddings(st.session_state.extracted_text)
                        st.session_state.embedding_done = True
                    st.success("Vectors are created!")

            elif st.session_state.embedding_done:
                st.info("Embeddings have been created.")

            st.markdown("---")

            st.header("4. ChatBot")

            if st.session_state.embedding_done:
                chatbot = ChatBot(st.session_state.vectorstore, model_name=st.session_state.selected_model)
                user_input = st.text_input("Your Message:", key="chat_input")

                if st.button("Send", key="send_button") and user_input:
                    with st.spinner("Generating response..."):
                        bot_answer, answer_time = chatbot.qa(user_input)  # Получаем ответ и время выполнения
                        # Добавляем вопрос и ответ в текущую сессию
                        new_entry = f"User: {user_input}\nBot: {bot_answer}\nTime: {answer_time:.2f} seconds"
                        st.session_state.chat_history.append(new_entry)
                        # Добавляем в полную историю и сохраняем в файл
                        st.session_state.full_chat_history.append(new_entry)
                        save_chat_history(st.session_state.full_chat_history)
                        st.success(f"Ответ сгенерирован за {answer_time:.2f} секунд!")

                # Отображаем только текущую сессию чата
                if st.session_state.chat_history:
                    st.subheader("Chat History (Current Session)")
                    for entry in st.session_state.chat_history:
                        st.text(entry)
                        st.markdown("---")  # Разделитель между сообщениями
            else:
                st.info("Please create embeddings to activate the chat.")
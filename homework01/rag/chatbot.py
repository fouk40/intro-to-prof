from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
import time


class ChatBot:
    def __init__(self, vector_db, model_name="deepseek"):
        self.db = vector_db
        self.model_name = model_name

        # Инициализация LLM в зависимости от выбранной модели
        if model_name == "deepseek":
            self.llm = ChatOllama(
                model="deepseek-r1:1.5b",
                base_url="http://localhost:11434",
                temperature=0.3
            )
        elif model_name == "llama3.2":
            self.llm = ChatOllama(
                model="llama3.2:latest",
                base_url="http://localhost:11434",
                temperature=0.3
            )
        elif model_name == "qwen2.5":
            self.llm = ChatOllama(
                model="qwen2.5:1.5b",
                temperature=0.3
            )
        elif model_name == "gemma2":
            self.llm = ChatOllama(
                model="gemma2:2b",
                base_url="http://localhost:11434",
                temperature=0.3
            )
        else:
            raise ValueError("Unsupported model name")

        self.prompt_template = """
            You are an AI assistant tasked with answering questions based solely
            on the provided context. Your goal is to generate a comprehensive answer
            for the given question using only the information available in the context.

            context: {context}
            question: {question}

            <response> Your answer in Markdown format. </response>
        """

        self.chain = self.build_chain()

    def build_chain(self):
        prompt = PromptTemplate(template=self.prompt_template,
                                input_variables=["context", "question"])
        retriever = self.db.as_retriever(search_kwargs={"k": 5})

        chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt},
            verbose=True
        )

        return chain

    def qa(self, question):
        """
        Генерирует ответ на вопрос и возвращает ответ и время выполнения.

        :param question: Вопрос пользователя.
        :return: Кортеж (ответ, время выполнения в секундах).
        """
        start_time = time.time()  # Записываем время начала выполнения
        response = self.chain(question)  # Выполняем цепочку RAG
        end_time = time.time()  # Записываем время окончания выполнения
        elapsed_time = end_time - start_time  # Вычисляем разницу
        return response["result"], elapsed_time  # Возвращаем ответ и время выполнения
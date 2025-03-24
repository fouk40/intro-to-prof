from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
import time


class WebSummarizer:
    def __init__(self, model_name="deepseek"):
        self.model_name = model_name

        # Инициализация LLM в зависимости от выбранной модели
        if model_name == "deepseek":
            self.llm = ChatOllama(
                model="deepseek-r1:1.5b",
                base_url="http://localhost:11434",
                temperature=0.3,
                max_tokens=200
            )
        elif model_name == "llama3.2":
            self.llm = ChatOllama(
                model="llama3.2:latest",
                base_url="http://localhost:11434",
                temperature=0.3,
                max_tokens=200
            )
        elif model_name == "qwen2.5":
            self.llm = ChatOllama(
                model="qwen2.5:1.5b",
                temperature=0.3,
                max_tokens=200
            )
        elif model_name == "gemma2":
            self.llm = ChatOllama(
                model="gemma2:2b",
                base_url="http://localhost:11434",
                temperature=0.3,
                max_tokens=200
            )
        else:
            raise ValueError("Unsupported model name")

        self.prompt_template = """
            You are an AI assistant that is tasked with summarizing a web page.
            Your summary should be detailed and cover all key points mentioned in the web page.
            Below is the extracted content of the web page:
            {content}

            Please provide a comprehensive and detailed summary in Markdown format.
        """

    def summarize(self, content):
        """
        Генерирует суммаризацию текста и возвращает результат и время выполнения.

        :param content: Текст для суммаризации.
        :return: Кортеж (суммаризация, время выполнения в секундах).
        """
        start_time = time.time()  # Записываем время начала выполнения

        # Создаем промпт для суммаризации
        summary_prompt = PromptTemplate(template=self.prompt_template, input_variables=["content"])
        prompt_text = summary_prompt.format(content=content)

        # Формируем сообщение для LLM
        messages = [{
            "role": "user",
            "content": prompt_text
        }]

        # Выполняем запрос к LLM
        response = self.llm.invoke(messages)
        summary = response.content  # Получаем результат суммаризации

        end_time = time.time()  # Записываем время окончания выполнения
        elapsed_time = end_time - start_time  # Вычисляем разницу

        return summary, elapsed_time  # Возвращаем суммаризацию и время выполнения